from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import relationship


# 테이블 데이터 좀 더 생각해봐야함
from database import Base

# last_use = Column(DateTime, nullable = True)
# use_count = Column(Integer, nullable = True)
# color = Column(String(50), nullable = True)


class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key = True)
    image = Column(LONGBLOB, nullable = False)
    category = Column(String(50), nullable = True)
    create_date = Column(DateTime, nullable = False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable = True)
    user = relationship("User", backref = "member_users")


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key = True)
    nickname = Column(String(50), unique = True, nullable = False)
    username = Column(String(50), unique = True, nullable = False)
    password = Column(String(1000), nullable = False)
    instagram = Column(String(50), unique = True, nullable = True)
    email = Column(String(50), unique = True, nullable = False)