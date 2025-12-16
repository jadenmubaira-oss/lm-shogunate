# 🧠 NEURAL COUNCIL - #1 IN THE WORLD

## The Ultimate Multi-Agent AI System

**4 AI models collaborating, debating, and refining until PERFECT.**

---

## 🔥 What Makes This #1

| Feature | Status | Description |
|---------|--------|-------------|
| 👁️ **TRUE VISION** | ✅ | Claude actually SEES your screenshots |
| 🧠 **TRUE EMBEDDINGS** | ✅ | Azure OpenAI semantic embeddings |
| 🔄 **UNLIMITED REFINEMENT** | ✅ | 10 rounds, 90% quality threshold |
| 📈 **SELF-RATING** | ✅ | Every response scored for quality |
| 💭 **DEBATE MODE** | ✅ | Agents challenge each other |
| 📊 **DYNAMIC ROUTING** | ✅ | Query classification |

---

## 🏆 The #1 Architecture

```
Query Input + Screenshot
    ↓
📊 CLASSIFY (code/creative/research/reasoning)
    ↓
🎯 STRATEGIST (WITH VISION - sees screenshots!)
    ↓
💭 DEBATE MODE? ─────────────────┐
    ↓ No                         ↓ Yes
⚔️📿 PARALLEL                   ⚔️ PROPOSAL
(Executor + Sage)               📿 CHALLENGE
    ↓                           ⚔️ RESPONSE
    ├───────────────────────────┘
    ↓
🔄 UNLIMITED REFINEMENT LOOP
    WHILE quality < 90% OR Sage has issues:
        ⚔️ Executor FIXES
        📿 Sage RE-REVIEWS
        📈 Quality RECALCULATED
    (Up to 10 rounds - we don't stop until PERFECT)
    ↓
👑 EMPEROR SYNTHESIS
```

---

## 🚀 Revolutionary Features

### 1. TRUE VISION
```python
# We actually pass screenshots to Claude's vision API!
call_agent_with_vision("Strategist", context, screenshot_b64, 4000)
```

### 2. TRUE EMBEDDINGS
```python
# Real semantic similarity, not hash-based!
embedding = get_real_embedding(text)  # Azure OpenAI API
```

### 3. UNLIMITED REFINEMENT
```python
MAX_REFINEMENT_ROUNDS = 10   # Not just 3!
QUALITY_THRESHOLD = 0.90     # Must be 90%+ to stop
while (not sage_approves or quality < 0.90) and round < 10:
    # Keep refining until PERFECT
```

### 4. SELF-RATING
```python
quality = rate_response_quality(solution)  # 0.0 to 1.0
```

---

## 🛠️ Setup

### 1. Supabase Database

Create project at [supabase.com](https://supabase.com) → SQL Editor → Run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    theme TEXT DEFAULT 'Neon',
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT,
    theme TEXT DEFAULT 'Neon',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    agent_name TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION match_memories(
    query_embedding VECTOR(1536),
    match_threshold FLOAT,
    match_count INT,
    p_user_id UUID DEFAULT NULL
)
RETURNS TABLE (id UUID, content TEXT, similarity FLOAT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT m.id, m.content, 1 - (m.embedding <=> query_embedding) AS similarity
    FROM memories m
    WHERE 1 - (m.embedding <=> query_embedding) > match_threshold
      AND (p_user_id IS NULL OR m.user_id = p_user_id)
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

CREATE INDEX idx_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_profiles_user ON user_profiles(user_id);
CREATE INDEX idx_memories_user ON memories(user_id);
```

### 2. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_API_KEY` | ✅ | Azure AI Foundry key |
| `REPLICATE_API_TOKEN` | Optional | For video generation |
| `SUPABASE_URL` | ✅ | Your Supabase URL |
| `SUPABASE_KEY` | ✅ | Supabase anon key |

### 3. Deploy to Render

```bash
git add .
git commit -m "NEURAL COUNCIL: #1 IN THE WORLD"
git push
```

Render settings:
- Build: `pip install -r requirements.txt`
- Start: `streamlit run app.py --server.port=$PORT --server.headless=true`

---

## 🧠 The Council

| Tier | Agent | Model | Role |
|------|-------|-------|------|
| 👑 | Emperor | Claude Opus 4.5 | Final Synthesis |
| 🎯 | Strategist | Claude Sonnet 4.5 | Planning + VISION |
| ⚔️ | Executor | GPT-5.2 | Implementation |
| 📿 | Sage | DeepSeek V3.2 | Critique & Approval |

---

**THE #1 AI COUNCIL AWAITS** 🧠👑
