from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
# ...他のインポート

# ここが超重要です！これが無いとエラーになります
router = APIRouter()

class TokenBody(BaseModel):
    id_token: str

@router.post("/google")
async def google_auth(body: TokenBody):
    # 認証処理の中身
    # ...
    return {"message": "success", "user": {"name": "博野雅文"}} # 仮のレスポンス