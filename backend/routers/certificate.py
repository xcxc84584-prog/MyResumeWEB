from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.certificate import Certificate
from backend.models.document import Document
from backend.schemas.certificate import CertificateCreate, CertificateUpdate, CertificateResponse
from backend.dependencies.auth import require_owner, require_review_or_owner

router = APIRouter(
    prefix="/api/certificates",
    tags=["Certificates"]
)

@router.post(
    "",
    response_model=CertificateResponse,
    status_code=status.HTTP_201_CREATED
)
def create_certificate(
    certificate_data: CertificateCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    certificate = Certificate(
        user_id=user.id,
        **certificate_data.model_dump()
    )

    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    return certificate

@router.get(
    "",
    response_model=list[CertificateResponse]
)
def get_certificates(
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_review_or_owner(
        request,
        db
    )

    certificates = db.query(Certificate).filter(
        Certificate.user_id == user.id
    ).order_by(
        Certificate.id.asc()
    ).all()

    return certificates

@router.get(
    "/{certificate_id}",
    response_model=CertificateResponse
)
def get_certificate(
    certificate_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_review_or_owner(
        request,
        db
    )

    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )

    return certificate

@router.put(
    "/{certificate_id}",
    response_model=CertificateResponse
)
def update_certificate(
    certificate_id: int,
    certificate_data: CertificateUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )

    update_data = certificate_data.model_dump(
        exclude_unset=True
    )

    final_issue_date = update_data.get(
        "issue_date",
        certificate.issue_date
    )

    final_expiration_date = update_data.get(
        "expiration_date",
        certificate.expiration_date
    )

    if (
        final_issue_date is not None
        and final_expiration_date is not None
        and final_expiration_date < final_issue_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expiration_date cannot be earlier than issue_date"
        )

    for field, value in update_data.items():
        setattr(
            certificate,
            field,
            value
        )

    db.commit()
    db.refresh(certificate)

    return certificate

@router.delete(
    "/{certificate_id}"
)
def delete_certificate(
    certificate_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )

    db.delete(certificate)
    db.commit()

    return {
        "message": "Certificate deleted successfully"
    }

@router.post(
    "/{certificate_id}/documents/{document_id}"
)
def link_document_to_certificate(
    certificate_id: int,
    document_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    certificate = db.query(
        Certificate
    ).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
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

    if document in certificate.documents:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document already linked to certificate"
        )

    certificate.documents.append(
        document
    )

    db.commit()

    return {
        "message": "Document linked to certificate successfully",
        "certificate_id": certificate.id,
        "document_id": document.id
    }

@router.delete(
    "/{certificate_id}/documents/{document_id}"
)
def unlink_document_from_certificate(
    certificate_id: int,
    document_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    certificate = db.query(
        Certificate
    ).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
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

    if document not in certificate.documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document is not linked to certificate"
        )

    certificate.documents.remove(
        document
    )

    db.commit()

    return {
        "message": "Document unlinked from certificate successfully",
        "certificate_id": certificate.id,
        "document_id": document.id
    }