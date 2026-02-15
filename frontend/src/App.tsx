import { useState } from 'react'
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google'
import { jwtDecode } from 'jwt-decode'
import Chat from './Chat'
import { baseURL } from './api'

const GOOGLE_CLIENT_ID =
  import.meta.env.VITE_GOOGLE_CLIENT_ID ||
  '558585274838-u6tav0qdsj1ffpa3o59nfaepto210b49.apps.googleusercontent.com'

const APP_VERSION = import.meta.env.VITE_APP_VERSION || 'dev'
const BUILD_TIME = import.meta.env.VITE_BUILD_TIME || ''
const VERSION_LABEL = BUILD_TIME ? `v.${APP_VERSION} · ${BUILD_TIME}` : `v.${APP_VERSION}`

type User = {
  name: string
  email: string
  idToken: string
}

function AppContent() {
  const [user, setUser] = useState<User | null>(null)

  if (user) {
    return (
      <div style={{ minHeight: '100vh', background: '#f3f4f6' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 16, flexWrap: 'wrap', gap: 8 }}>
          <span style={{ color: '#6b7280', fontSize: 12 }}>
            API: {baseURL ? baseURL.replace(/^https?:\/\//, '').replace(/\/$/, '') : '未設定（送信できません）'}
            {' · '}
            <span title="ビルド版"> {VERSION_LABEL}</span>
          </span>
          <span style={{ marginRight: 12, color: '#6b7280' }}>{user.name} さん</span>
          <button
            onClick={() => setUser(null)}
            style={{
              padding: '8px 16px',
              background: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: 8,
              cursor: 'pointer',
            }}
          >
            ログアウト
          </button>
        </div>
        <Chat
          userName={user.name}
          idToken={user.idToken}
          onAuthError={() => setUser(null)}
        />
      </div>
    )
  }

  return (
    <div style={{ textAlign: 'center', marginTop: '100px' }}>
      <h1 style={{ color: '#2563eb', marginBottom: 8 }}>Family Hub</h1>
      <p style={{ color: '#6b7280', marginBottom: 24 }}>
        Googleアカウントでログインして、家族とチャットしよう
      </p>
      {VERSION_LABEL && (
        <p style={{ color: '#9ca3af', fontSize: 12, marginBottom: 16 }}>{VERSION_LABEL}</p>
      )}
      <div style={{ display: 'inline-block' }}>
        <GoogleLogin
          onSuccess={(credentialResponse) => {
            if (credentialResponse.credential) {
              const decoded = jwtDecode<{ name?: string; email?: string }>(
                credentialResponse.credential
              )
              setUser({
                name: decoded.name || '匿名',
                email: decoded.email || '',
                idToken: credentialResponse.credential,
              })
            }
          }}
          onError={() => console.log('ログインに失敗しました')}
        />
      </div>
    </div>
  )
}

function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AppContent />
    </GoogleOAuthProvider>
  )
}

export default App