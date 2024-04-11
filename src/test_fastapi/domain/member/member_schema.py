import datetime

from pydantic import BaseModel
from domain.user.user_schema import User


class Member(BaseModel):
    id: int
    image: bytes
    create_date: datetime.datetime
    user: User | None


class User(BaseModel):
    username: str
    email: str