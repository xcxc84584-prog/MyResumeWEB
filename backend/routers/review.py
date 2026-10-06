from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.review import (
    ReviewEnterRequest,
    ReviewExitRequest
)
from backend.security import verify_password
from backend.dependencies.auth import (
    get_session_user,
    require_owner
)

router = APIRouter(
    prefix="/api/review",
    tags=["Review"]
)

@router.get("/status")
def get_review_status(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_session_user(
        request,
        db
    )

    return {
        "account_mode": user.account_mode,
        "access_mode": request.session.get(
            "access_mode"
        )
    }

@router.post("/enter")
def enter_review_mode(
    data: ReviewEnterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    user.account_mode = "review"

    request.session[
        "access_mode"
    ] = "owner"

    db.commit()
    db.refresh(
        user
    )

    return {
        "message": "Review mode enabled successfully",
        "account_mode": user.account_mode,
        "access_mode": request.session.get(
            "access_mode"
        ),
        "redirect": "/resume"
    }

@router.post("/exit")
def exit_review_mode(
    data: ReviewExitRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    user.account_mode = "edit"

    request.session[
        "access_mode"
    ] = "owner"

    db.commit()
    db.refresh(
        user
    )

    return {
        "message": "Review mode disabled successfully",
        "account_mode": user.account_mode,
        "access_mode": "owner",
        "redirect": "/dashboard"
    }