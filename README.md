# 🏯 LM SHOGUNATE

## The Ultimate Multi-User AI Council

4 AI models working together. Multi-user support. Screen capture. Works anywhere.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **4 AI Models** | Claude Opus 4.5, Sonnet 4.5, GPT-5.2, DeepSeek V3.2 |
| 👥 **Multi-User** | Email/password registration & login |
| 🔒 **Per-User Data** | Each user has private sessions & memories |
| 📸 **Screen Capture** | Capture and share screen (desktop) |
| 🎨 **Image Generation** | DALL-E 3 |
| 🎬 **Video Generation** | Kling v2.5 |
| 🔍 **Web Search** | DuckDuckGo |
| 📱 **Mobile Ready** | Responsive design |

---

## 🚀 Setup

### 1. Supabase Database

Go to [supabase.com](https://supabase.com) → Create project → SQL Editor → Run:

```sql
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- User profiles (for theme preferences)
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    theme TEXT DEFAULT 'Shogunate',
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Chat sessions (per user)
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT,
    theme TEXT DEFAULT 'Shogunate',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    agent_name TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Memories (per user)
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Memory search (updated for user filtering)
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

-- Indexes
CREATE INDEX idx_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_profiles_user ON user_profiles(user_id);
CREATE INDEX idx_memories_user ON memories(user_id);
```

### 2. Enable Supabase Auth

In Supabase Dashboard:
1. Go to **Authentication** → **Providers**
2. Enable **Email** provider
3. (Optional) Disable email confirmation for faster testing

### 3. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_API_KEY` | ✅ | Azure AI Foundry key |
| `REPLICATE_API_TOKEN` | Optional | For video generation |
| `SUPABASE_URL` | ✅ | Your Supabase URL |
| `SUPABASE_KEY` | ✅ | Supabase anon key |

### 4. Deploy to Render

1. Fork repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect repo
4. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `streamlit run app.py --server.port=$PORT --server.headless=true`
5. Add environment variables
6. Deploy

---

## 🎮 Usage

### Commands

| Command | Example |
|---------|---------|
| Normal | `Write a Python web scraper` |
| Search | `search: AI news 2025` |
| Image | `image: samurai in rain` |
| Video | `video: wolf running` |

### Screen Capture (Desktop)

1. Click "📸 Screen Capture" expander
2. Click "Capture Screen" button
3. Select window/screen to share
4. Screenshot attaches to next message

---

## 👥 Multi-User

Each user:
- Has separate login
- Sees only their sessions
- Has private memories
- Theme preferences saved

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

**THE COUNCIL AWAITS** 👑
