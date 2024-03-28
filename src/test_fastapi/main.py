from fastapi import FastAPI


from domain.user import user_router
from domain.member import member_router


app = FastAPI()


app.include_router(member_router.router)
app.include_router(user_router.router)