import base64
import copy
from fastapi import APIRouter, Depends, UploadFile, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import numpy as np
import cv2
from rembg import remove
from starlette import status
from database import get_db
from domain.Clothes import Clothes_schema, Clothes_crud
from domain.user.user_router import get_current_user
from models import User
from fastapi import HTTPException

from learning_model.judgment_of_clothes import analyze_image
from learning_model.discrimination_color import color_extraction


router = APIRouter(
    prefix="/api/Clothes",
)


@router.get("/check")
def Clothes_check(Clothe_category: str = "", 
                Clothe_id: int = -1, 
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

    clothe = Clothes_crud.modify_Clothes(user_id = current_user.username, modify_clothe = clothe, db = db)
    return clothe


@router.post("/create", status_code = status.HTTP_200_OK)
async def Clothes_create(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    category: str = Form(...),
    color: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    contents = await file.read()

    nparr = np.frombuffer(contents, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 배경 제거
    img_no_bg = remove(img_np)
    # 이미지 직렬화 (예시: base64 인코딩)
    _, img_encoded = cv2.imencode('.png', img_no_bg)
    img_data = img_encoded.tobytes()

    if not Clothes_crud.image_doublecheck(db = db, image = img_data, user_id = current_user.username):
        raise HTTPException(status_code = 400, detail = "이미 존재하는 이미지 입니다.")

    clothe_data = {
        "image": img_data,  # 직렬화된 이미지
        "category": category,
        "color": color,
        "user_id": current_user.username if current_user else None,
        "user": current_user
    }

    # Add database saving task to background
    background_tasks.add_task(Clothes_crud.create_Clothes, db, clothe_data)


@router.post("/yolo", status_code = status.HTTP_200_OK)
async def upload_files(file: UploadFile):
    # analyze_image에 사용할 파일을 읽기
    category_copy = copy.deepcopy(file)
    # color_extraction에 사용할 파일을 읽기
    color_copy = copy.deepcopy(file)

    results = await analyze_image(file = category_copy)
    color = color_extraction(file = color_copy)

    return  {"category": results, "color": color}


@router.delete("/delete")
def Clothes_delete(Clothes_id: int,
                current_user: User = Depends(get_current_user), 
                db: Session = Depends(get_db)):
    Clothes_crud.delete_Clothes_data(db = db, user_id = current_user.username, Clothes_id = Clothes_id)


@router.post("/matching", status_code = status.HTTP_200_OK)
async def Clothes_matching(temperature: int, Clothes_id: int = -1, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user.username
    
    if Clothes_id is not -1:
        matching = await Clothes_crud.Clothes_push_by_id( clothes_id = Clothes_id, user_id = user_id, current_temperature = temperature, db = db)
        if matching == 0:
            raise HTTPException(status_code = 400, detail = "선택하신 옷은 현재 온도에 맞지 않습니다.")
    else:
        matching = await Clothes_crud.Clothes_push_by_temperature(user_id = user_id, current_temperature = temperature, db = db)
    
    return matching
