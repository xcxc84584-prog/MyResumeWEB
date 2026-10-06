from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import UserRegister, UserLogin, UserResponse
from backend.security import hash_password, verify_password

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_username = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.post("/login", response_model=UserResponse)
@router.post("/login")
def login(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if user_data.password == "":
        if user.account_mode != "review":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        request.session.clear()
        request.session["user_id"] = user.id
        request.session["account_created_at"] = user.created_at.isoformat()
        request.session["access_mode"] = "review"

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "account_mode": user.account_mode,
            "access_mode": "review",
            "redirect": "/resume"
        }

    if not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    request.session.clear()
    request.session["user_id"] = user.id
    request.session["account_created_at"] = user.created_at.isoformat()
    request.session["access_mode"] = "owner"

    if user.account_mode == "review":
        redirect = "/resume"
    else:
        redirect = "/dashboard"

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "account_mode": user.account_mode,
        "access_mode": "owner",
        "redirect": redirect
    }

@router.get("/me", response_model=UserResponse)
def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user or request.session.get("account_created_at") != user.created_at.isoformat():
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    return user

@router.post("/logout")
def logout(request: Request):
    request.session.clear()

    return {
        "message": "Logged out successfully"
    }

from backend.dependencies.auth import require_owner
from backend.schemas.account import AccountDeletionRequest
from backend.account_deletion import delete_account

@router.delete("/account")
def delete_user_account(data: AccountDeletionRequest, request: Request,
                        db: Session = Depends(get_db)):
    user = require_owner(request, db)
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="密碼錯誤")
    paths = [document.file_path for document in user.documents]
    if user.profile and user.profile.avatar_path:
        paths.append(user.profile.avatar_path)
    pending = delete_account(db, user, paths)
    request.session.clear()
    return {"message": "一般帳號已註銷", "redirect": "/",
            "file_cleanup_pending": pending}
