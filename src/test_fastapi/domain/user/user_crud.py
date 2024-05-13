from passlib.context import CryptContext
from sqlalchemy.orm import Session
from pydantic import EmailStr
from domain.user.user_schema import UserCreate, UserModify
from models import User


pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")


def create_user(db: Session, user_create: UserCreate):
    db_user = User(username = user_create.username,
                   password = pwd_context.hash(user_create.password1),
                   User_NickName = user_create.User_NickName,
                   User_Instagram_ID = user_create.User_Instagram_ID,
                   User_Age = user_create.User_Age,
                   User_ProfileImage = user_create.User_ProfileImage,
                )
    db.add(db_user)
    db.commit()
    return user_create.username

def get_existing_user(db: Session, user_create: UserCreate):
    return db.query(User).filter(
        (User.username == user_create.username)
    ).first()


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def modify_user(db: Session, modify_user: UserModify, current_user: User):
    original_user = db.query(User).filter(User.username == current_user.username).first()
    
    if modify_user.User_Imail != "" and modify_user.User_Imail is not None:
        user = db.query(User).filter(User.User_Imail == modify_user.User_Imail).first()
        if user:
            return "이미 존재하는 이메일 입니다\n 다시 입력해 주세요!!!!"
        
    for attr in ['User_Imail', 'User_NickName', 'password1', 'User_Instagram_ID', 'User_Age', 'User_ProfileImage']:
        new_value = getattr(modify_user, attr)
        if new_value != "" and new_value is not None:
            if attr == 'password1':
                new_value = pwd_context.hash(new_value)
            setattr(original_user, attr, new_value)
    
    db.add(original_user)
    db.commit()
    return get_user(db = db, username = current_user.username)