import os
import uuid
from datetime import date
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.profile import Profile
from backend.schemas.profile import ProfileCreate, ProfileUpdate
from backend.dependencies.auth import require_owner, require_review_or_owner

router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"]
)

AVATAR_DIRECTORY = "storage/uploads/avatars"
MAX_AVATAR_SIZE = 5 * 1024 * 1024

ALLOWED_AVATAR_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp"
}

def calculate_age(
    birth_date: date | None
) -> int | None:
    if birth_date is None:
        return None

    today = date.today()

    return (
        today.year
        - birth_date.year
        - (
            (today.month, today.day)
            < (birth_date.month, birth_date.day)
        )
    )

def profile_response(
    profile: Profile
) -> dict:
    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "gender": profile.gender,
        "marital_status": profile.marital_status,
        "birth_date": profile.birth_date,
        "age": calculate_age(
            profile.birth_date
        ),
        "height_cm": profile.height_cm,
        "weight_kg": profile.weight_kg,
        "blood_type": profile.blood_type,
        "phone": profile.phone,
        "address": profile.address,
        "education_level": profile.education_level,
        "medical_history": profile.medical_history,
        "avatar_path": (
            "/"
            + profile.avatar_path.replace(
                "storage/",
                "",
                1
            )
            if profile.avatar_path
            else None
        ),
        "created_at": profile.created_at,
        "updated_at": profile.updated_at
    }

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_profile(
    profile_data: ProfileCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    existing_profile = db.query(
        Profile
    ).filter(
        Profile.user_id == user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists"
        )

    profile = Profile(
        user_id=user.id,
        **profile_data.model_dump()
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile_response(
        profile
    )

@router.get("")
def get_profile(
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_review_or_owner(
        request,
        db
    )

    profile = db.query(
        Profile
    ).filter(
        Profile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return profile_response(
        profile
    )

@router.put("")
def update_profile(
    profile_data: ProfileUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    profile = db.query(
        Profile
    ).filter(
        Profile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            profile,
            field,
            value
        )

    db.commit()
    db.refresh(profile)

    return profile_response(
        profile
    )

@router.delete("")
def delete_profile(
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    profile = db.query(
        Profile
    ).filter(
        Profile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    db.delete(profile)
    db.commit()

    return {
        "message":
            "Profile deleted successfully"
    }

@router.post("/avatar")
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    profile = db.query(
        Profile
    ).filter(
        Profile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG and WebP images are allowed"
        )

    content = await file.read()

    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Avatar file is too large"
        )

    extension = ALLOWED_AVATAR_TYPES[
        file.content_type
    ]

    filename = (
        f"user_{user.id}_"
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    os.makedirs(
        AVATAR_DIRECTORY,
        exist_ok=True
    )

    file_path = os.path.join(
        AVATAR_DIRECTORY,
        filename
    )

    old_avatar_path = profile.avatar_path

    with open(
        file_path,
        "wb"
    ) as avatar_file:
        avatar_file.write(
            content
        )

    profile.avatar_path = file_path.replace(
        "\\",
        "/"
    )

    db.commit()
    db.refresh(profile)

    if (
        old_avatar_path
        and os.path.isfile(
            old_avatar_path
        )
    ):
        try:
            os.remove(
                old_avatar_path
            )
        except OSError:
            pass

    return {
        "message":
            "Avatar uploaded successfully",
        "avatar_path":
            "/"
            + profile.avatar_path.replace(
                "storage/",
                "",
                1
            )
    }