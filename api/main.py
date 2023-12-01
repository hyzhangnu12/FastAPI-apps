from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import user, item, vote

# from . import models
# models.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:3000",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(item.router)
app.include_router(vote.router)

@app.get("/")
async def index():
    return {"message": "Welcome to our place!"}