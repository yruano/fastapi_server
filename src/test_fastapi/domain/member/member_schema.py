import datetime

from pydantic import BaseModel, field_validator
from domain.user.user_schema import User


class Member(BaseModel):
    id: int
    image: bytes
    create_date: datetime.datetime
    user: User | None


class MemberCreate(BaseModel):
    image: bytes

    @field_validator('image')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v