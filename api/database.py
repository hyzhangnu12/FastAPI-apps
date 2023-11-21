from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings


SQLALCHEMY_DATABASE_URL = f'{settings.DB_ENGINE}+{settings.DB_DRIVER}://'\
                        + f'{settings.DB_USER}:{settings.DB_PASSWORD}'\
                        + f'@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

# print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
