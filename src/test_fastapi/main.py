from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


from domain.user import user_router
# from domain.member import member_router


app = FastAPI()


# app.include_router(member_router.router)
# app.include_router(user_router.router)