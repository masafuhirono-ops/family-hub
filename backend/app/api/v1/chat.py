from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_serializer
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.models import Message
from app.core.security import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    sender_name: str
    content: str
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")

    class Config:
        from_attributes = True


@router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """メッセージ一覧を取得（要ログイン）"""
    messages = db.query(Message).order_by(Message.created_at.asc()).all()
    return messages


@router.post("/messages", response_model=MessageResponse)
async def create_message(
    body: MessageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """メッセージを送信（要ログイン・送信者名はトークンから取得）"""
    if not body.content.strip():
        raise HTTPException(status_code=400, detail="メッセージを入力してください")

    sender_name = current_user.get("name") or current_user.get("email", "匿名")

    msg = Message(
        sender_name=sender_name,
        content=body.content.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
