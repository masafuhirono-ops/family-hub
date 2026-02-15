import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.oauth2 import id_token
from google.auth.transport import requests

# ローカル: .env が読めない場合のフォールバック（フロントと同じ値）
GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    "558585274838-u6tav0qdsj1ffpa3o59nfaepto210b49.apps.googleusercontent.com",
)
# 本番環境用: 家族のメールをカンマ区切りで指定。未設定なら認証済み全員を許可
WHITELIST_EMAILS_STR = os.getenv("FAMILY_WHITELIST_EMAILS", "")
WHITELIST_EMAILS = [e.strip() for e in WHITELIST_EMAILS_STR.split(",") if e.strip()]

security = HTTPBearer(auto_error=False)


def verify_google_token(token: str) -> dict:
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID が設定されていません",
        )
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスが取得できません",
            )
        if WHITELIST_EMAILS and email not in WHITELIST_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="このアカウントはアクセスできません",
            )
        return idinfo
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ログインが必要です",
        )
    return verify_google_token(credentials.credentials)