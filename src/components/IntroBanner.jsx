const starterPrompts = [
  "I'm interested in AI and IoT careers",
  'What skills do I need for Data Science?',
  'I just learned SQL. What should I learn next?',
  "I'm a CS student with 6 months left for placements",
  'Compare Software Engineer vs Data Analyst roles',
]

export default function IntroBanner({ show, onSelectPrompt }) {
  if (!show) return null

  return (
    <section className="flex flex-col items-center px-4 py-10 text-center animate-fadeUp">
      <div className="mb-5 flex h-20 w-20 animate-floaty items-center justify-center rounded-3xl border border-indigo-400/25 bg-gradient-to-br from-indigo-500/20 to-violet-500/20 text-4xl shadow-2xl shadow-indigo-500/10">
        🧭
      </div>

      <h2 className="font-display text-2xl font-bold text-slate-100">
        Your AI career guide
      </h2>

      <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
        Ask about career paths, placement prep, skill gaps, roadmap planning,
        or role comparison. Your conversation is remembered across sessions.
      </p>

      <div className="mt-6 flex max-w-3xl flex-wrap justify-center gap-3">
        {starterPrompts.map((prompt) => (
          <button
            key={prompt}
            onClick={() => onSelectPrompt(prompt)}
            className="rounded-full border border-indigo-400/20 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-300 transition hover:-translate-y-0.5 hover:bg-indigo-500/20"
          >
            {prompt}
          </button>
        ))}
      </div>
    </section>
  )
}
