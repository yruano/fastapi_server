from datetime import datetime

from domain.member.member_schema import MemberCreate
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


def create_member(db: Session, member_create: MemberCreate, user: User):
    db_Member = Member(subject = member_create.subject,
                           content = member_create.content,
                           create_date = datetime.now(),
                           user = user)
    db.add(db_Member)
    db.commit()