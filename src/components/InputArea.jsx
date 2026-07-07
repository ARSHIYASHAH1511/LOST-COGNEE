import { useRef } from 'react'

export default function InputArea({ onSend, loading, error }) {
  const textareaRef = useRef(null)

  const handleSend = () => {
    const text = textareaRef.current.value.trim()
    if (!text || loading) return

    onSend(text)
    textareaRef.current.value = ''
    textareaRef.current.style.height = 'auto'
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const autoResize = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`
  }

  return (
    <div className="border-t border-indigo-500/15 py-4">
      {error && (
        <div className="mb-3 rounded-xl border border-red-400/30 bg-red-500/10 px-4 py-2 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="flex items-end gap-3 rounded-3xl border border-indigo-500/20 bg-[#1e2a3a] px-4 py-3 focus-within:border-indigo-400/40">
        <textarea
          ref={textareaRef}
          rows={1}
          disabled={loading}
          onKeyDown={handleKeyDown}
          onInput={autoResize}
          placeholder="Ask about career paths, skills, placements, or next steps..."
          className="max-h-[140px] flex-1 resize-none overflow-y-auto bg-transparent text-sm text-slate-100 outline-none placeholder:text-slate-500 disabled:opacity-50"
        />

        <button
          onClick={handleSend}
          disabled={loading}
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 text-white shadow-lg shadow-indigo-500/25 transition hover:scale-105 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
          ) : (
            <svg
              className="h-4 w-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </div>

      <p className="mt-2 text-center text-[11px] text-slate-500">
        Press Enter to send · Shift+Enter for new line
      </p>
    </div>
  )
}
