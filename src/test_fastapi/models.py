from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import relationship

from database import Base


class Clothes(Base):
    __tablename__ = "Clothes"

    Clothes_Id = Column(Integer, primary_key = True)
    Clothes_Create_Date = Column(DateTime, nullable = False)
    Clothes_LastFit_Date = Column(DateTime, nullable = False)
    Clothes_Category = Column(String(50), nullable = True)
    Clothes_Image = Column(LONGBLOB, nullable = False)
    Clothes_Count = Column(Integer, nullable = True)
    Clothes_Score = Column(Integer, nullable = True)
    Clothes_Color = Column(String(7), nullable = True)
    Clothes_Tone = Column(String(20), nullable = True)
    # Clothes_ThermalInsulation = Column(Integer, nullable = True)
    # Clothes_Thickness = Column(String(20), nullable = True)
    User_Id = Column(String(50), ForeignKey("User.username"), nullable = True)
    User = relationship("User", backref = "Clothe_Users")


class User(Base):
    __tablename__ = "User"

    username = Column(String(50), primary_key = True, unique = True, nullable = False)
    password = Column(String(1000), nullable = False)
    User_NickName = Column(String(20), unique = True, nullable = False)
    User_Instagram_ID = Column(String(50), nullable = True)
    User_Age = Column(Integer, nullable = True)
    User_ProfileImage = Column(LONGBLOB, nullable = True)