import datetime

from pydantic import BaseModel
from domain.user.user_schema import User


class Clothes(BaseModel):
    Clothes_Id: int
    Clothes_Create_Date: datetime.datetime
    Clothes_LastFit_Date: datetime.datetime
    Clothes_Category: str
    Clothes_Image: bytes
    Clothes_Count: int
    Clothes_Score: int
    Clothes_Color: str
    User_Id: str
    User: User