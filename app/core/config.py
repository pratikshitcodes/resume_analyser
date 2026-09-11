import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current and parent directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")
load_dotenv(BASE_DIR.parent.parent / ".env")

class Settings:
    BASE_DIR: Path = BASE_DIR
    PROJECT_NAME: str = "AI Recruitment & Interview Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Secret Key & JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ai-recruitment-super-secret-jwt-key-change-in-prod-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # PostgreSQL discrete configuration (supports passwords with '@', '#', '%', etc.)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "resume_evaluator")

    # Database URL: Primary is PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # AI Providers
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "groq") # groq | openai | gemini | mock
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "openai/gpt-oss-120b")
    
    # Upload Storage
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
