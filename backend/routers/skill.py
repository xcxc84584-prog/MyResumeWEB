from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.skill import Skill
from backend.models.document import Document
from backend.schemas.skill import SkillCreate, SkillUpdate, SkillResponse
from backend.dependencies.auth import require_owner, require_review_or_owner

router = APIRouter(
    prefix="/api/skills",
    tags=["Skills"]
)

@router.post(
    "",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED
)
def create_skill(
    skill_data: SkillCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    skill = Skill(
        user_id=user.id,
        **skill_data.model_dump()
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    return skill

@router.get(
    "",
    response_model=list[SkillResponse]
)
def get_skills(
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_review_or_owner(
        request,
        db
    )

    skills = db.query(Skill).filter(
        Skill.user_id == user.id
    ).order_by(
        Skill.id.asc()
    ).all()

    return skills

@router.get(
    "/{skill_id}",
    response_model=SkillResponse
)
def get_skill(
    skill_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_review_or_owner(
        request,
        db
    )

    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.user_id == user.id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    return skill

@router.put(
    "/{skill_id}",
    response_model=SkillResponse
)
def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.user_id == user.id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    update_data = skill_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            skill,
            field,
            value
        )

    db.commit()
    db.refresh(skill)

    return skill

@router.delete(
    "/{skill_id}"
)
def delete_skill(
    skill_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.user_id == user.id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    db.delete(skill)
    db.commit()

    return {
        "message": "Skill deleted successfully"
    }

@router.post(
    "/{skill_id}/documents/{document_id}"
)
def link_document_to_skill(
    skill_id: int,
    document_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    skill = db.query(
        Skill
    ).filter(
        Skill.id == skill_id,
        Skill.user_id == user.id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
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

    if document in skill.documents:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document already linked to skill"
        )

    skill.documents.append(
        document
    )

    db.commit()

    return {
        "message": "Document linked to skill successfully",
        "skill_id": skill.id,
        "document_id": document.id
    }

@router.delete(
    "/{skill_id}/documents/{document_id}"
)
def unlink_document_from_skill(
    skill_id: int,
    document_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    skill = db.query(
        Skill
    ).filter(
        Skill.id == skill_id,
        Skill.user_id == user.id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
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

    if document not in skill.documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document is not linked to skill"
        )

    skill.documents.remove(
        document
    )

    db.commit()

    return {
        "message": "Document unlinked from skill successfully",
        "skill_id": skill.id,
        "document_id": document.id
    }