from pydantic import BaseModel, field_validator, EmailStr
from pydantic_core.core_schema import FieldValidationInfo


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


class User(BaseModel):
    id: int
    username: str
    email: str


class UserCreate():
    username: str
    password1: str
    password2: str
    User_NickName: str
    User_Instagram_ID: str
    User_Age: int
    User_Imail: EmailStr
    User_ProfileImage: bytes

    def __init__(self, username: str, password1: str, password2: str, 
                User_NickName: str, User_Instagram_ID: str, User_Age: int, 
                User_Imail: EmailStr, User_ProfileImage: bytes):
        self.username = username
        self.password1 = password1
        self.password2 = password2
        self.User_NickName = User_NickName
        self.User_Instagram_ID = User_Instagram_ID
        self.User_Age = User_Age
        self.User_Imail = User_Imail
        self.User_ProfileImage = User_ProfileImage

    @field_validator('username', 'password1', 'password2')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

    @field_validator('password2')
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password1' in info.data and v != info.data['password1']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v


class UserModify(BaseModel):
    password1: str
    password2: str
    User_NickName: str
    User_Instagram_ID: str
    User_Age: int
    User_Imail: EmailStr

    @field_validator('password2')
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password1' in info.data and v != info.data['password1']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v