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


class UserCreate(BaseModel):
    nickname: str
    username: str
    password1: str
    password2: str
    instagram: str
    email: EmailStr


    @field_validator('username', 'password1', 'password2', 'email')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v


    @field_validator('password2')
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password1' in info.data and v != info.data['password1']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v

# 일반 password는 바꿀건지 아닌지 먼저 확인을하고 바꾸면 열리는 방식으로 하는게 좋을거 같군
# 값들이 빈칸을 체크하고 빈값은 None으로 표시하든 아니면 다른 방식으로 값을 보네는 방법을 생가해야함
# class UserModify(BaseModel):
#     nickname: str
#     username: str
#     password_change: bool
#     password1: str
#     password2: str
#     instagram: str
#     email: EmailStr

#     @field_validator('password2')
#     def passwords_match(cls, v, info: FieldValidationInfo):
#         if 'password1' in info.data and v != info.data['password1']:
#             raise ValueError('비밀번호가 일치하지 않습니다')
#         return v