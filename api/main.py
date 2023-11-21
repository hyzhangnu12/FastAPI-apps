from fastapi import FastAPI
from .routers import user, item

# from . import models
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user.router)
app.include_router(item.router)