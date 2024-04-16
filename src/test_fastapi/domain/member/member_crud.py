from datetime import datetime

from models import Member, User
from sqlalchemy.orm import Session


def get_member_list(db: Session):
    member_list = db.query(Member)\
        .order_by(Member.create_date.desc())\
        .all()
    return member_list


def get_member(db: Session, member_id: int):
    member = db.query(Member).get(member_id)
    return member


def create_member(db: Session, _image: bytes, user: User):
    db_Member = Member(image = _image,
                           create_date = datetime.now(),
                           user = user)
    db.add(db_Member)
    db.commit()


def check_member_data(db: Session, user_id: int):
    member = db.query(Member).filter(Member.user_id == user_id)
    return member


def delete_member_data(db: Session, user_id: int, member_id: int):
    member = db.query(Member).filter(Member.id == member_id, Member.user_id == user_id).first()

    print(member)
    if member is not None:
        db.delete(member)
        db.commit()
        return True
    else:
        return False


def check_user(db: Session, user: User):
    return db.query(User).filter(User.username == user.username).first()


def modify_user(db: Session, user_modify: User, current_user: User):
    user = db.query(User).filter(
        (User.username == user_modify.username) |
        (User.email == user_modify.email)
    ).first()

    if user:
        return "다시 입력해주세요"
    
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        user.username = user_modify.username
        user.email = user.email
        db.add(user)
        db.commit()
        return user_modify
    else:
        return "error"