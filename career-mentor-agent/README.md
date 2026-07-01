# 🧭 Career Mentor AI

> A full-stack AI chatbot with **persistent cross-session memory** — powered by **Cognee** (hybrid graph+vector memory), **Google Gemini 2.0 Flash**, and **FastAPI**.

---

## 📁 Folder Structure

```
career-mentor-agent/
├── backend/
│   ├── main.py           ← FastAPI app (Cognee + Gemini)
│   ├── requirements.txt  ← Python dependencies
│   └── .env.example      ← Template for your API keys
├── frontend/
│   └── index.html        ← Single-file chat UI (vanilla HTML/CSS/JS)
└── README.md
```

---

## 🚀 Setup & Running

### 1. Create a Python virtual environment and install dependencies

```bash
# From the project root
cd backend

# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
# source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Set up your `.env` file

```bash
# In the backend/ folder
cp .env.example .env
```

Open `backend/.env` and fill in your **Google Gemini API key**:

```env
GEMINI_API_KEY=AIza...your_real_key_here
LLM_API_KEY=AIza...your_real_key_here   # same key, used by Cognee internally
LLM_PROVIDER=gemini
LLM_MODEL=gemini/gemini-2.0-flash
EMBEDDING_PROVIDER=gemini
EMBEDDING_MODEL=models/embedding-001
```

> 🔑 Get your free Gemini API key at: https://aistudio.google.com/app/apikey

### 3. Start the backend server

```bash
# Make sure you're in the backend/ folder with venv activated
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Career Mentor backend ready.
```

Verify it's working: http://localhost:8000/health → `{"status":"ok"}`

### 4. Open the frontend

Simply open `frontend/index.html` in your browser:

```bash
# Option A: just double-click the file in Explorer

# Option B: quick static server (Python)
cd frontend
python -m http.server 3000
# Then visit http://localhost:3000
```

The chat UI will connect to the backend at `http://localhost:8000`.

---

## 🧠 How the Memory Works (for the Demo)

This app uses **Cognee**'s hybrid graph + vector memory pipeline:

| Step | What happens |
|------|-------------|
| **`cognee.add(text, dataset_name=user_id)`** | Stores the raw conversation turn (user message + bot reply) in Cognee's document store, scoped to *this user's* private dataset. |
| **`cognee.cognify(datasets=[user_id])`** | Cognee processes the text — it extracts entities (e.g. "SQL", "Data Science", "IoT"), relationships, and summaries, then writes them into a **knowledge graph** AND a **vector embedding index**. This is what gives long-term structured memory. |
| **`cognee.search(query, datasets=[user_id])`** | At the start of every new message, we query *both* the vector index (semantic similarity) and the graph (relationship traversal) to retrieve the most relevant past context for this user. |
| **Gemini prompt assembly** | The retrieved memory is injected into the Gemini prompt as a context block, so the LLM can reference it naturally in its reply. |

### Live Demo Flow

1. Open the app → send **"Hi, I'm interested in AI and IoT careers."**
2. Bot responds → Cognee stores this exchange and builds a graph node for "AI", "IoT".
3. **Close the browser tab** (memory is now only in Cognee's storage).
4. Reopen the app (same browser) → send **"I just learned SQL, what should I learn next?"**
5. Cognee retrieves the previous AI/IoT context → Gemini references it in the reply.
6. The **"🧠 Using memory from previous sessions"** tag appears on the bot's bubble, confirming persistence.

> The **Session ID** shown in the header is the same UUID stored in `localStorage` — it never changes for that browser, proving that memory continuity is tied to the user, not the session.

---

## 🛠️ API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | Health check — returns `{"status":"ok"}` |
| `POST` | `/chat`   | Send a message; returns `{"reply":"..."}` |

**POST `/chat` body:**
```json
{
  "user_id": "your-uuid-here",
  "message": "What skills do I need for Data Science?"
}
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML5 / CSS3 / JavaScript (no frameworks) |
| Backend | Python 3.11, FastAPI, Uvicorn |
| Long-term Memory | [Cognee](https://github.com/topoteretes/cognee) — graph + vector hybrid |
| LLM | Google Gemini 2.0 Flash (`gemini-2.0-flash`) |
| Embedding | Google `models/embedding-001` via Cognee |
| Memory Backend | SQLite + local vector store (default Cognee config) |

---

## 🔍 Troubleshooting

| Problem | Fix |
|---------|-----|
| `CORS error` in browser | Make sure the backend is running and CORS is allowed (it is, by default in this app) |
| `Gemini API error` | Check `GEMINI_API_KEY` in `.env` and ensure billing/free tier is active |
| `cognify` takes a long time | Normal — graph building is async. The reply is still returned instantly. |
| Memory not appearing | Ensure the same `localStorage` user ID is being used (same browser, not incognito) |
| Port 8000 already in use | Change the port: `uvicorn main:app --port 8001` and update the `API_BASE` in `index.html` |
