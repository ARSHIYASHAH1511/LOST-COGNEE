import os

mistral_key = os.getenv("MISTRAL_API_KEY")

if mistral_key:
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = mistral_key
    if not os.getenv("OPENAI_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = "https://api.mistral.ai/v1"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Get database URL from environment variable, OR use a local sqlite file as a backup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./career_mentor.db")

# Create database engine
# Note: connect_args is needed only for SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()
