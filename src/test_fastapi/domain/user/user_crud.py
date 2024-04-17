from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate
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


def check_user(db: Session, user: User):
    return db.query(User).filter(User.username == user.username).first()


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# 이거 class를 하나 만들던 해야 할거 같군 이대로는 스파게티다 흠
# 클래스가 해야할거 값을 받는다 일단 비밀번호가 들어오면 확인해서 채크한다
# 클래스에서 교체할 정보들을 걸러서 주면 좋을거 같은데 이방식으로 하면 좋을듯
def modify_user(db: Session, modify_user: UserCreate, current_user: User):
    # original_user = db.query(User).filter(User.id == current_user.id).first()
    
    # if modify_user.username is not None or modify_user.email is not None:
    #     user = get_existing_user(db, user_create = modify_user)
    #     if user:
    #         return print("이미 존재하는 이메일 또는 아이디 입니다\n 다시 입력해 주세요!!!!")
        
    #     if modify_user.username is not None:
    #         original_user.username = modify_user.username
    #     if modify_user.email is not None:
    #         original_user.email = user.email

    # if modify_user.nickname is not None:
    #     original_user.nickname = modify_user.nickname
    
    # if modify_user.password1 is not None:
    #     original_user.password = pwd_context.hash(modify_user.password1)
    
    # if modify_user.instagram is not None:
    #     original_user.instagram = modify_user.instagram
    
    # db.add(original_user)
    # db.commit()
    return modify_user
