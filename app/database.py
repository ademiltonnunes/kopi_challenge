from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration from individual environment variables
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "kopi_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "kopi_pass@")
POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME", "kopi_challenge_db")

# Construct DATABASE_URL from individual variables
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}"

# Create SQLAlchemy engine with TCP connection
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "host": POSTGRES_SERVER,
        "port": POSTGRES_PORT,
        "user": POSTGRES_USERNAME,
        "password": POSTGRES_PASSWORD
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 