# Family Hub セキュア AWS デプロイガイド

不正アクセスを防ぎ、本番運用できる構成です。

## セキュリティ対策（実装済み）

| 対策 | 内容 |
|------|------|
| **API 認証** | 全チャット API に Google トークン検証を必須化 |
| **送信者名の信頼** | クライアント送信を廃止し、トークンから取得した値のみ使用 |
| **メールホワイトリスト** | 本番では家族のメールのみ許可（オプション） |
| **環境変数** | シークレットをコードに含めず .env で管理 |

---

## 推奨 AWS 構成

```
[ユーザー] 
    ↓ HTTPS
[CloudFront] ← ACM証明書（無料）
    ↓
[S3] 静的ファイル（React）
    +
[API Gateway] → [Lambda] FastAPI
                    ↓
                [RDS PostgreSQL] または [DynamoDB]
```

### 各コンポーネント

| サービス | 役割 |
|----------|------|
| **CloudFront** | HTTPS 配信、DDoS 軽減 |
| **S3** | フロントエンドの静的ファイル |
| **API Gateway** | REST API のエンドポイント、スロットリング |
| **Lambda** | バックエンド API（Mangum で FastAPI 実行） |
| **RDS / DynamoDB** | メッセージ永続化 |

---

## デプロイ手順概要

### 1. 環境変数・シークレット

- **AWS Secrets Manager** または **Systems Manager Parameter Store** に保存
- `GOOGLE_CLIENT_ID`, `FAMILY_WHITELIST_EMAILS`, DB 接続情報など

### 2. Google Cloud Console

- 本番ドメインを **認可された JavaScript 生成元** に追加
  - 例: `https://your-app.cloudfront.net`

### 3. CORS

- `main.py` の `allow_origins` に本番ドメインのみ指定
- 正規表現は本番では使わず、許可するオリジンを列挙

### 4. データベース

- SQLite は本番非推奨（同時書き込みに弱い）
- **RDS PostgreSQL** または **DynamoDB** へ移行

### 5. レート制限

- API Gateway のスロットリングを有効化
- 必要に応じて Lambda 側でもレート制限を実装

---

## ローカル開発時の設定

```powershell
# backend/.env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
# 開発時は空でOK（認証済み全員許可）
# FAMILY_WHITELIST_EMAILS=

# frontend/.env
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

---

## 本番時の追加推奨

1. **WAF** - 不正アクセス・悪意あるリクエストのブロック
2. **VPC** - Lambda と RDS をプライベートサブネットに配置
3. **CloudWatch** - アクセスログ・エラーログの監視
4. **バックアップ** - RDS の自動バックアップを有効化
