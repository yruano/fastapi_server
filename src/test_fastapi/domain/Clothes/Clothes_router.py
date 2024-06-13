import base64
from pydantic import EmailStr
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from starlette import status
from database import get_db
from domain.Clothes import Clothes_schema, Clothes_crud
from domain.user.user_router import get_current_user
from domain.user.user_schema import UserModify
from domain.user.user_crud import modify_user, get_user
from models import User

from learning_model.judgment_of_clothes import analyze_image, color_extraction


router = APIRouter(
    prefix="/api/Clothes",
)


@router.get("/clothes_check")
def Clothes_check(Clothe_category: str = None, 
                Clothe_id: int = None, 
                current_user: User = Depends(get_current_user), 
                db: Session = Depends(get_db)):
    clothe = Clothes_crud.check_Clothes_data(category = Clothe_category, clothe_id = Clothe_id, db = db, user_id = current_user.username)
    return clothe


@router.post("/clothes_modify")
async def Clothe_modify(clothe_id: int,
                        file: Optional[UploadFile] = Form(""),
                        count:int = Form(""),
                        current_user: User = Depends(get_current_user), 
                        db: Session = Depends(get_db)):
    
    if file:
        contents = await file.read()
        encoded_image = base64.b64encode(contents)
    else:
        encoded_image = ""

    clothe = Clothes_schema.Clothes
    clothe.Clothes_Category = await analyze_image(file = file)
    clothe.Clothes_Image = encoded_image
    clothe.Clothes_Count = count
    clothe.Clothes_Id = clothe_id
    clothe.Clothes_Color = color_extraction(file = file)

    clothe = Clothes_crud.modify_Clothes(user_id = User.username, modify_clothe = clothe, db = db)
    return clothe


@router.get("/user_check")
def user_check(current_user: User = Depends(get_current_user), 
            db: Session = Depends(get_db)):
    user = get_user(db = db, username = current_user.username)
    return user


@router.post("/user_modify")
async def user_modify(
                    password1: str = Form(""),
                    password2: str = Form(""),
                    User_NickName: str = Form(""),
                    User_Instagram_ID: Optional[str] = Form(""),
                    User_Age: Optional[int] = Form(0),
                    file: Optional[UploadFile] = File(None),
                    db: Session = Depends(get_db),
                    _current_user: User = Depends(get_current_user)
                    ):
    if file:
        contents = await file.read()
        encoded_image = base64.b64encode(contents)
    else:
        encoded_image = ""

    _user_modify = UserModify(
        password1 = password1,
        password2 = password2,
        User_NickName = User_NickName,
        User_Instagram_ID = User_Instagram_ID,
        User_Age = User_Age,
        User_ProfileImage = encoded_image,
    )

    user = modify_user(db = db, modify_user = _user_modify, current_user = _current_user)
    return user


@router.post("/create", status_code = status.HTTP_204_NO_CONTENT)
async def Clothes_create(file: UploadFile,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    contents = await file.read()
    encoded_image = base64.b64encode(contents)

    clothe = Clothes_schema.Clothes
    clothe.Clothes_Category = await analyze_image(file = file)
    clothe.Clothes_Image = encoded_image
    clothe.User_Id = current_user.username
    clothe.User = current_user
    clothe.Clothes_Color = color_extraction(file = file)
    
    Clothes_crud.create_Clothes(db = db, _clothe = clothe)


@router.post("/yolo/")
async def upload_files(file: UploadFile = File(...)):
    # 이미지 분석
    results = await analyze_image(file = file)
    color_extraction(file = file)
    
    return results


@router.post("/delete")
def Clothes_delete(Clothes_id: int, 
                current_user: User = Depends(get_current_user), 
                db: Session = Depends(get_db)):
    clothe = Clothes_crud.delete_Clothes_data(db = db, user_id = current_user.username, Clothes_id = Clothes_id)


@router.post("/matching", status_code = status.HTTP_204_NO_CONTENT)
async def Clothes_delete(color: str = Form(""), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = await Clothes_crud.predict_color(color = color)
    sss = Clothes_crud.Clothes_push(clothe_id = 0, user_id = current_user.username, current_temperature = 20, db = db)
    return result