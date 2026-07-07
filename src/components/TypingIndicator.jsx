export default function TypingIndicator() {
  return (
    <div className="flex items-end gap-3 animate-fadeUp">
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 text-sm text-white shadow shadow-indigo-500/30">
        🧭
      </div>

      <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm border border-indigo-500/15 bg-[#1a2235] px-4 py-3">
        <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-400 [animation-delay:0ms]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-400 [animation-delay:150ms]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-400 [animation-delay:300ms]" />
      </div>
    </div>
  )
}
