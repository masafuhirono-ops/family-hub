from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, Base
from app.models.models import User, Message
from app.api.v1 import auth, chat

# データベースのテーブル作成
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Family Hub API")

# CORS: 本番で CORS_ORIGINS を設定（カンマ区切り）。未設定ならローカル用
_cors_origins = os.getenv("CORS_ORIGINS", "")
if _cors_origins:
    allow_origins = [o.strip() for o in _cors_origins.split(",") if o.strip()]
else:
    allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

_middleware_kw: dict = {
    "allow_origins": allow_origins,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if not _cors_origins:
    _middleware_kw["allow_origin_regex"] = r"https?://(192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+):5173|https://[a-z0-9-]+\.(ngrok-free\.app|ngrok\.io|ngrok-free\.dev)"
app.add_middleware(CORSMiddleware, **_middleware_kw)
# --- ここまで ---

# 認証用ルーターの登録
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

# チャット用ルーターの登録
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Family Hub API"}