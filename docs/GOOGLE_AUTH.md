# Google Auth 実装の概要

## フロー

1. **フロントエンド**: `@react-oauth/google` の `GoogleLogin` でユーザーがログイン
2. ログイン成功後、**Google ID トークン**（JWT）を取得
3. チャット API 呼び出し時に **Authorization: Bearer &lt;トークン&gt;** で送信
4. **バックエンド**: `google.oauth2.id_token.verify_oauth2_token()` でトークン検証
5. 検証済みの `email` / `name` を使って送信者を記録

## 実装箇所

| 場所 | 内容 |
|------|------|
| `frontend/src/App.tsx` | GoogleOAuthProvider, GoogleLogin, ログイン後に idToken を state で保持 |
| `frontend/src/Chat.tsx` | 全 API リクエストに `Authorization: Bearer ${idToken}` を付与 |
| `backend/app/core/security.py` | `verify_google_token()`, `get_current_user()`（Depends） |
| `backend/app/api/v1/chat.py` | GET/POST に `Depends(get_current_user)` で認証必須 |

## 環境変数

- **フロント**: `VITE_GOOGLE_CLIENT_ID`（Google Cloud Console の OAuth クライアント ID）
- **バックエンド**: `GOOGLE_CLIENT_ID`（同じ値）
- **本番オプション**: `FAMILY_WHITELIST_EMAILS`（カンマ区切り）で許可メールを制限可能

## Google Cloud Console

- **認可された JavaScript 生成元** に本番 URL（例: CloudFront の URL）を追加すること。
