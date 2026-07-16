import os
import sys
import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()
import openai

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Disable Cognee auth & caching ─────────────────────────────────────────
os.environ.setdefault("ENABLE_BACKEND_ACCESS_CONTROL", "false")
os.environ.setdefault("CACHING", "false")

# ── Add backend dir to path ───────────────────────────────────────────────
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# ── Import local modules ──────────────────────────────────────────────────
from database import engine, SessionLocal, Base
from memory_store import configure_cognee, recall_memories, store_memory

Base.metadata.create_all(bind=engine)

# ── Load env vars ─────────────────────────────────────────────────────────
load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", API_KEY)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mistral")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-large-latest").split("/", 1)[-1]
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "mistral")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "mistral-embed").split("/", 1)[-1]
LLM_BASE_URL = os.getenv("LLM_ENDPOINT") or "https://api.mistral.ai/v1"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

if not API_KEY:
    log.warning("MISTRAL_API_KEY not set — LLM calls will fail.")

if API_KEY:
    os.environ["OPENAI_API_KEY"] = API_KEY

openai_client = openai.OpenAI(api_key=API_KEY, base_url=LLM_BASE_URL)

# ── Configure Cognee ──────────────────────────────────────────────────────
async def configure_runtime_memory():
    await configure_cognee(
        llm_provider=LLM_PROVIDER,
        llm_model=LLM_MODEL,
        llm_api_key=LLM_API_KEY,
        embedding_provider=EMBEDDING_PROVIDER,
        embedding_model=EMBEDDING_MODEL,
        embedding_api_key=LLM_API_KEY,
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    await configure_runtime_memory()
    log.info("🚀 Career Mentor backend ready")
    log.info("Chat memory persistence enabled.")
    yield
    log.info("Career Mentor backend shutting down.")

# ── Create app ONCE with lifespan ─────────────────────────────────────────
app = FastAPI(
    title="AI Career Mentor Chatbot",
    description="Persistent-memory career advisor powered by Cognee + Mistral",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Add CORS to THIS same app ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ───────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

# ── System Prompt ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are "Career Mentor AI", a warm, encouraging, and knowledgeable career advisor \
specifically for students and early-career professionals. Your goals are:
1. Help users discover suitable career paths based on their interests, skills, and goals.
2. Identify skill gaps and suggest concrete, actionable learning resources.
3. Remember everything the user has shared with you in past sessions and reference it naturally.
4. Keep responses concise (3–5 short paragraphs max), friendly, and jargon-free.
5. Always end with one specific follow-up question to keep the conversation moving forward.

If the user's message touches on a career field, skill, or goal — acknowledge it explicitly \
and connect it to anything you know from memory about this person.
"""

# ── LLM Call ──────────────────────────────────────────────────────────────
def call_llm(memory_context: str, user_message: str) -> str:
    memory_block = (
        f"\n\n--- Relevant memory from previous sessions ---\n{memory_context}\n--- End of memory ---\n"
        if memory_context
        else "\n\n(No prior memory found for this user yet.)\n"
    )
    user_content = (
        f"{memory_block}"
        f"\nUser's new message: {user_message}\n\n"
        "Respond as the Career Mentor. If memory context is available, "
        "reference relevant details naturally in your reply."
    )

    response = openai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_content},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

# ── Endpoints ─────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "Career Mentor AI backend is running successfully!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.user_id or not req.message:
        raise HTTPException(status_code=400, detail="user_id and message are required.")

    try:
        memory_context = await recall_memories(req.user_id, req.message)
    except Exception as exc:
        log.error("Unexpected recall error: %s", exc)
        memory_context = ""

    try:
        reply = call_llm(memory_context, req.message)
    except Exception as exc:
        log.error("LLM call failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"LLM error: {exc}")

    asyncio.create_task(store_memory(req.user_id, req.message, reply))

    return ChatResponse(reply=reply)
