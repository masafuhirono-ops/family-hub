import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { api } from './api'

const APP_VERSION = import.meta.env.VITE_APP_VERSION || 'dev'
const BUILD_TIME = import.meta.env.VITE_BUILD_TIME || ''
const VERSION_LABEL = BUILD_TIME ? `v.${APP_VERSION} · ${BUILD_TIME}` : `v.${APP_VERSION}`

type Message = {
  id: number
  sender_name: string
  content: string
  created_at: string
}

type ChatProps = {
  userName: string
  idToken: string
  onAuthError?: () => void
}

export default function Chat({ userName, idToken, onAuthError }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const apiHeaders = { Authorization: `Bearer ${idToken}` }

  const fetchMessages = async () => {
    try {
      const res = await api.get<Message[]>('/api/v1/chat/messages', {
        headers: apiHeaders,
      })
      setMessages(res.data)
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 401) {
        onAuthError?.()
      } else {
        console.error('メッセージ取得エラー:', err)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMessages()
    const interval = setInterval(fetchMessages, 3000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!inputText.trim()) return

    try {
      await api.post(
        '/api/v1/chat/messages',
        { content: inputText.trim() },
        { headers: apiHeaders }
      )
      setInputText('')
      fetchMessages()
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 401) {
        onAuthError?.()
      } else {
        console.error('送信エラー:', err)
      }
    }
  }

  const formatTime = (dateStr: string) => {
    const str =
      dateStr.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(dateStr)
        ? dateStr
        : dateStr + 'Z'
    const d = new Date(str)
    return d.toLocaleTimeString('ja-JP', {
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Tokyo',
    })
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>家族チャット</h2>
      <p style={styles.subtitle}>ようこそ {userName} さん</p>
      <p style={{ color: '#9ca3af', fontSize: 12, marginTop: 4, marginBottom: 0 }}>{VERSION_LABEL}</p>

      <div style={styles.messagesBox}>
        {loading ? (
          <p style={styles.loading}>読み込み中...</p>
        ) : messages.length === 0 ? (
          <p style={styles.empty}>まだメッセージはありません。最初のメッセージを送ってみよう！</p>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} style={styles.messageRow}>
              <span style={styles.sender}>{msg.sender_name}</span>
              <span style={styles.time}>{formatTime(msg.created_at)}</span>
              <p style={styles.content}>{msg.content}</p>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={styles.inputArea}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="メッセージを入力..."
          style={styles.input}
        />
        <button onClick={sendMessage} style={styles.sendButton}>
          送信
        </button>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: 600,
    margin: '40px auto',
    padding: 20,
    fontFamily: 'sans-serif',
  },
  title: {
    color: '#2563eb',
    marginBottom: 4,
  },
  subtitle: {
    color: '#6b7280',
    marginBottom: 20,
    fontSize: 14,
  },
  messagesBox: {
    background: '#f9fafb',
    border: '1px solid #e5e7eb',
    borderRadius: 12,
    padding: 16,
    minHeight: 300,
    maxHeight: 400,
    overflowY: 'auto',
    marginBottom: 16,
  },
  loading: {
    color: '#9ca3af',
    textAlign: 'center' as const,
    padding: 20,
  },
  empty: {
    color: '#9ca3af',
    textAlign: 'center' as const,
    padding: 40,
  },
  messageRow: {
    marginBottom: 12,
    padding: 12,
    background: 'white',
    borderRadius: 8,
    border: '1px solid #e5e7eb',
  },
  sender: {
    fontWeight: 'bold',
    color: '#2563eb',
    marginRight: 8,
    fontSize: 14,
  },
  time: {
    color: '#9ca3af',
    fontSize: 12,
  },
  content: {
    margin: '8px 0 0 0',
    lineHeight: 1.5,
  },
  inputArea: {
    display: 'flex',
    gap: 8,
  },
  input: {
    flex: 1,
    padding: '12px 16px',
    border: '1px solid #d1d5db',
    borderRadius: 8,
    fontSize: 16,
  },
  sendButton: {
    padding: '12px 24px',
    background: '#2563eb',
    color: 'white',
    border: 'none',
    borderRadius: 8,
    fontWeight: 'bold',
    cursor: 'pointer',
  },
}
