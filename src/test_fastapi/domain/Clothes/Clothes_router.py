import base64
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import EmailStr

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


@router.get("/user_check")
def user_check(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user(db = db, username = current_user.username)
    return user

# 이거도 바꿔야한다 문제가 있네
# 회원가입과 비슷한 형식으로 하는게 좋겠군
# 그리고 클래스 함수를 사요아는 방식으로 하는게 좋을거 같은데 이부분을 더 생각해 봐야겠군
# 이거 fastapi랑 py클래스 좀 확인해서 처리를 다시 해야 겠다 이거 되면 회원가입도 바꾸고 그러면 좀 더 나은 값들이 나오겠지
@router.post("/user_modify")
async def user_modify(
                    password1: str = "",
                    password2: str = "",
                    User_NickName: str = "",
                    User_Instagram_ID: str = "",
                    User_Age: int = 0,
                    User_Imail: EmailStr = "",
                    file: UploadFile = File(None),
                    _current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if file:
        contents = await file.read()
        User_ProfileImage = base64.b64encode(contents)
    else:
        User_ProfileImage = None

    _user_modify = UserModify(
        password1 = password1,
        password2 = password2,
        User_NickName = User_NickName,
        User_Instagram_ID = User_Instagram_ID,
        User_Age = User_Age,
        User_Imail = User_Imail,
        User_ProfileImage = User_ProfileImage,
    )
    
    user = modify_user(db = db, modify_user = _user_modify, current_user = _current_user)
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
    clothe.Clothes_Category = None
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