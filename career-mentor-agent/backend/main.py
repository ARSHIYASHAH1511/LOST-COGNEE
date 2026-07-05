"""
AI Career Mentor Chatbot — FastAPI Backend
Uses Cognee v1.2 for persistent memory + Mistral for reasoning.
"""

import os
import sys
import asyncio
import logging
from contextlib import asynccontextmanager

# ── Disable Cognee auth BEFORE importing cognee ───────────────────────────────
os.environ.setdefault("ENABLE_BACKEND_ACCESS_CONTROL", "false")
os.environ.setdefault("CACHING", "false")

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from memory_store import configure_cognee, recall_memories, store_memory

# ─────────────────────────────────────────────
# Load environment variables
# ─────────────────────────────────────────────
load_dotenv()

# NOTE: variable is still named GEMINI_API_KEY for historical reasons — it
# actually holds the Mistral key now. LLM_API_KEY falls back to it if unset.
API_KEY          = os.getenv("GEMINI_API_KEY", "")
LLM_API_KEY      = os.getenv("LLM_API_KEY", API_KEY)

LLM_PROVIDER     = os.getenv("LLM_PROVIDER", "mistral")
# LLM_MODEL may come in as "mistral/mistral-large-latest" (LiteLLM-style) or
# just "mistral-large-latest". Strip any "provider/" prefix since Mistral's
# OpenAI-compatible endpoint wants the bare model name.
_raw_llm_model   = os.getenv("LLM_MODEL", "mistral-large-latest")
LLM_MODEL        = _raw_llm_model.split("/", 1)[-1]

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "mistral")
_raw_embed_model    = os.getenv("EMBEDDING_MODEL", "mistral-embed")
EMBEDDING_MODEL     = _raw_embed_model.split("/", 1)[-1]

# Base URL for the OpenAI-compatible client. Mistral's endpoint by default;
# override via EMBEDDING_ENDPOINT/LLM_ENDPOINT in .env if needed.
LLM_BASE_URL = os.getenv("LLM_ENDPOINT") or "https://api.mistral.ai/v1"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

if not API_KEY:
    log.warning("GEMINI_API_KEY (Mistral key) not set — LLM calls will fail.")

# ─────────────────────────────────────────────
# LLM client (OpenAI SDK, pointed at Mistral's compatible endpoint)
# ─────────────────────────────────────────────
openai_client = openai.OpenAI(api_key=API_KEY, base_url=LLM_BASE_URL)

# ─────────────────────────────────────────────
# Configure Cognee at startup
# ─────────────────────────────────────────────
async def configure_runtime_memory():
    """Initialise Cognee if possible, otherwise keep local persistence active."""
    await configure_cognee(
        llm_provider=LLM_PROVIDER,
        llm_model=LLM_MODEL,
        llm_api_key=LLM_API_KEY,
        embedding_provider=EMBEDDING_PROVIDER,
        embedding_model=EMBEDDING_MODEL,
        embedding_api_key=LLM_API_KEY,
    )


# ─────────────────────────────────────────────
# App lifespan
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await configure_runtime_memory()
    log.info("🚀 Career Mentor backend ready on http://localhost:8000")
    log.info("Chat memory persistence enabled; turns will be saved to %s", os.getenv("CHAT_MEMORY_FILE", "backend/data/chat_memory.json"))
    yield
    log.info("Career Mentor backend shutting down.")


# ─────────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────────
app = FastAPI(
    title="AI Career Mentor Chatbot",
    description="Persistent-memory career advisor powered by Cognee + Mistral",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str


# ─────────────────────────────────────────────
# System Prompt
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# LLM call
# ─────────────────────────────────────────────
def call_llm(memory_context: str, user_message: str) -> str:
    """Build prompt and call the configured LLM (Mistral by default)."""
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


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.user_id or not req.message:
        raise HTTPException(status_code=400, detail="user_id and message are required.")

    # 1 — Recall relevant memories
    try:
        memory_context = await recall_memories(req.user_id, req.message)
    except Exception as exc:
        log.error("Unexpected recall error: %s", exc)
        memory_context = ""

    # 2 — Generate reply
    try:
        reply = call_llm(memory_context, req.message)
    except Exception as exc:
        log.error("LLM call failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"LLM error: {exc}")

    # 3 — Store memory (non-blocking)
    asyncio.create_task(store_memory(req.user_id, req.message, reply))

    # 4 — Return
    return ChatResponse(reply=reply)