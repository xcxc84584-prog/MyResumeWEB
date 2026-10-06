import json
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.dependencies.auth import require_owner
from backend.models.profile import Profile
from backend.models.skill import Skill
from backend.models.certificate import Certificate
from backend.models.reviewer_account import ReviewerAccount
from backend.models.resume_submission import ResumeSubmission
from backend.schemas.submission import ResumeSubmissionCreate

router = APIRouter(
    prefix="/api/submissions",
    tags=["submissions"]
)

STATUS_TEXT = {
    "unread": "未讀",
    "backup": "備選",
    "accepted": "正取",
    "rejected": "落選"
}

def build_resume_snapshot(
    user,
    db: Session
):
    from backend.routers.resume import build_resume
    return json.dumps(build_resume(user, db), ensure_ascii=False, default=str)

@router.post("")
def submit_resume(
    data: ResumeSubmissionCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    reviewer = (
        db.query(ReviewerAccount)
        .filter(
            ReviewerAccount.id
            == data.reviewer_account_id
        )
        .first()
    )

    if reviewer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer account not found"
        )

    existing = (
        db.query(ResumeSubmission)
        .filter(
            ResumeSubmission.applicant_user_id
            == user.id,
            ResumeSubmission.reviewer_account_id
            == reviewer.id
        )
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resume already submitted"
        )

    snapshot = build_resume_snapshot(
        user,
        db
    )

    submission = ResumeSubmission(
        applicant_user_id=user.id,
        reviewer_account_id=reviewer.id,
        status="unread",
        resume_snapshot=snapshot
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return {
        "id": submission.id,
        "reviewer_account_id": reviewer.id,
        "company_name": reviewer.company_name,
        "description": reviewer.description,
        "status": submission.status,
        "status_text": STATUS_TEXT[
            submission.status
        ],
        "submitted_at": submission.submitted_at
    }

@router.get("/mine")
def get_my_submissions(
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    submissions = (
        db.query(ResumeSubmission)
        .filter(
            ResumeSubmission.applicant_user_id
            == user.id
        )
        .order_by(
            ResumeSubmission.submitted_at.desc()
        )
        .all()
    )

    result = []

    for submission in submissions:
        reviewer = submission.reviewer_account

        result.append({
            "id": submission.id,
            "reviewer_account_id":
                submission.reviewer_account_id,
            "company_name":
                reviewer.company_name,
            "description":
                reviewer.description,
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

@router.delete("/{submission_id}")
def withdraw_submission(
    submission_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    submission = (
        db.query(ResumeSubmission)
        .filter(
            ResumeSubmission.id
            == submission_id,
            ResumeSubmission.applicant_user_id
            == user.id
        )
        .first()
    )

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    db.delete(submission)
    db.commit()

    return {
        "message": "Resume withdrawn successfully"
    }