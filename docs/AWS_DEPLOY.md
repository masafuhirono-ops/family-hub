# Family Hub AWS デプロイ手順

## 構成

| 役割 | AWS サービス | 概要 |
|------|--------------|------|
| フロントエンド | S3 + CloudFront | React 静的サイト、HTTPS |
| バックエンド API | App Runner | FastAPI コンテナ |
| データベース | RDS PostgreSQL | メッセージ永続化 |

---

## 前提条件

- AWS アカウント
- AWS CLI のインストールと設定（`aws configure`）
- Docker のインストール（ローカルビルド用）

---

## Step 1: RDS PostgreSQL を作成

1. **RDS コンソール** → 「データベースの作成」
2. エンジン: **PostgreSQL**
3. テンプレート: **無料利用枠**（または開発用）
4. 設定:
   - DB 識別子: `family-hub-db`
   - マスターパスワード: 強力なパスワードを設定
   - パブリックアクセス: **あり**（App Runner から接続のため）
5. 「作成」をクリック
6. 作成後、**エンドポイント**と**ポート**をメモ

接続文字列の例:
```
postgresql://postgres:あなたのパスワード@family-hub-db.xxxxx.ap-northeast-1.rds.amazonaws.com:5432/postgres
```

**セキュリティグループ**: インバウンドでポート 5432 を開く（App Runner 用 VPC からアクセス可能に）

---

## Step 2: ECR に Docker イメージをプッシュ

```powershell
# 1. ECR リポジトリ作成
aws ecr create-repository --repository-name family-hub-api

# 2. ログイン
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com
# （123456789012 はあなたの AWS アカウント ID）

# 3. ビルド＆プッシュ
cd family-hub/backend
docker build -t family-hub-api .
docker tag family-hub-api:latest 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/family-hub-api:latest
docker push 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/family-hub-api:latest
```

---

## Step 3: App Runner で API をデプロイ

1. **App Runner コンソール** → 「サービス作成」
2. ソース: **コンテナレジストリ** → **Amazon ECR**
3. 先ほどプッシュしたイメージを選択
4. サービス名: `family-hub-api`
5. ポート: `8000`
6. **環境変数**を追加:

| 名前 | 値 |
|------|-----|
| DATABASE_URL | postgresql://postgres:パスワード@ホスト:5432/postgres |
| GOOGLE_CLIENT_ID | あなたの Google クライアント ID |
| CORS_ORIGINS | https://あなたのドメイン |

7. 「作成」をクリック
8. 作成後、**サービス URL**（例: `https://xxxxx.ap-northeast-1.awsapprunner.com`）をメモ

---

## Step 4: フロントエンドを S3 + CloudFront にデプロイ

### 4-1. ビルド

```powershell
cd family-hub/frontend
$env:VITE_API_URL = "https://xxxxx.ap-northeast-1.awsapprunner.com"
$env:VITE_GOOGLE_CLIENT_ID = "あなたのGoogleクライアントID"
npm run build
```

### 4-2. S3 バケット作成

```powershell
aws s3 mb s3://family-hub-frontend-あなたのID --region ap-northeast-1
aws s3 sync dist/ s3://family-hub-frontend-あなたのID --delete
```

### 4-3. CloudFront ディストリビューション作成

1. **CloudFront コンソール** → 「ディストリビューション作成」
2. オリジン: S3 バケットを選択
3. ビューワープロトコルポリシー: **Redirect HTTP to HTTPS**
4. 代替ドメイン名（CNAME）: 使う場合は設定
5. 「作成」をクリック
6. **ドメイン名**（例: `d1234abcd.cloudfront.net`）をメモ

---

## Step 5: Google Cloud Console の設定

1. **認可された JavaScript 生成元** に追加:
   - `https://d1234abcd.cloudfront.net`（あなたの CloudFront ドメイン）
2. **保存**

---

## Step 6: CORS_ORIGINS を更新

App Runner の環境変数 `CORS_ORIGINS` に、CloudFront の URL を設定:
```
https://d1234abcd.cloudfront.net
```

App Runner コンソール → サービス → 設定 → 編集で更新。

---

## 環境変数一覧

### バックエンド（App Runner）

| 変数名 | 説明 |
|--------|------|
| DATABASE_URL | PostgreSQL 接続文字列 |
| GOOGLE_CLIENT_ID | Google OAuth クライアント ID |
| CORS_ORIGINS | フロントの URL（カンマ区切り可） |
| FAMILY_WHITELIST_EMAILS | 本番用: 許可するメール（カンマ区切り、任意） |

### フロントエンド（ビルド時）

| 変数名 | 説明 |
|--------|------|
| VITE_API_URL | API の URL（App Runner の URL） |
| VITE_GOOGLE_CLIENT_ID | Google OAuth クライアント ID |

---

## カスタムドメインを使う場合

1. Route 53 または外部で DNS を設定
2. ACM で証明書を発行（us-east-1 で CloudFront 用）
3. CloudFront に CNAME と証明書を設定
4. Google Cloud Console にカスタムドメインを追加
5. CORS_ORIGINS にカスタムドメインを追加

---

## コスト目安（東京リージョン）

- RDS（db.t3.micro）: 約 $15/月
- App Runner: 従量課金（低トラフィックなら数ドル）
- S3 + CloudFront: 無料枠内で収まることが多い

無料枠を活用するなら、RDS の「12 か月無料」や App Runner の従量課金を確認してください。

---

## GitHub Actions デプロイパイプライン

`main` ブランチへ push すると、フロントエンド（S3 + CloudFront）とバックエンド（ECR + App Runner）が自動デプロイされます。

### 初回: リポジトリの GitHub Secrets を設定

GitHub リポジトリ → **Settings** → **Secrets and variables** → **Actions** で以下を追加:

| Secret 名 | 必須 | 説明 |
|-----------|------|------|
| AWS_ACCESS_KEY_ID | ✅ | IAM ユーザーのアクセスキー |
| AWS_SECRET_ACCESS_KEY | ✅ | IAM ユーザーのシークレットキー |
| AWS_ECR_REPOSITORY_NAME | ✅ | ECR リポジトリ名（例: `family-hub-api`） |
| AWS_S3_BUCKET_FRONTEND | ✅ | フロント用 S3 バケット名 |
| VITE_GOOGLE_CLIENT_ID | ✅ | Google OAuth クライアント ID |
| VITE_API_URL | ✅ | 本番 API の URL（App Runner の URL） |
| AWS_CLOUDFRONT_DISTRIBUTION_ID | 任意 | CloudFront のディストリビューション ID（キャッシュ無効化用） |
| APP_RUNNER_SERVICE_ARN | 任意 | App Runner のサービス ARN（未設定なら ECR プッシュのみ） |

### IAM ユーザーに必要な権限

- ECR: イメージの push
- S3: 指定バケットへの PutObject / DeleteObject
- CloudFront: CreateInvalidation（任意）
- App Runner: StartDeployment（任意）

### 手動実行

**Actions** タブ → **Deploy to AWS** → **Run workflow** で `main` を選んで実行できます。
