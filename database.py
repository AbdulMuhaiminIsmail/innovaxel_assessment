from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

engine = create_engine(
    str(DATABASE_URL), connect_args={"check_same_thread": False}
)

LocalSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    session = LocalSession()
    try:
        yield session 
    finally:
        session.close()