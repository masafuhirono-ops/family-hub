# ngrok でインターネットからアクセスする方法

## 1. ngrok のインストール

1. [ngrok](https://ngrok.com/) に登録（無料）
2. ダウンロードしてインストール: https://ngrok.com/download
3. サインアップ後に表示される **認証トークン** でログイン:
   ```powershell
   ngrok config add-authtoken あなたのトークン
   ```

## 2. 環境変数の設定

バックエンドで Google トークン検証を使うため、`backend/.env` を作成してください:

```powershell
cd family-hub\backend
copy .env.example .env
# .env を編集して GOOGLE_CLIENT_ID を設定（フロントと同じ値）
```

## 3. アプリの起動

**ターミナル1 - バックエンド**
```powershell
cd family-hub\backend
.\start.ps1
```

**ターミナル2 - フロントエンド**
```powershell
cd family-hub\frontend
npm run dev
```

**ターミナル3 - ngrok**
```powershell
ngrok http 5173
```

## 4. ngrok の URL を確認

ngrok を起動すると、次のような表示が出ます:
```
Forwarding    https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:5173
```

この **https://xxxx....ngrok-free.app** があなたの公開URLです。

## 5. Google Cloud Console の設定

1. [Google Cloud Console](https://console.cloud.google.com/) を開く
2. **API とサービス** → **認証情報**
3. 使用中の **OAuth 2.0 クライアント ID** をクリック
4. **認可された JavaScript 生成元** に以下を追加:
   ```
   https://xxxx-xx-xx-xx-xx.ngrok-free.app
   ```
   （ngrok で表示された URL をそのまま入力）
5. **保存** をクリック

※ ngrok の無料プランでは起動のたびに URL が変わります。その都度 Google Cloud Console に新しい URL を追加してください。有料プランでは固定ドメインが使えます。

## 6. アクセス

携帯や他の PC のブラウザで、ngrok の URL を開きます。
同じ Wi-Fi でなくても、インターネット接続があればアクセスできます。

---

**注意**: 初回アクセス時、ngrok の無料プランでは「Visit Site」ボタンを押す必要がある場合があります。
