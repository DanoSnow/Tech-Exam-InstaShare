from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Response
from typing import List
import usersdb as db
from auth import current_user
from schemas import User


router = APIRouter(tags=["Files"])


@router.get("/files/hello")
async def files():
    return {"message": "hello files"}


# Upload files (current user)
@router.post("/files/upload")
async def upload(files: List[UploadFile] = File(...),
                 user: User = Depends(current_user)):
    db.add_files(files, user)
    return {"files_count": len(files)}


# Get files (current user)
@router.get("/users/me/files")
async def get_files(user: User = Depends(current_user)):
    return db.get_files(user)


# Get all files
@router.get("/files")
async def get_all_files():
    return db.get_all_files()


# Get all zipfiles
@router.get("/zipfiles")
async def get_all_zipfiles():
    return db.get_all_zipfiles()


@router.get("/users/me/files/download/{id}")
async def download(id: int, user: User = Depends(current_user)):
    try:
        file = db.get_zipfile(id, user)
        headers = {"Content-Disposition": f'attachment; filename={file[0]}'}
        return Response(content=file[1], media_type="application/zip",
                        headers=headers)
    except FileNotFoundError:
        raise HTTPException(detail="File not found", status_code=404)


@router.patch("/users/me/files/modify/{id}", status_code=200)
async def modify_filename(id: int, new_filename: str,
                          user: User = Depends(current_user)):
    try:
        db.modify_filename(id, new_filename, user)
    except FileNotFoundError:
        raise HTTPException(detail="File not found", status_code=404)
    return {"message": "filename successfully modified"}