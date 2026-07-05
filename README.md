#a career agent

An AI-powered career mentor chatbot with **persistent long-term memory**.  
It remembers everything you tell it — even after you close the tab — so you can build on career conversations across sessions.

---

## ✨ Features

- **🧠 Persistent Memory** — Powered by [Cognee](https://github.com/topoteretes/cognee). Every chat is stored and recalled across sessions.
- **💬 Career Mentor Chat** — Ask about career paths, skill gaps, learning plans, and interview prep.
- **🔍 Context-Aware Answers** — The AI pulls relevant past conversations to give personalized advice.
- **🛡️ Works Offline** — Falls back to local JSON file storage when Cognee is unavailable.
- **⚡ Fast & Lightweight** — Single-page chat UI + FastAPI backend.

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML + CSS + Vanilla JS (single-page chat UI) |
| **Backend** | FastAPI (Python) |
| **LLM** | Mistral (via OpenAI-compatible SDK) |
| **Memory** | Cognee (vector knowledge graph) + JSON file fallback |
| **Deployment** | Uvicorn + Docker-ready |

---

## 📁 Project Structure

