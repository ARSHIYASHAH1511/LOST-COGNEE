const BASE_URL = 'https://career-mentor-backend.onrender.com'

export async function sendChatMessage({ message, userId, sessionId }) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 30000) // 30 sec timeout

  try {
    const res = await fetch(`${BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, userId, sessionId }),
      signal: controller.signal,
    })

    clearTimeout(timeout)

    if (!res.ok) {
      const text = await res.text()
      throw new Error(`HTTP ${res.status}: ${text}`)
    }

    return res.json()
  } catch (err) {
    clearTimeout(timeout)
    if (err.name === 'AbortError') {
      throw new Error('Request timed out. Backend may be waking up — try again in 30 seconds.')
    }
    throw err
  }
}
