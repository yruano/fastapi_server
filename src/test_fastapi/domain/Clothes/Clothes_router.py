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
                        Thickness: str = Form(""),
                        color: str = Form(""),
                        count:int = Form(""),
                        current_user: User = Depends(get_current_user), 
                        db: Session = Depends(get_db)):
    
    if file:
        contents = await file.read()
        encoded_image = base64.b64encode(contents)
    else:
        encoded_image = ""

    clothe = Clothes_schema.Clothes
    clothe.Clothes_Category = "윗옷"
    clothe.Clothes_Id = clothe_id
    clothe.Clothes_Image = encoded_image
    clothe.Clothes_Color = color
    clothe.Clothes_Count = count

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


# @router.post("/create", status_code = status.HTTP_204_NO_CONTENT)
# async def Clothes_create(file: UploadFile,
#                         db: Session = Depends(get_db),
#                         current_user: User = Depends(get_current_user)):
#     contents = await file.read()
#     encoded_image = base64.b64encode(contents)
#     color = '#ffb3ba'

#     clothe = Clothes_schema.Clothes
#     clothe.Clothes_Category = "wool_coat"
#     clothe.Clothes_Image = encoded_image
#     clothe.User_Id = current_user.username
#     clothe.User = current_user
#     clothe.Clothes_Color = color
#     Clothes_crud.create_Clothes(db = db, _clothe = clothe)


# YOLO 모델 로드 (가정)
# 학습 시킨 코드가 필요
# 흠 무슨 코드가 필요한거지
# ??? 이거 하려면 데이터셋이 필요하네 ??????????????????????????????????
# https://github.com/Recircle2000/autolookbook_YOLO/blob/master/train_lib/YOLOv8/yoloTrain.ipynb
# 이거는 모델 설정이 잘못 되었던 내가 잘못 쓰던
# 일단 스스로 무언가 학습을 하고 무언가 만들고 있어 이게 맞나?
import cv2
from rembg import remove
from PIL import Image
from ultralytics import YOLO
import extcolors
import numpy as np
from sklearn.cluster import KMeans

async def analyze_image(image_data: bytes):
    # 이미지를 numpy 배열로 변환
    nparr = np.frombuffer(image_data, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 배경 제거
    img_no_bg = remove(img_np)

    # 그레이스케일로 변환
    gray_img = cv2.cvtColor(img_no_bg, cv2.COLOR_BGR2GRAY)
    
    # # 히스토그램 평활화
    # equalized_img = cv2.equalizeHist(gray_img)
    
    # # YOLO 모델 로드
    # model = YOLO("best240506.pt")
    
    # # 결과 저장할 임시 파일 경로 설정
    # temp_output_path = "temp_output.png"
    # cv2.imwrite(temp_output_path, equalized_img)
    
    # # YOLO 모델로 분석
    # results = model(temp_output_path)
    
    # # 분석 결과 플롯 생성
    # plot_img = results[0].plot()
    
    # return plot_img

@router.post("/yolo/")
async def upload_files(file: UploadFile = File(...)):
    contents = await file.read()
    
    # 이미지 분석
    results = await analyze_image(contents)
    
    # 색상 추출
    img = Image.open(file.file)
    colors, pixel_count = extcolors.extract_from_image(img)
    
    pixel_output = 0
    for c in colors:
        pixel_output += c[1]
        print(f'{c[0]} : {round((c[1] / pixel_count) * 100, 2)}% ({c[1]})')
    
    print(f'Pixels in output: {pixel_output} of {pixel_count}')
    
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