import { useEffect, useState } from 'react'
import { v4 as uuidv4 } from 'uuid'
import Header from './components/Header'
import IntroBanner from './components/IntroBanner'
import ChatWindow from './components/ChatWindow'
import InputArea from './components/InputArea'
import { useChat } from './hooks/useChat'

const USER_ID_KEY = 'career_mentor_user_id'

export default function App() {
  const [userId, setUserId] = useState('')

  useEffect(() => {
    let stored = localStorage.getItem(USER_ID_KEY)

    if (!stored) {
      stored = uuidv4()
      localStorage.setItem(USER_ID_KEY, stored)
    }

    setUserId(stored)
  }, [])

  const { messages, loading, error, sendMessage, clearChat } = useChat(userId)

  return (
    <div className="mx-auto flex h-screen max-w-4xl flex-col px-4 sm:px-6">
      <Header userId={userId} onClear={clearChat} />
      <IntroBanner show={messages.length === 0} onSelectPrompt={sendMessage} />
      <ChatWindow messages={messages} loading={loading} />
      <InputArea onSend={sendMessage} loading={loading} error={error} />
    </div>
  )
}
