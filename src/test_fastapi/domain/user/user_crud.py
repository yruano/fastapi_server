from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate, UserModify
from models import User


pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")


def create_user(db: Session, user_create: UserCreate):
    db_user = User(username = user_create.username,
                   nickname = user_create.nickname,
                   password = pwd_context.hash(user_create.password1),
                   instagram = user_create.instagram,
                   email = user_create.email)
    db.add(db_user)
    db.commit()


def get_existing_user(db: Session, user_create: UserCreate):
    return db.query(User).filter(
        (User.username == user_create.username) |
        (User.email == user_create.email)
    ).first()


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def modify_user(db: Session, modify_user: UserModify, current_user: User):
    original_user = db.query(User).filter(User.id == current_user.id).first()
    
    if modify_user.email is not None:
        user = db.query(User).filter((User.id != current_user.id) & (User.email == modify_user.email)).first()
        if user:
            return "이미 존재하는 이메일 또는 아이디 입니다\n 다시 입력해 주세요!!!!"
        
    for attr in ['email', 'nickname', 'password1', 'instagram']:
        new_value = getattr(modify_user, attr)
        if new_value != "":
            if attr == 'password1':
                new_value = pwd_context.hash(new_value)
            setattr(original_user, attr, new_value)
    
    db.add(original_user)
    db.commit()
    return get_user(db = db, user = current_user)