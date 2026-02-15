import axios from 'axios'

// 本番: VITE_API_URL を設定（例: https://api.example.com）
// ローカル: 未設定なら相対パス（Vite プロキシ経由）
export const baseURL = import.meta.env.VITE_API_URL || ''

export const api = axios.create({ baseURL })
