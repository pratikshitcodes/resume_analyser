import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

from sqlalchemy.engine import URL, make_url

def get_db_url_and_credentials():
    # If discrete POSTGRES_PASSWORD is provided or DATABASE_URL is not set
    if settings.POSTGRES_PASSWORD or not settings.DATABASE_URL:
        user = settings.POSTGRES_USER or "postgres"
        password = settings.POSTGRES_PASSWORD
        host = settings.POSTGRES_HOST or "localhost"
        port = settings.POSTGRES_PORT or 5432
        db_name = settings.POSTGRES_DB or "resume_evaluator"
        
        db_url = URL.create(
            drivername="postgresql",
            username=user,
            password=password,
            host=host,
            port=port,
            database=db_name,
        )
        return db_url, user, password, host, port, db_name
    else:
        # Parse DATABASE_URL safely
        try:
            parsed = make_url(settings.DATABASE_URL)
            return (
                parsed, 
                parsed.username or "postgres", 
                parsed.password or "", 
                parsed.host or "localhost", 
                parsed.port or 5432, 
                parsed.database or "resume_evaluator"
            )
        except Exception:
            return settings.DATABASE_URL, "postgres", "", "localhost", 5432, "resume_evaluator"

def create_db_engine(db_url):
    engine_kwargs = {"echo": False}
    url_str = str(db_url)
    
    if url_str.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    elif url_str.startswith("postgresql"):
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20
        engine_kwargs["pool_pre_ping"] = True
    
    return create_engine(db_url, **engine_kwargs)

def get_engine_and_session():
    # Attempt primary database (PostgreSQL)
    db_target, user, password, host, port, db_name = get_db_url_and_credentials()
    try:
        if str(db_target).startswith("postgresql"):
            # Ensure the database exists if on PostgreSQL
            try:
                import psycopg2
                from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
                conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cur = conn.cursor()
                cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
                if not cur.fetchone():
                    cur.execute(f'CREATE DATABASE "{db_name}";')
                    logger.info(f"Database '{db_name}' created successfully in PostgreSQL.")
                cur.close()
                conn.close()
            except Exception as dbe:
                logger.debug(f"PostgreSQL database check/create step note: {dbe}")

        eng = create_db_engine(db_target)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Connected successfully to PostgreSQL database: {db_name} on {host}:{port}")
        return eng, sessionmaker(autocommit=False, autoflush=False, bind=eng)
    except Exception as e:
        logger.warning(f"Could not connect to configured PostgreSQL ({db_name} on {host}:{port}): {e}")
        # If user has a PostgreSQL URL that failed, fall back gracefully to SQLite
        fallback_url = f"sqlite:///{settings.BASE_DIR / 'recruitment_platform.db'}"
        logger.info(f"Using local database fallback: {fallback_url}.")
        eng = create_db_engine(fallback_url)
        return eng, sessionmaker(autocommit=False, autoflush=False, bind=eng)

engine, SessionLocal = get_engine_and_session()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from ..models import (
        User, Resume, ParsedProfile, ATSAnalysis, Job, 
        MatchResult, InterviewQuestionSet, MockInterviewSession, 
        InterviewSlot, ChatSession, ChatMessage
    )
    Base.metadata.create_all(bind=engine)
