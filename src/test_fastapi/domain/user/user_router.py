import base64
from pydantic import EmailStr
from datetime import timedelta, datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
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

# 그냥 UploadFile을 사용하여 멀티폼과 그냥 톰을 동시에 사용하면
# 멀치 폼에서는 file의 크기가 크다 보니 여러번에 걸쳐 값을 받아온다
# 하지만 그냥 폼은 그렇지 않다보니 422가 발생한다

@router.post("/create", status_code = status.HTTP_204_NO_CONTENT)
async def user_create(
                    username: EmailStr = Form(...),
                    password1: str = Form(...),
                    password2: str = Form(...),
                    User_NickName: str = Form(...),
                    User_Instagram_ID: str = Form(""),
                    User_Age: int = Form(0),
                    file: UploadFile = File(None),
                    db: Session = Depends(get_db)
                ):
    encoded_image = b""

    if file:
        contents = await file.read()
        encoded_image = base64.b64encode(contents)

    _user_create = user_schema.UserCreate(
        username = username,
        password1 = password1,
        password2 = password2,
        User_NickName = User_NickName,
        User_Instagram_ID = User_Instagram_ID,
        User_Age = User_Age,
        User_ProfileImage = encoded_image,
    )

    user = user_crud.duplication_user(db, user_create = _user_create)
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
    except JWTError:
        raise credentials_exception
    else:
        user = user_crud.get_user(db, username = username)
        if user is None:
            raise credentials_exception
        return user


@router.get("/check")
def user_check(current_user: user_schema.User = Depends(get_current_user), 
            db: Session = Depends(get_db)):
    user = user_crud.get_user(db = db, username = current_user.username)
    return user


@router.post("/modify")
async def user_modify(
                    password1: str = Form(""),
                    password2: str = Form(""),
                    User_NickName: str = Form(""),
                    User_Instagram_ID: str = Form(""),
                    User_Age: int = Form(0),
                    file: UploadFile = File(None),
                    db: Session = Depends(get_db),
                    _current_user: user_schema.User = Depends(get_current_user)
                    ):
    encoded_image = b""

    if file:
        contents = await file.read()
        encoded_image = base64.b64encode(contents)

    _user_modify = user_schema.UserModify(
        password1 = password1,
        password2 = password2,
        User_NickName = User_NickName,
        User_Instagram_ID = User_Instagram_ID,
        User_Age = User_Age,
        User_ProfileImage = encoded_image,
    )

    user = user_crud.modify_user(db = db, modify_user = _user_modify, current_user = _current_user)
    return user
