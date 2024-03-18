from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from starlette import status
from database import get_db
from domain.member import member_schema, member_crud
from domain.user.user_router import get_current_user
from test_fastapi.models import User


router = APIRouter(
    prefix="/api/member",
)


@router.get("/list", response_model = list[member_schema.Member])
def member_list(db: Session = Depends(get_db)):
    _member_list = member_crud.get_member_list(db)
    return _member_list


@router.get("/detail/{member_id}", response_model = member_schema.Member)
def member_detail(member_id: int, db: Session = Depends(get_db)):
    member = member_crud.get_member(db, member_id = member_id)
    return member


@router.post("/create", status_code = status.HTTP_204_NO_CONTENT)
def member_create(_member_create: member_schema.MemberCreate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    member_crud.create_member(db = db, member_create = _member_create, user = current_user)