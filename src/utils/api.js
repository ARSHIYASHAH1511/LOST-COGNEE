const BASE_URL = 'https://lost-cognee-backend-final.onrender.com/chat'

export async function sendChatMessage({ message, userId, sessionId }) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 90000) // 90 sec timeout

  try {
    const res = await fetch(BASE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: userId, message }), // ✅ Fixed: userId → user_id
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
