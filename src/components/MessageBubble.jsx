import ReactMarkdown from 'react-markdown'

function formatTime(date) {
  return new Intl.DateTimeFormat('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div
      className={`flex items-end gap-3 animate-fadeUp ${
        isUser ? 'flex-row-reverse' : ''
      }`}
    >
      <div
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm shadow ${
          isUser
            ? 'border border-indigo-400/30 bg-slate-700 text-indigo-200'
            : 'bg-gradient-to-br from-indigo-500 to-violet-500 text-white shadow-indigo-500/30'
        }`}
      >
        {isUser ? 'U' : '🧭'}
      </div>

      <div className={`flex max-w-[80%] flex-col ${isUser ? 'items-end' : ''}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-6 shadow-md ${
            isUser
              ? 'rounded-br-sm bg-gradient-to-br from-indigo-500 to-violet-500 text-white'
              : 'rounded-bl-sm border border-indigo-500/15 bg-[#1a2235] text-slate-200'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none break-words">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        <span className="mt-1 px-1 text-[11px] text-slate-500">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  )
}
