import base64
from pydantic import EmailStr
from datetime import timedelta, datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.user import user_crud, user_schema
from domain.user.user_crud import pwd_context


ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "4ab2fce7a6bd79e1c014396315ed322dd6edb1c5d975c6b74a2904135172c03c"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/api/user/login")


router = APIRouter(
    prefix = "/api/user",
)

# 문제는 file: Optional[UploadFile] = File(None)이라는 선언이 FastAPI의 요청 본문에 있는 
# 다른 필드(user_create, db)와 충돌할 수 있다는 것입니다. 
# FastAPI는 요청 본문의 각 필드를 개별적으로 해석하려고 시도하기 때문에, 
# UploadFile과 다른 필드가 함께 있으면 FastAPI가 어떤 필드가 파일을 나타내는지 혼동할 수 있습니다.

@router.post("/create", status_code = status.HTTP_204_NO_CONTENT)
async def user_create(
                    username: str,
                    password1: str,
                    password2: str,
                    User_NickName: str,
                    User_Instagram_ID: str = None,
                    User_Age: int = None,
                    User_Imail: EmailStr = None,
                    file: UploadFile = File(None),
                    db: Session = Depends(get_db)
                ):
    if file:
        contents = await file.read()
        User_ProfileImage = base64.b64encode(contents)
    else:
        User_ProfileImage = None

    _user_create = user_schema.UserCreate(
        username = username,
        password1 = password1,
        password2 = password2,
        User_NickName = User_NickName,
        User_Instagram_ID = User_Instagram_ID,
        User_Age = User_Age,
        User_Imail = User_Imail,
        User_ProfileImage = User_ProfileImage,
    )

    user = user_crud.get_existing_user(db, user_create = _user_create)
    if user:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT,
                            detail="이미 존재하는 사용자입니다.")
    user_crud.create_user(db = db, user_create = _user_create)


@router.post("/login", response_model = user_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):

    # check user and password
    user = user_crud.get_user(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password",
            headers = {"WWW-Authenticate": "Bearer"},
        )


    # make access token
    data = {
        "sub": user.username,
        "exp": datetime.now() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm = ALGORITHM)


    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = user_crud.get_user(db, username = username)
        if user is None:
            raise credentials_exception
        return user