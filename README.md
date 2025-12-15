# LM Shogunate — Autonomous Multi-Agent LLM Council

Welcome to LM Shogunate — a multi-agent autonomous system where multiple top-tier LLM personas collaborate to plan, code, critique, auto-fix, and store results. This README provides a complete, step-by-step guide for a beginner to get from zero to a running deployment (local and Render).

Important: Environment variables (API keys) must be set in your host (Render or environment). Do NOT commit `.env` to the repo.

Contents
- What this is
- Architecture overview
- Prerequisites
- Files in this repo
- Quickstart (local)
- Deploy to Render (recommended)
- Supabase (memory) setup — you mentioned this is already done
- How the council works (agent flow)
- Theme behavior (UI only)
- Security & rotating keys
- Cost & budgeting
- Troubleshooting

---

What this is
------------
- A Streamlit UI (`app.py`) presenting a themed interface (Shogunate, Bandit Camp, Neon Tokyo).
- An orchestration layer (`council.py`) that runs four personas in sequence: Architect, Coder, Critic, Wildcard. They see each other's output and can iterate until a solution is approved.
- Supabase used as persistent storage: sessions, messages, and long-term vector memory.

Architecture overview
---------------------
- UI: Streamlit app (`app.py`) — mobile responsive.
- Orchestrator: `council.py` — calls your deployed LLMs via Azure Foundry / Gemini keys.
- Memory: Supabase with vector extension for semantic recall.
- Host: Render (free tier recommended) — environment variables configured in Render.

Prerequisites
-------------
- Python 3.11+ locally (to run locally). Render will use its runtime.
- Git and a GitHub account with the repo pushed.
- Supabase project with the schema (you mentioned you already ran the SQL).
- Render account with the repository connected and environment variables set.
- Azure Foundry keys and Gemini API key set as env variables in Render.

Files in this repo
------------------
- `app.py` — Streamlit front-end and theme injection.
- `council.py` — Orchestration of personas and database functions.
- `requirements.txt` — Python dependencies (note: `tiktoken` removed for Build portability).
 - `app.py` — Streamlit front-end and theme injection.
 - `council.py` — Orchestration of personas and database functions. NOTE: Opus (your Azure Opus deployment) is configured as the primary Architect and primary Coder for the highest-quality planning and code generation.
 - `requirements.txt` — Python dependencies (note: `tiktoken` removed for Build portability).

Quickstart (local)
------------------
1. Clone the repo and create a venv:

```bash
git clone https://github.com/jadenmubaira-oss/lm-shogunate.git
cd lm-shogunate
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Create a local `.env` (only for local testing). **DO NOT** commit it.

Example `.env` (local only):

```text
AZURE_API_KEY="<YOUR_AZURE_KEY>"
AZURE_API_BASE="https://polyprophet-resource.services.ai.azure.com"
AZURE_API_VERSION="2024-10-21"
GEMINI_API_KEY="<YOUR_GEMINI_KEY>"
SUPABASE_URL="<YOUR_SUPABASE_URL>"
SUPABASE_KEY="<YOUR_SUPABASE_ANON_KEY>"
APP_PASSWORD="your_passcode"
MODEL_OPUS="azure/claude-opus-4-5"
MODEL_GPT="azure/gpt-5.2-chat"
MODEL_GROK="azure/grok-4-fast-reasoning"
MODEL_GEMINI="gemini/gemini-2.0-flash-exp"
MODEL_EMBEDDING="azure/text-embedding-ada-002"
```

3. Run the app locally:

```bash
streamlit run app.py --server.port 8501
```

4. Open `http://localhost:8501` on your phone (if on same network) or computer.

Deploy to Render (recommended)
-----------------------------
1. Push your repo to GitHub and connect Render to the repo.
2. In Render, create a new **Web Service** (connect to `main` branch).
3. Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

4. Add environment variables in Render (do not use `.env` in repo). Important keys (exact names):
 - `AZURE_API_KEY` — your Azure Foundry key
 - `AZURE_API_BASE` — https://polyprophet-resource.services.ai.azure.com
 - `AZURE_API_VERSION` — e.g., 2024-10-21
 - `GEMINI_API_KEY` — your Google Gemini key
 - `SUPABASE_URL` — your Supabase project URL (e.g., https://xyz.supabase.co)
 - `SUPABASE_KEY` — your Supabase anon/public key
 - `APP_PASSWORD` — the passcode for the Streamlit UI (example: Tj!74162oo42oo4)
 - Model envs (map your deployment names):
   - `MODEL_OPUS`=azure/claude-opus-4-5
   - `MODEL_GPT`=azure/gpt-5.2-chat
   - `MODEL_GROK`=azure/grok-4-fast-reasoning
   - `MODEL_GEMINI`=gemini/gemini-2.0-flash-exp
   - `MODEL_EMBEDDING`=your-embedding-deployment-name (e.g., azure/text-embedding-ada-002)

How to ensure the "real thing" works (no mocks)
-----------------------------------------------
1. Deploy an embedding model in Azure Foundry and set `MODEL_EMBEDDING` to its deployment name.
2. Confirm `AZURE_API_KEY`, `AZURE_API_BASE` and `AZURE_API_VERSION` are set in Render.
3. The app calls `litellm.embedding` at runtime to compute embeddings — once configured the system uses real embeddings and real model calls (no mocks required).

5. Deploy and open your Render URL on mobile or desktop.

Supabase — memory (you said you already ran schema)
-------------------------------------------------
- Ensure you enabled the `vector` extension and created `chat_sessions`, `messages`, `memories`, and the `match_memories` function (SQL provided in project notes).

How the council works (agent flow)
---------------------------------
1. User sends a request.
2. Architect (Opus) generates a plan.
3. Coder (GPT-5.2) writes code.
4. Critic (Grok) judges; if REJECTED, auto-fix loop runs with Coder revising (configurable retries).
5. Wildcard (Gemini) offers an alternative.
6. Successes are saved to Supabase memory via embeddings.

Theme behavior
--------------
- UI themes (Shogunate, Bandit Camp, Neon Tokyo) affect only visuals — colors, icons, CSS.
- The actual agent behavior and persona instructions are independent of theme.

Security & rotating keys
------------------------
- Never commit `.env` to the repo. Use Render environment variables.
- If a key has been exposed, rotate it in the provider's console immediately and update Render.

Cost & budgeting
-----------------
- Hosting: Render free tier possible; Supabase free tier possible.
- Model inference costs are the primary ongoing cost — price depends on Azure Foundry / Gemini usage and token counts.
- To reduce cost: lower `max_tokens`, reduce history size, or use cheaper models for some roles.

Troubleshooting
---------------
- Build errors (Rust): We removed `tiktoken` to avoid Rust build on Render. If you need `tiktoken`, provide a prebuilt wheel or enable a build image with Rust.
- Database errors: ensure `SUPABASE_URL` and `SUPABASE_KEY` in Render match your project.
- Model errors: verify model names match deployments exactly.

Contact & next steps
--------------------
- If you'd like, I can:
  - Polish the Neon pink retro theme CSS and add flower motifs.
  - Add PWA (Add-to-Home) support.
  - Add a token-metering/budget limit in `council.py` to cap costs.

Enjoy the council.

---
*(This README was auto-generated and pushed to the repository to make it easy for a beginner to get started.)*
# lm-shogunate
Step forward, warrior. The council convenes
