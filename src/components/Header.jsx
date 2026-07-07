export default function Header({ userId, onClear }) {
  return (
    <header className="flex items-center justify-between gap-4 border-b border-indigo-500/15 py-4">
      <div className="flex items-center gap-3 min-w-0">
        <div className="relative shrink-0">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-indigo-400/30 bg-gradient-to-br from-indigo-500/20 to-violet-500/20 text-xl shadow-lg shadow-indigo-500/20">
            🧭
          </div>
          <span className="absolute right-0 top-0 h-3 w-3 rounded-full border-2 border-[#0b0f1a] bg-emerald-400" />
        </div>

        <div className="min-w-0">
          <h1 className="truncate font-display text-lg font-bold text-slate-100">
            Career Mentor AI
          </h1>
          <p className="text-xs text-emerald-400">
            Memory-powered career guidance
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className="hidden rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-emerald-300 md:block">
          Persistent Memory
        </div>

        <div
          title={userId}
          className="hidden max-w-[140px] truncate rounded-full border border-indigo-400/20 bg-indigo-500/10 px-3 py-1 text-xs text-indigo-300 sm:block"
        >
          {userId}
        </div>

        <button
          onClick={onClear}
          className="rounded-full border border-red-400/20 bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-300 transition hover:bg-red-500/20"
        >
          Clear
        </button>
      </div>
    </header>
  )
}
