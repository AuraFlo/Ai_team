from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use SQLite (lightweight, good for edge devices like Raspberry Pi)
SQLALCHEMY_DATABASE_URL = "sqlite:///./fitness_app.db"

# For SQLite, need check_same_thread=False when using it with multiple threads
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session maker for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()