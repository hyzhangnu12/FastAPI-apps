from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DB_ENGINE = "postgresql"
DB_DRIVER = "psycopg"
POSTGRES_USER = "dbuser"
POSTGRES_PASSWORD = "ewq123"
HOST = "localhost"
PORT = "5432"
DBNAME = "dbuser" #"fastapi"
SQLALCHEMY_DATABASE_URL = f'{DB_ENGINE}+{DB_DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOST}:{PORT}/{DBNAME}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
