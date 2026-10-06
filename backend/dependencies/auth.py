from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session
from backend.models.user import User

def get_session_user(
    request: Request,
    db: Session
) -> User:
    user_id = request.session.get(
        "user_id"
    )

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user = db.query(
        User
    ).filter(
        User.id == user_id
    ).first()

    if user is None or request.session.get("account_created_at") != user.created_at.isoformat():
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    return user

def require_owner(
    request: Request,
    db: Session
) -> User:
    user = get_session_user(
        request,
        db
    )

    access_mode = request.session.get(
        "access_mode"
    )

    if access_mode != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required"
        )

    return user

def require_review_or_owner(
    request: Request,
    db: Session
) -> User:
    user = get_session_user(
        request,
        db
    )

    access_mode = request.session.get(
        "access_mode"
    )

    if access_mode not in {
        "owner",
        "review"
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return user

def get_page_access_mode(
    request: Request
) -> str | None:
    user_id = request.session.get(
        "user_id"
    )

    access_mode = request.session.get(
        "access_mode"
    )

    if user_id is None:
        return None

    if access_mode not in {
        "owner",
        "review"
    }:
        return None

    return access_mode