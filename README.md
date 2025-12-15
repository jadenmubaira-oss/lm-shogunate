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
```
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

Notes on embeddings (easiest setup)
----------------------------------
- The project previously required a deployed embedding model. For the easiest setup, the app now uses a deterministic mock embedding function that does NOT require any embedding model or extra API keys. This makes deployment and initial testing trivial.
- If you later want higher-quality semantic search using real embeddings, you can deploy an embedding model in Azure Foundry and replace the `get_embedding` function to call it — I can help with that migration.

How the Supabase memory works (kept for persistence)
---------------------------------------------------
1. The app stores every message in the `messages` table and saves successful solutions in `memories` with an embedding vector.
2. The `match_memories` function (run in SQL on Supabase) performs a nearest-neighbor search against stored embeddings and returns the top relevant memories to the council when you submit a request.
3. Because `get_embedding` uses a deterministic mock, the memory system will behave consistently out of the box without extra configuration. If you later enable real embeddings, the memory retrieval will improve.

Easiest setup summary (minimal required env vars)
------------------------------------------------
Set these in Render (only):
- `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` — for Azure Foundry model calls
- `GEMINI_API_KEY` — for Gemini wildcard role
- `SUPABASE_URL`, `SUPABASE_KEY` — for memory persistence
- `APP_PASSWORD` — passcode to access the UI
- `MODEL_OPUS`, `MODEL_GPT`, `MODEL_GROK`, `MODEL_GEMINI` — map to your deployed model names

With these set, you can deploy to Render and the app will run immediately using deterministic mock embeddings for memory.

5. Deploy and open your Render URL on mobile or desktop.

Supabase — memory (you said you already ran schema)
-------------------------------------------------
Ensure you enabled the `vector` extension and created `chat_sessions`, `messages`, `memories`, and the `match_memories` function. If you haven't already, run the SQL below in the Supabase SQL editor.

Run this SQL in Supabase SQL editor (creates extensions, tables, index, and `match_memories`):

```sql
-- 1) Ensure required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2) Sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz NOT NULL DEFAULT now(),
  metadata jsonb
);

-- 3) Messages table
CREATE TABLE IF NOT EXISTS messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES chat_sessions(id) ON DELETE CASCADE,
  role text NOT NULL,
  content text,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- 4) Memories table (embedding vector uses 1536 dims; adjust if you later use a different embedding size)
CREATE TABLE IF NOT EXISTS memories (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES chat_sessions(id) ON DELETE SET NULL,
  title text,
  content text,
  embedding vector(1536),
  created_at timestamptz NOT NULL DEFAULT now()
);

-- 5) Index for fast ANN search (ivfflat). Tune lists for your dataset size.
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes WHERE tablename = 'memories' AND indexname = 'memories_embedding_ivfflat_idx'
  ) THEN
    EXECUTE 'CREATE INDEX memories_embedding_ivfflat_idx ON memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)';
  END IF;
END
$$;

-- 6) Nearest-neighbor helper: returns rows ordered by nearest embedding and a simple score
CREATE OR REPLACE FUNCTION match_memories(query vector(1536), max_results integer DEFAULT 5)
RETURNS TABLE (
  id uuid,
  session_id uuid,
  title text,
  content text,
  score double precision
) AS $$
  SELECT
    m.id,
    m.session_id,
    m.title,
    m.content,
    1.0 / (1.0 + (m.embedding <-> query)) AS score
  FROM memories m
  WHERE m.embedding IS NOT NULL
  ORDER BY m.embedding <-> query
  LIMIT max_results;
$$ LANGUAGE SQL STABLE;
```

Notes:
- The SQL above uses `vector(1536)` because the app's mock embedding uses 1536 dims. If you later enable real embeddings with a different dimensionality, update the `vector(...)` size accordingly.
- If your Supabase plan or Postgres build does not support `ivfflat`, you can omit the ivfflat index line; queries will still work but may be slower for large datasets.

Quick smoke test (run in SQL editor):

1) Create a session and insert a sample memory (ensure your vector literal matches the declared dimension):

```sql
INSERT INTO chat_sessions (id) VALUES (gen_random_uuid()) RETURNING id;
-- Replace <SESSION_ID> in the next statement with the returned id and provide a proper 1536-length vector
INSERT INTO memories (session_id, title, content, embedding)
VALUES ('<SESSION_ID>', 'Test memory', 'This is a test memory content',
        ARRAY[0.0 /* repeat 1536 floats as needed */]::vector);
```

2) Query nearest neighbors:

```sql
SELECT * FROM match_memories(ARRAY[0.0 /* 1536 floats */]::vector, 5);
```

If you want me to verify these steps remotely, provide a temporary read-only `SUPABASE_KEY` (or paste the SQL editor output) and I will run the checks and report back.

Supabase gotchas & fixes
-------------------------
Real Supabase projects sometimes differ from the example schema (existing installs or earlier migrations). Here are quick checks and fixes you can run if you hit errors:

1) Inspect the `memories` table shape:

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'memories';
```

2) Common issues and fixes:
- Missing `session_id`, `title`, or `content` in `memories`: add them (non-destructive):

```sql
ALTER TABLE memories ADD COLUMN IF NOT EXISTS session_id uuid;
ALTER TABLE memories ADD COLUMN IF NOT EXISTS title text;
ALTER TABLE memories ADD COLUMN IF NOT EXISTS content text;
```

- `chat_sessions.title` is NOT NULL: create sessions with a title or relax the constraint. Preferred (create with title):

```sql
INSERT INTO chat_sessions (title, metadata) VALUES ('Smoke test session', '{}'::jsonb) RETURNING id;
```

If you prefer to allow empty titles:

```sql
ALTER TABLE chat_sessions ALTER COLUMN title DROP NOT NULL;
-- or set a default
ALTER TABLE chat_sessions ALTER COLUMN title SET DEFAULT 'Untitled session';
```

- `memories.id` type mismatch (you may see `bigint` instead of `uuid`): adapt the function return types or migrate the column. Quick, non-destructive approach — keep `id bigint` in the function:

```sql
CREATE OR REPLACE FUNCTION match_memories(query vector(1536), max_results integer DEFAULT 5)
RETURNS TABLE (id bigint, session_id uuid, title text, content text, score double precision) AS $$
  SELECT m.id, m.session_id, m.title, m.content, 1.0 / (1.0 + (m.embedding <-> query)) AS score
  FROM memories m
  WHERE m.embedding IS NOT NULL
  ORDER BY m.embedding <-> query
  LIMIT max_results;
$$ LANGUAGE SQL STABLE;
```

3) Smoke-test insert (creates a titled session and a 1536-d zero vector memory):

```sql
WITH s AS (
  INSERT INTO chat_sessions (title, metadata) VALUES ('Smoke test session', '{}'::jsonb) RETURNING id
)
INSERT INTO memories (session_id, title, content, embedding, created_at)
SELECT s.id, 'Smoke test memory', 'Inserted by smoke test', array_fill(0.0::double precision, ARRAY[1536])::vector, now() FROM s;
```

4) Verify retrieval:

```sql
SELECT * FROM match_memories(array_fill(0.0::double precision, ARRAY[1536])::vector, 5);
```

If anything errors, paste the exact error text here and I'll provide the precise fix.

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

PWA & Mobile install
---------------------
- The app includes a lightweight Add-to-Home-Screen prompt for modern mobile browsers when using the Neon Tokyo theme. To enable the browser install prompt you may also need to serve the app over HTTPS (Render does this) and follow standard PWA behavior.

Token budgeting & cost controls
------------------------------
- Per-session token budget is enforced via `SESSION_TOKEN_BUDGET` (env, default 5000 tokens). You can tune `MAX_TOKENS_PER_CALL` (default 3000) to cap per-call token usage.
- The system will preferentially use the high-quality `MODEL_OPUS` for `Architect` and `Coder` roles; if budget is low the orchestrator will fall back to cheaper models (e.g., `MODEL_GEMINI` or `MODEL_HAIKU`) automatically.

Environment variable reference (add these to Render):
- `SESSION_TOKEN_BUDGET` — integer, total token budget per session (default 5000)
- `MAX_TOKENS_PER_CALL` — integer, per-call hard cap (default 3000)
 - `MODEL_EMBEDDING` — embedding deployment name (optional). Only required if you enable real embeddings; the app defaults to a deterministic mock embedding so no embedding model is required for initial deployment.

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
