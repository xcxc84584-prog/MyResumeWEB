import logging
from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException


def delete_account(db, account, file_paths=()):
    root = Path("storage/uploads").resolve()
    staged = []
    try:
        for value in set(file_paths):
            source = Path(value).resolve()
            if not source.is_relative_to(root):
                raise ValueError("Upload path is outside storage")
            if source.is_file():
                target = source.with_name(source.name + ".delete-" + uuid4().hex)
                source.rename(target)
                staged.append((source, target))
        db.delete(account)
        db.commit()
    except Exception:
        db.rollback()
        for source, target in reversed(staged):
            target.rename(source)
        logging.exception("Account deletion failed")
        raise HTTPException(status_code=500, detail="註銷失敗，請稍後再試")
    pending = False
    for source, target in staged:
        try:
            target.unlink()
        except OSError:
            pending = True
            logging.exception("Could not remove deleted account upload: %s", target)
    return pending
