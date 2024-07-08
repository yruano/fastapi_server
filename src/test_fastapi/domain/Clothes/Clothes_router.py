import base64
from pydantic import EmailStr
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from starlette import status
from database import get_db
from domain.Clothes import Clothes_schema, Clothes_crud
from domain.user.user_router import get_current_user
from models import User

from learning_model.judgment_of_clothes import analyze_image
from learning_model.discrimination_color import color_extraction
from learning_model.cody import predict_category


router = APIRouter(
    prefix="/api/Clothes",
)


@router.get("/check")
def Clothes_check(Clothe_category: str = None, 
                Clothe_id: int = None, 
                current_user: User = Depends(get_current_user), 
                db: Session = Depends(get_db)):
    clothe = Clothes_crud.check_Clothes_data(category = Clothe_category, clothe_id = Clothe_id, db = db, user_id = current_user.username)
    return clothe


@router.post("/modify")
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


@router.post("/create", status_code = status.HTTP_204_NO_CONTENT)
async def Clothes_create(file: UploadFile,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    clothe = Clothes_schema.Clothes

    if file is not None:
        clothe.Clothes_Category = await analyze_image(file = file)
        clothe.Clothes_Color = color_extraction(file = file)
        contents = await file.read()
        encoded_image = base64.b64encode(contents)
    else:
        return "사진이 없습니다."

    clothe.Clothes_Image = encoded_image
    clothe.User_Id = current_user.username
    clothe.User = current_user
    
    Clothes_crud.create_Clothes(db = db, _clothe = clothe)
    return clothe.Clothes_Color


@router.post("/yolo/")
async def upload_files(file: UploadFile = File(...)):
    # 이미지 분석
    results = await analyze_image(file = file)
    print(color_extraction(file = file))
    print(await predict_category(category = results))
    
    return results


@router.delete("/delete")
def Clothes_delete(Clothes_id: int, 
                current_user: User = Depends(get_current_user), 
                db: Session = Depends(get_db)):
    clothe = Clothes_crud.delete_Clothes_data(db = db, user_id = current_user.username, Clothes_id = Clothes_id)


@router.post("/matching", status_code = status.HTTP_204_NO_CONTENT)
async def Clothes_matching(temperature: int, Clothes_id: int = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if Clothes_id is not None:
        matching = Clothes_crud.Clothes_push(clothe_id = Clothes_id, user_id = current_user.username, current_temperature = temperature, db = db)
    else:
        matching = Clothes_crud.Clothes_push(user_id = current_user.username, current_temperature = temperature, db = db)
    return matching