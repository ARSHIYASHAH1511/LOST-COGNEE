# Cognee — STS-Stream Fork

This is a fork of [Cognee](https://github.com/topoteretes/cognee), the open-source AI memory platform for agents.

Used as the **memory & RAG layer** for **[STS-Stream](https://github.com/ARSHIYASHAH1511/STS-Stream)** — an AI-powered career guidance platform.

---

## 🚀 What is Cognee?

Cognee gives AI agents **persistent long-term memory**.  
You can ingest data in any format, and it builds a self-hosted knowledge graph so agents can:

- **Remember** — Recall past conversations and user data across sessions
- **Connect** — Link related facts (e.g., a user's skill gaps + trending industry roles)
- **Act** — Generate personalized recommendations with full context

---

## 🧠 Why this fork?

STS-Stream uses **4 AI agents** (Career, Resume, Learning, Interview) that need to:

- Remember each user's profile, strengths, and progress
- Understand skill gaps by comparing resumes against industry trends
- Recommend personalized learning plans that adapt over time

Cognee provides the memory layer that makes this possible.

---

## 🛠️ What's changed / added?

| Change | Description |
|--------|-------------|
| Configuration | Pre-configured for Gemini API + local vector store |
| Integration | Ready-to-use with STS-Stream agent files |
| Dependencies | Updated for compatibility with `google-generativeai` |

---

## ⚙️ Setup

```bash
# Clone the repo
git clone https://github.com/acharnikhil72-commits/cognee.git
cd cognee

# Install dependencies
pip install -r requirements.txt

# Set your Gemini API key
set GEMINI_API_KEY=your_key_here
set LLM_PROVIDER=gemini
