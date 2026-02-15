import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

// Google OAuth 2.0 のポリシー準拠のため、Referrer-Policy を設定
// これにより、Google の認証サーバーが正しくオリジンを検証できるようになります
if (!document.querySelector('meta[name="referrer"]')) {
  const meta = document.createElement('meta')
  meta.name = 'referrer'
  meta.content = 'strict-origin-when-cross-origin'
  document.head.appendChild(meta)
}

const root = document.getElementById('root')
if (root) {
  createRoot(root).render(
    <StrictMode>
      <App />
    </StrictMode>
  )
}