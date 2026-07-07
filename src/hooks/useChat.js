import { useEffect, useMemo, useState } from 'react'
import { sendChatMessage } from '../utils/api'

const CHAT_LOG_KEY = 'career_mentor_chat_log'

export function useChat(userId) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const sessionId = useMemo(() => `session_${Date.now()}`, [])

  useEffect(() => {
    const saved = localStorage.getItem(CHAT_LOG_KEY)
    if (saved) {
      try {
        const parsed = JSON.parse(saved).map((msg) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }))
        setMessages(parsed)
      } catch {
        localStorage.removeItem(CHAT_LOG_KEY)
      }
    }
  }, [])

  useEffect(() => {
    localStorage.setItem(CHAT_LOG_KEY, JSON.stringify(messages))
  }, [messages])

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return

    const userMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setLoading(true)
    setError('')

    try {
      const data = await sendChatMessage({
        message: text,
        userId,
        sessionId,
      })

      const botText =
        data.response ||
        data.message ||
        data.reply ||
        'I received your message, but the response format needs adjustment.'

      const botMessage = {
        id: `bot_${Date.now()}`,
        role: 'bot',
        content: botText,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, botMessage])
    } catch (err) {
      console.error(err)
      setError('Could not connect to backend. Check API URL or CORS.')
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    localStorage.removeItem(CHAT_LOG_KEY)
  }

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearChat,
  }
}
