import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.document import Document
from backend.schemas.document import DocumentResponse
from backend.dependencies.auth import require_owner

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)

UPLOAD_DIR = "storage/uploads/documents"
MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/zip",
    "application/x-zip-compressed"
}

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type"
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File cannot be empty"
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File size exceeds 10 MB"
        )

    extension = os.path.splitext(
        file.filename or ""
    )[1].lower()

    stored_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        stored_filename
    )

    try:
        with open(
            file_path,
            "wb"
        ) as output_file:
            output_file.write(
                content
            )

        document = Document(
            user_id=user.id,
            original_filename=(
                file.filename
                or stored_filename
            ),
            stored_filename=stored_filename,
            file_path=file_path,
            content_type=file.content_type,
            file_size=len(content)
        )

        db.add(
            document
        )
        db.commit()
        db.refresh(
            document
        )

        return document

    except Exception:
        db.rollback()

        if os.path.exists(
            file_path
        ):
            os.remove(
                file_path
            )

        raise

@router.get(
    "",
    response_model=list[DocumentResponse]
)
def get_documents(
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
        request,
        db
    )

    documents = db.query(
        Document
    ).filter(
        Document.user_id == user.id
    ).order_by(
        Document.id.asc()
    ).all()

    return documents

@router.get(
    "/{document_id}",
    response_model=DocumentResponse
)
def get_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
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

    return document

@router.get(
    "/{document_id}/file"
)
def get_document_file(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
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

@router.delete(
    "/{document_id}"
)
def delete_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_owner(
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

    file_path = document.file_path

    db.delete(
        document
    )
    db.commit()

    if os.path.isfile(
        file_path
    ):
        try:
            os.remove(
                file_path
            )
        except OSError:
            pass

    return {
        "message": "Document deleted successfully"
    }