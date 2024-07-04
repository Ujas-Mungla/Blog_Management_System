from fastapi import FastAPI, APIRouter
from src.routers.user import user
from src.routers.user import Otp
from src.routers.category import Cate
from src.routers.blog import blogger
app = FastAPI()
app.include_router(user)
app.include_router(Otp)
app.include_router(Cate)
app.include_router(blogger)



