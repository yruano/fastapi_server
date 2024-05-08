from fastapi import FastAPI


from domain.user import user_router
from domain.Clothes import Clothes_router


app = FastAPI()


app.include_router(Clothes_router.router)
app.include_router(user_router.router)