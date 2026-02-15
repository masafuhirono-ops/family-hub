from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

import os

import re
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
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

# S3 静的サイトのオリジンを正規表現でも許可（ホスト名の微妙な差に対応）
_origin_regex = r"https?://cursor-depoly\.s3-website(-[a-z0-9-]+)?\.amazonaws\.com"
_s3_origin_pattern = re.compile(_origin_regex)


class OptionsCORSMiddleware(BaseHTTPMiddleware):
    """OPTIONS プリフライトを確実に 200 で返す（App Runner 等で 400 になる対策）"""

    async def dispatch(self, request, call_next):
        if request.method != "OPTIONS":
            return await call_next(request)
        origin = request.headers.get("origin", "")
        if not origin and request.headers.get("Origin"):
            origin = request.headers.get("Origin")
        allow_origin = origin if (_s3_origin_pattern.match(origin) or origin in allow_origins) else allow_origins[0] if allow_origins else "*"
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": allow_origin,
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "86400",
            },
        )


app.add_middleware(OptionsCORSMiddleware)
_middleware_kw: dict = {
    "allow_origins": allow_origins,
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    "allow_headers": ["*"],
    "allow_origin_regex": _origin_regex,
}
if not _cors_origins:
    _middleware_kw["allow_origin_regex"] = r"https?://(192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+):5173|https://[a-z0-9-]+\.(ngrok-free\.app|ngrok\.io|ngrok-free\.dev)"
app.add_middleware(CORSMiddleware, **_middleware_kw)
# --- ここまで ---

# 認証用ルーターの登録
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

# チャット用ルーターの登録
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """500 の原因をログに出す"""
    tb = traceback.format_exc()
    print(f"Unhandled exception: {exc}\n{tb}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
def read_root():
    return {"message": "Welcome to Family Hub API"}