# 🧠 NEURAL COUNCIL

## The True Pinnacle Multi-Agent AI

4 AI models collaborating, debating, and refining each other's work.

---

## ✨ Revolutionary Features

| Feature | Description |
|---------|-------------|
| 🧠 **4 AI Models** | Claude Opus 4.5, Sonnet 4.5, GPT-5.2, DeepSeek V3.2 |
| 🔄 **Multi-Round Refinement** | Loops until Sage APPROVES (up to 3 rounds) |
| 💭 **Debate Mode** | Agents challenge each other's proposals |
| 📊 **Dynamic Routing** | Query classification for optimal processing |
| 📈 **Confidence Scoring** | Every response rated for confidence |
| 👥 **Multi-User** | Email/password auth, per-user data |
| 🎨 **Image Generation** | DALL-E 3 via natural language |
| 🎬 **Video Generation** | Kling v2.5 via natural language |
| 🔍 **Web Search** | DuckDuckGo integration |
| 📸 **Screen Capture** | Share your screen (desktop) |

---

## 🚀 The Revolutionary Architecture

```
Query Input
    ↓
📊 CLASSIFY (code/creative/research/reasoning)
    ↓
🎯 STRATEGIST (analysis & plan)
    ↓
💭 DEBATE MODE? ─────────────────┐
    ↓ No                         ↓ Yes
⚔️📿 PARALLEL                   ⚔️ PROPOSAL
(Executor + Sage)               📿 CHALLENGE
    ↓                           ⚔️ RESPONSE
    ├───────────────────────────┘
    ↓
🔄 MULTI-ROUND REFINEMENT
    WHILE !sage_approves AND rounds < 3:
        ⚔️ Executor FIXES
        📿 Sage RE-REVIEWS
    ↓
📈 CONFIDENCE CHECK (0-100%)
    ↓
👑 EMPEROR SYNTHESIS (final perfect answer)
```

---

## 🔥 What Makes This Revolutionary

### 1. Multi-Round Refinement Loop
```python
while not sage_approves(reasoning) and round_num < 3:
    solution = executor_fixes(issues)
    reasoning = sage_reviews(solution)
    # Loops until Sage says "APPROVED" or "LGTM"
```

### 2. Debate Mode
For complex queries, agents actively challenge each other:
- **Executor proposes** a solution
- **Sage challenges** "What's wrong? What's better?"
- **Executor responds** and improves

### 3. Query Classification
```
'code'      → GPT-5.2 prioritized
'creative'  → Claude prioritized  
'reasoning' → DeepSeek prioritized
```

### 4. Confidence Scoring
Every response includes confidence level: `📈 Solution confidence: 85%`

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

### 2. Enable Supabase Auth

In Supabase Dashboard:
1. **Authentication** → **Providers**
2. Enable **Email** provider

### 3. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_API_KEY` | ✅ | Azure AI Foundry key |
| `REPLICATE_API_TOKEN` | Optional | For video generation |
| `SUPABASE_URL` | ✅ | Your Supabase URL |
| `SUPABASE_KEY` | ✅ | Supabase anon key |

### 4. Deploy to Render

1. Push to GitHub
2. [render.com](https://render.com) → New Web Service
3. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `streamlit run app.py --server.port=$PORT --server.headless=true`
4. Add environment variables
5. Deploy

---

## 🎮 Commands

| Command | Example |
|---------|---------|
| Normal | `Write a Python web scraper` |
| Search | `search: AI news 2025` |
| Image | `image: sunset over mountains` |
| Video | `video: waves crashing` |
| Natural | `create an image of a robot` |
| Natural | `make a video of a dog running` |

---

## 🧠 The Council

| Tier | Agent | Model | Role |
|------|-------|-------|------|
| 👑 | Emperor | Claude Opus 4.5 | Final Synthesis |
| 🎯 | Strategist | Claude Sonnet 4.5 | Planning |
| ⚔️ | Executor | GPT-5.2 | Implementation |
| 📿 | Sage | DeepSeek V3.2 | Critique & Verification |

---

## 💰 Costs

| Service | Cost |
|---------|------|
| Azure Claude | ~$0.015/1K tokens |
| DALL-E 3 | ~$0.08/image |
| Kling Video | $0.07/sec |
| Render | Free tier |
| Supabase | Free tier |

---

**THE COUNCIL AWAITS** 🧠
