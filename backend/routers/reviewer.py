from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.database import get_db
from backend.models.reviewer_account import ReviewerAccount
from backend.schemas.reviewer import (
    ReviewerRegisterRequest,
    ReviewerLoginRequest
)
from backend.security import (
    hash_password,
    verify_password
)
from backend.models.resume_submission import ResumeSubmission
import json
from sqlalchemy import case
from backend.schemas.reviewer_submission import ReviewerSubmissionStatusUpdate


router = APIRouter(
    prefix="/api/reviewer",
    tags=["Reviewer"]
)

@router.post("/register")
def register_reviewer(
    data: ReviewerRegisterRequest,
    db: Session = Depends(get_db)
):
    company_name = data.company_name.strip()
    description = data.description.strip()

    if not company_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name cannot be empty"
        )

    if not description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description cannot be empty"
        )

    existing = db.query(
        ReviewerAccount
    ).filter(
        ReviewerAccount.company_name == company_name,
        ReviewerAccount.description == description
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company name and description already exist"
        )

    reviewer = ReviewerAccount(
        company_name=company_name,
        description=description,
        password_hash=hash_password(
            data.password
        )
    )

    db.add(
        reviewer
    )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company name and description already exist"
        )

    db.refresh(
        reviewer
    )

    return {
        "message":
            "Reviewer account registered successfully",
        "reviewer": {
            "id": reviewer.id,
            "company_name":
                reviewer.company_name,
            "description":
                reviewer.description
        }
    }

@router.post("/login")
def login_reviewer(
    data: ReviewerLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    company_name = data.company_name.strip()
    description = data.description.strip()

    reviewer = db.query(
        ReviewerAccount
    ).filter(
        ReviewerAccount.company_name == company_name,
        ReviewerAccount.description == description
    ).first()

    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid reviewer credentials"
        )

    if not verify_password(
        data.password,
        reviewer.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid reviewer credentials"
        )

    request.session.clear()

    request.session[
        "reviewer_id"
    ] = reviewer.id
    request.session["account_created_at"] = reviewer.created_at.isoformat()

    request.session[
        "access_mode"
    ] = "company_reviewer"

    return {
        "message":
            "Reviewer login successful",
        "reviewer": {
            "id": reviewer.id,
            "company_name":
                reviewer.company_name,
            "description":
                reviewer.description
        },
        "access_mode":
            "company_reviewer",
        "redirect":
            "/reviewer/dashboard"
    }

@router.get("/me")
def get_current_reviewer(
    request: Request,
    db: Session = Depends(get_db)
):
    reviewer_id = request.session.get(
        "reviewer_id"
    )

    access_mode = request.session.get(
        "access_mode"
    )

    if (
        reviewer_id is None
        or access_mode != "company_reviewer"
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Reviewer not authenticated"
        )

    reviewer = db.query(
        ReviewerAccount
    ).filter(
        ReviewerAccount.id == reviewer_id
    ).first()

    if not reviewer or request.session.get("account_created_at") != reviewer.created_at.isoformat():
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Reviewer not authenticated"
        )

    return {
        "id": reviewer.id,
        "company_name":
            reviewer.company_name,
        "description":
            reviewer.description
    }

@router.post("/logout")
def logout_reviewer(
    request: Request
):
    request.session.clear()

    return {
        "message":
            "Reviewer logout successful",
        "redirect":
            "/"
    }
@router.get("/search")
def search_reviewer_accounts(
    company_name: str = "",
    description: str = "",
    db: Session = Depends(get_db)
):
    company_name = company_name.strip()
    description = description.strip()

    query = db.query(ReviewerAccount)

    if company_name:
        query = query.filter(
            ReviewerAccount.company_name.ilike(
                f"%{company_name}%"
            )
        )

    if description:
        query = query.filter(
            ReviewerAccount.description.ilike(
                f"%{description}%"
            )
        )

    reviewers = query.order_by(
        ReviewerAccount.company_name.asc(),
        ReviewerAccount.description.asc()
    ).limit(3).all()

    return [
        {
            "id": reviewer.id,
            "company_name": reviewer.company_name,
            "description": reviewer.description
        }
        for reviewer in reviewers
    ]

STATUS_TEXT = {
    "unread": "未讀",
    "backup": "備選",
    "accepted": "正取",
    "rejected": "落選"
}

def require_reviewer(
    request: Request,
    db: Session
):
    reviewer_id = request.session.get(
        "reviewer_id"
    )

    access_mode = request.session.get(
        "access_mode"
    )

    if (
        reviewer_id is None
        or access_mode != "company_reviewer"
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Reviewer authentication required"
        )

    reviewer = (
        db.query(ReviewerAccount)
        .filter(
            ReviewerAccount.id == reviewer_id
        )
        .first()
    )

    if reviewer is None or request.session.get("account_created_at") != reviewer.created_at.isoformat():
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Reviewer authentication required"
        )

    return reviewer

@router.get("/submissions")
def get_reviewer_submissions(
    request: Request,
    db: Session = Depends(get_db)
):
    reviewer = require_reviewer(
        request,
        db
    )

    status_order = case(
        (ResumeSubmission.status == "unread", 1),
        (ResumeSubmission.status == "backup", 2),
        (ResumeSubmission.status == "accepted", 3),
        (ResumeSubmission.status == "rejected", 4),
        else_=5
    )

    submissions = (
        db.query(ResumeSubmission)
        .filter(
            ResumeSubmission.reviewer_account_id
            == reviewer.id
        )
        .order_by(
            status_order.asc(),
            ResumeSubmission.submitted_at.desc()
        )
        .all()
    )

    result = []

    for index, submission in enumerate(
        submissions,
        start=1
    ):
        result.append({
            "sequence": index,
            "id": submission.id,
            "applicant_user_id":
                submission.applicant_user_id,
            "username":
                submission.applicant.username,
            "status":
                submission.status,
            "status_text":
                STATUS_TEXT.get(
                    submission.status,
                    submission.status
                ),
            "submitted_at":
                submission.submitted_at
        })

    return result
@router.get("/submissions/{submission_id}")
def get_reviewer_submission(
    submission_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    reviewer = require_reviewer(
        request,
        db
    )

    submission = (
        db.query(ResumeSubmission)
        .filter(
            ResumeSubmission.id == submission_id,
            ResumeSubmission.reviewer_account_id == reviewer.id
        )
        .first()
    )

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    try:
        snapshot = json.loads(
            submission.resume_snapshot
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid resume snapshot"
        )

    legacy_snapshot = any("documents" not in item for group in ("skills", "certificates")
                          for item in snapshot.get(group, []))
    snapshot = normalize_snapshot(snapshot, submission.id)
    return {
        "legacy_snapshot": legacy_snapshot,
        "id": submission.id,
        "sequence": submission.id,
        "status": submission.status,
        "status_text": STATUS_TEXT.get(
            submission.status,
            submission.status
        ),
        "submitted_at": submission.submitted_at,
        "resume": snapshot
    }
@router.patch("/submissions/{submission_id}/status")
def update_submission_status(
    submission_id: int,
    data: ReviewerSubmissionStatusUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    reviewer = require_reviewer(
        request,
        db
    )

    submission = (
        db.query(ResumeSubmission)
        .filter(
            ResumeSubmission.id == submission_id,
            ResumeSubmission.reviewer_account_id == reviewer.id
        )
        .first()
    )

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    submission.status = data.status

    db.commit()
    db.refresh(submission)

    return {
        "id": submission.id,
        "status": submission.status,
        "status_text": STATUS_TEXT.get(
            submission.status,
            submission.status
        )
    }

from backend.schemas.account import AccountDeletionRequest
from backend.account_deletion import delete_account

@router.delete("/account")
def delete_reviewer_account(data: AccountDeletionRequest, request: Request,
                            db: Session = Depends(get_db)):
    reviewer = require_reviewer(request, db)
    if not verify_password(data.password, reviewer.password_hash):
        raise HTTPException(status_code=401, detail="密碼錯誤")
    delete_account(db, reviewer)
    request.session.clear()
    return {"message": "批閱帳號已註銷", "redirect": "/"}


from pathlib import Path
from datetime import date
from fastapi.responses import FileResponse
from backend.models.document import Document
from backend.routers.resume import calculate_age

def normalize_snapshot(snapshot, submission_id):
    profile = snapshot.get("profile")
    if profile:
        fields = ("full_name", "gender", "birth_date", "age", "phone", "education_level", "avatar_path")
        profile = {key: profile.get(key) for key in fields}
        avatar = profile.get("avatar_path")
        if avatar:
            profile["avatar_path"] = "/uploads/avatars/" + str(avatar).replace("\\", "/").split("/")[-1]
        if profile.get("age") is None and profile.get("birth_date"):
            try:
                profile["age"] = calculate_age(date.fromisoformat(profile["birth_date"]))
            except ValueError:
                pass
    result = {"username": snapshot.get("username"), "profile": profile}
    fields = {"skills": ("id", "skill_name", "learning_duration", "proficiency_level"),
              "certificates": ("id", "certificate_name", "issuer", "issue_date", "expiration_date", "certificate_number")}
    for group, keys in fields.items():
        result[group] = []
        for source in snapshot.get(group, []):
            item = {key: source.get(key) for key in keys}
            item["documents"] = [{**document, "file_url":
                f"/api/reviewer/submissions/{submission_id}/documents/{document['id']}/file"}
                for document in source.get("documents", [])]
            result[group].append(item)
    return result

@router.get("/submissions/{submission_id}/documents/{document_id}/file")
def get_submission_document(submission_id: int, document_id: int, request: Request,
                            db: Session = Depends(get_db)):
    reviewer = require_reviewer(request, db)
    submission = db.query(ResumeSubmission).filter_by(id=submission_id, reviewer_account_id=reviewer.id).first()
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    snapshot = json.loads(submission.resume_snapshot)
    allowed = {document["id"] for group in ("skills", "certificates")
               for item in snapshot.get(group, []) for document in item.get("documents", [])}
    if document_id not in allowed:
        raise HTTPException(status_code=404, detail="Document not found")
    document = db.query(Document).filter_by(id=document_id, user_id=submission.applicant_user_id).first()
    if document is None or not Path(document.file_path).is_file():
        raise HTTPException(status_code=404, detail="Document no longer available")
    return FileResponse(document.file_path, media_type=document.content_type,
                        filename=document.original_filename, content_disposition_type="inline")
