import base64
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session


from starlette import status
from database import get_db
from domain.member import member_schema, member_crud
from domain.user.user_router import get_current_user
from models import User


router = APIRouter(
    prefix="/api/member",
)


@router.get("/list", response_model = list[member_schema.Member])
def member_list(db: Session = Depends(get_db)):
    _member_list = member_crud.get_member_list(db)
    return _member_list


@router.get("/detail", response_model = member_schema.Member)
def member_detail(member_id: int, db: Session = Depends(get_db)):
    member = member_crud.get_member(db, member_id = member_id)
    return member


@router.post("/create", status_code = status.HTTP_204_NO_CONTENT)
async def member_create(file: UploadFile,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    contents = await file.read()
    encoded_image = base64.b64encode(contents)
    member_crud.create_member(db = db, _image = encoded_image, user = current_user)
    return {"file_size": file.filename}


@router.post("/check",  response_model = list[member_schema.Member])
def member_check(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = member_crud.check_member_data(db, user_id = current_user.id)
    return member


@router.post("/delete", status_code = status.HTTP_204_NO_CONTENT)
def member_delete(member_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = member_crud.delete_member_data(db = db, user_id = current_user.id, member_id = member_id)
    if member:
        return "성공"
    else:
        return "실패"