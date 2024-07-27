from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


class User(BaseModel):
    username: EmailStr
    password: str
    User_NickName: str
    User_Instagram_ID: str
    User_Age: int
    User_ProfileImage: bytes


class UserCreate():
    username: EmailStr
    password1: str
    password2: str
    User_NickName: str
    User_Instagram_ID: str
    User_Age: int
    User_ProfileImage: bytes

    def __init__(self, username: str, password1: str, password2: str, 
                User_NickName: str, User_Instagram_ID: str, User_Age: int,
                User_ProfileImage: bytes):
        self.username = self.not_empty(username)
        self.password1 = self.not_empty(password1)
        self.password2 = self.passwords_match(password2)
        self.User_NickName = self.not_empty(User_NickName)
        self.User_Instagram_ID = User_Instagram_ID
        self.User_Age = User_Age
        self.User_ProfileImage = User_ProfileImage

    def not_empty(self, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

    def passwords_match(self, v):
        if self.password1 != v:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v


class UserModify():
    password1: str
    password2: str
    User_NickName: str
    User_Instagram_ID: str
    User_Age: int
    User_ProfileImage: bytes

    def __init__(self, password1: str, password2: str, User_NickName: str, 
                User_Instagram_ID: str, User_Age: int,
                User_ProfileImage: bytes):
        self.password1 = password1
        self.password2 = self.passwords_match(password2)
        self.User_NickName = User_NickName
        self.User_Instagram_ID = User_Instagram_ID
        self.User_Age = User_Age
        self.User_ProfileImage = User_ProfileImage

    def passwords_match(self, v):
        if self.password1 != v:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v
