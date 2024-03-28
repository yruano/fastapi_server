from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key = True)
    image = Column(LargeBinary, nullable = False)
    create_date = Column(DateTime, nullable = False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable = True)
    user = relationship("User", backref = "member_users")


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key = True)
    username = Column(String(50), unique = True, nullable = False)
    password = Column(String(1000), nullable = False)
    email = Column(String(50), unique = True, nullable = False)