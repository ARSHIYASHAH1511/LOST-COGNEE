"""
AI Career Mentor Chatbot — FastAPI Backend
Uses Cognee v1.2 for persistent memory + OpenAI GPT-4o-mini for reasoning.
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager

# ── Disable Cognee auth BEFORE importing cognee ───────────────────────────────
os.environ.setdefault("ENABLE_BACKEND_ACCESS_CONTROL", "false")
os.environ.setdefault("CACHING", "false")

import cognee
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─────────────────────────────────────────────
# Load environment variables
# ─────────────────────────────────────────────
load_dotenv()

OPENAI_API_KEY  = os.getenv("GEMINI_API_KEY", "")   # stored as GEMINI_API_KEY in .env
LLM_API_KEY     = os.getenv("LLM_API_KEY", OPENAI_API_KEY)
LLM_PROVIDER    = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL       = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
EMBEDDING_MODEL  = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

if not OPENAI_API_KEY:
    log.warning("GEMINI_API_KEY (OpenAI key) not set — LLM calls will fail.")

# ─────────────────────────────────────────────
# OpenAI client
# ─────────────────────────────────────────────
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ─────────────────────────────────────────────
# Configure Cognee at startup
# ─────────────────────────────────────────────
async def configure_cognee():
    """Point Cognee's internal LLM + embeddings at OpenAI."""
    try:
        await cognee.config.set_llm_config({
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini",
            "llm_api_key": LLM_API_KEY,
        })
        log.info("Cognee LLM → openai/gpt-4o-mini")
    except Exception as exc:
        log.warning("Cognee LLM config skipped: %s", exc)

    try:
        await cognee.config.set_embedding_config({
            "embedding_provider": "openai",
            "embedding_model": EMBEDDING_MODEL,
            "embedding_api_key": LLM_API_KEY,
        })
        log.info("Cognee Embeddings → openai/%s", EMBEDDING_MODEL)
    except Exception as exc:
        log.warning("Cognee Embedding config skipped: %s", exc)


# ─────────────────────────────────────────────
# App lifespan
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await configure_cognee()
    log.info("🚀 Career Mentor backend ready on http://localhost:8000")
    yield
    log.info("Career Mentor backend shutting down.")


# ─────────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────────
app = FastAPI(
    title="AI Career Mentor Chatbot",
    description="Persistent-memory career advisor powered by Cognee + OpenAI",
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
# Memory helpers  (FIXED: use `datasets=[user_id]` / `dataset_name=user_id`,
# NOT `user_id=user_id` — cognee.recall()/remember() don't accept that kwarg)
# ─────────────────────────────────────────────
async def recall_memories(user_id: str, query: str) -> str:
    """Retrieve relevant memories for this user from Cognee."""
    try:
        results = await cognee.recall(query, datasets=[user_id])

        if not results:
            return ""

        memory_lines = []
        for item in results[:8]:
            text = getattr(item, "text", None) or getattr(item, "content", None) or str(item)
            if text.strip():
                memory_lines.append(text.strip())

        return "\n".join(memory_lines) if memory_lines else ""

    except Exception as exc:
        log.warning("Memory recall failed for user %s: %s", user_id, exc)
        return ""


async def store_memory(user_id: str, user_msg: str, bot_reply: str):
    """Persist this conversation turn into Cognee."""
    text_to_store = f"User said: {user_msg}\nCareer Mentor replied: {bot_reply}"
    try:
        await cognee.remember(text_to_store, dataset_name=user_id)
        log.info("Memory stored for user %s", user_id)
    except Exception as exc:
        log.error("Memory store failed for user %s: %s", user_id, exc)


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
    """Build prompt and call OpenAI gpt-4o-mini."""
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
        model="gpt-4o-mini",
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
        log.error("OpenAI call failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"LLM error: {exc}")

    # 3 — Store memory (non-blocking)
    asyncio.create_task(store_memory(req.user_id, req.message, reply))

    # 4 — Return
    return ChatResponse(reply=reply)