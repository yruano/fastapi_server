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


def create_member(db: Session, _image: bytes, user: User, category: str):
    db_Member = Member(image = _image,
                        create_date = datetime.now(),
                        user = user,
                        category = category)
    db.add(db_Member)
    db.commit()


def check_member_data(db: Session, user_id: int):
    member = db.query(Member).filter(Member.user_id == user_id)
    return member


def delete_member_data(db: Session, user_id: int, member_id: int):
    member = db.query(Member).filter(Member.id == member_id, Member.user_id == user_id).first()

    if member is not None:
        db.delete(member)
        db.commit()
        return True
    else:
        return False


def category_check_member(db: Session, user_id: int, category: str):
    member_list = db.query(Member).filter(Member.category == category, Member.user_id == user_id).all()
    return member_list