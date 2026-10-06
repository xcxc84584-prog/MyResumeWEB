import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.profile import Profile
from backend.models.skill import Skill
from backend.models.certificate import Certificate
from backend.models.document import Document
from backend.dependencies.auth import require_review_or_owner

router = APIRouter(
    prefix="/api/resume",
    tags=["Resume"]
)

def calculate_age(birth_date):
    if birth_date is None:
        return None

    from datetime import date

    today = date.today()

    return (
        today.year
        - birth_date.year
        - (
            (today.month, today.day)
            < (birth_date.month, birth_date.day)
        )
    )

def document_response(document: Document) -> dict:
    return {
        "id": document.id,
        "original_filename": document.original_filename,
        "content_type": document.content_type,
        "file_size": document.file_size
    }

@router.get("")
def get_resume(
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_review_or_owner(
        request,
        db
    )

    return build_resume(user, db)


def build_resume(user, db: Session):
    profile = db.query(
        Profile
    ).filter(
        Profile.user_id == user.id
    ).first()

    skills = db.query(
        Skill
    ).filter(
        Skill.user_id == user.id
    ).order_by(
        Skill.id.asc()
    ).all()

    certificates = db.query(
        Certificate
    ).filter(
        Certificate.user_id == user.id
    ).order_by(
        Certificate.id.asc()
    ).all()

    profile_data = None

    if profile:
        profile_data = {
            "full_name": profile.full_name,
            "gender": profile.gender,
            "birth_date": profile.birth_date,
            "age": calculate_age(
                profile.birth_date
            ),
            "phone": profile.phone,
            "education_level": profile.education_level,
            "avatar_path": (
                "/"
                + profile.avatar_path.replace(
                    "storage/",
                    "",
                    1
                )
                if profile.avatar_path
                else None
            )
        }

    skill_data = []

    for skill in skills:
        skill_data.append({
            "id": skill.id,
            "skill_name": skill.skill_name,
            "learning_duration": skill.learning_duration,
            "proficiency_level": skill.proficiency_level,
            "documents": [
                document_response(document)
                for document in skill.documents
            ]
        })

    certificate_data = []

    for certificate in certificates:
        certificate_data.append({
            "id": certificate.id,
            "certificate_name": certificate.certificate_name,
            "issuer": certificate.issuer,
            "issue_date": certificate.issue_date,
            "expiration_date": certificate.expiration_date,
            "certificate_number": certificate.certificate_number,
            "documents": [
                document_response(document)
                for document in certificate.documents
            ]
        })

    return {
        "username": user.username,
        "profile": profile_data,
        "skills": skill_data,
        "certificates": certificate_data
    }

@router.get(
    "/documents/{document_id}/file"
)
def get_resume_document_file(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_review_or_owner(
        request,
        db
    )

    document = db.query(
        Document
    ).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    is_linked_to_skill = any(
        skill.user_id == user.id
        for skill in document.skills
    )

    is_linked_to_certificate = any(
        certificate.user_id == user.id
        for certificate in document.certificates
    )

    if (
        not is_linked_to_skill
        and not is_linked_to_certificate
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document is not available in resume"
        )

    if not os.path.isfile(
        document.file_path
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found"
        )

    return FileResponse(
        path=document.file_path,
        media_type=document.content_type,
        filename=document.original_filename,
        content_disposition_type="inline"
    )