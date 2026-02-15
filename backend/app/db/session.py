from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 本番: DATABASE_URL（例: postgresql://user:pass@host:5432/dbname）
# ローカル: 未設定なら SQLite
# AWS RDS は postgres:// を返す場合があるので postgresql:// に統一
_raw = os.getenv("DATABASE_URL", "sqlite:///./test.db")
DATABASE_URL = _raw.replace("postgres://", "postgresql://", 1) if _raw.startswith("postgres://") else _raw

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()