import base64
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session


from starlette import status
from database import get_db
from domain.Clothes import Clothes_schema, Clothes_crud
from domain.user.user_router import get_current_user
from domain.user.user_schema import UserModify
from domain.user.user_crud import modify_user, get_user
from models import User


router = APIRouter(
    prefix="/api/Clothes",
)


@router.get("/user_check", response_model = Clothes_schema.User)
def user_check(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user(db = db, user = current_user)
    return user


@router.post("/user_modify")
def user_modify(_modify_user: UserModify, _current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = modify_user(db = db, modify_user = _modify_user, current_user = _current_user)
    return user


@router.get("/list", response_model = list[Clothes_schema.Clothes])
def Clothes_list(db: Session = Depends(get_db)):
    _Clothes_list = Clothes_crud.get_Clothes_list(db)
    return _Clothes_list


@router.get("/detail", response_model = Clothes_schema.Clothes)
def Clothes_detail(Clothes_id: int, db: Session = Depends(get_db)):
    clothe = Clothes_crud.get_Clothes(db, Clothes_id = Clothes_id)
    return clothe


@router.post("/create", status_code = status.HTTP_204_NO_CONTENT)
async def Clothes_create(file: UploadFile,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    contents = await file.read()
    encoded_image = base64.b64encode(contents)

    clothe = Clothes_schema.Clothes
    clothe.Clothes_Image = encoded_image
    clothe.User_Id = current_user.username
    clothe.User = current_user
    Clothes_crud.create_Clothes(db = db, _clothe = clothe)


@router.get("/check",  response_model = list[Clothes_schema.Clothes])
def Clothes_check(Clothes_category: str = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    clothe = Clothes_crud.check_Clothes_data(category = Clothes_category, db = db, user_id = current_user.username)
    return clothe


@router.post("/delete", status_code = status.HTTP_204_NO_CONTENT)
def Clothes_delete(Clothes_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    clothe = Clothes_crud.delete_Clothes_data(db = db, user_id = current_user.id, Clothes_id = Clothes_id)
    if clothe:
        return "성공"
    else:
        return "실패"