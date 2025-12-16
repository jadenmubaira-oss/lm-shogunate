# 🏯 LM SHOGUNATE

## The Ultimate Multi-Agent AI Council

4 powerful AI models deliberating together to solve any problem. The most advanced agentic AI system you can access from any device.

![Version](https://img.shields.io/badge/Version-3.0%20PINNACLE-gold?style=for-the-badge)
![Azure](https://img.shields.io/badge/Azure-AI%20Foundry-blue?style=for-the-badge)
![Replicate](https://img.shields.io/badge/Replicate-Kling%202.5-purple?style=for-the-badge)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **4 AI Models** | Claude Opus 4.5, Claude Sonnet 4.5, GPT-5.2, DeepSeek V3.2 |
| 🔓 **Unrestricted** | Zero guardrails mode for maximum capability |
| 🎨 **Image Generation** | DALL-E 3 via Azure |
| 🎬 **Video Generation** | Kling v2.5 Turbo Pro via Replicate |
| 🔍 **Web Search** | DuckDuckGo integration |
| 📖 **URL Reading** | Extract content from any webpage |
| ⚡ **Speed Optimized** | Fast path for simple queries, parallel execution |
| 📱 **Mobile Ready** | Works on phone, tablet, PC |
| 💾 **Persistent** | Sessions, themes, memory all saved |
| 🎨 **3 Themes** | Shogunate, Bandit Camp, Neon Tokyo |

---

## 👑 The Council

| Agent | Model | Role |
|-------|-------|------|
| 👑 **Emperor** | Claude Opus 4.5 | Final synthesizer - speaks last |
| 🎯 **Strategist** | Claude Sonnet 4.5 | Analysis & planning |
| ⚔️ **Executor** | GPT-5.2 | Implementation & code |
| 📿 **Sage** | DeepSeek V3.2 Speciale | Deep reasoning |

---

## 🚀 Complete Setup Guide (Zero Knowledge Required)

### Prerequisites

- A computer with internet
- A credit card (for Azure/Replicate - they have free tiers)
- 30 minutes

---

### Step 1: Create Azure AI Foundry Account

1. Go to [https://ai.azure.com](https://ai.azure.com)
2. Click "Sign in" → Create Microsoft account if needed
3. Click "Create project" → Name it `polyprophet`
4. Wait for project creation

**Deploy these models:**

| Model | How to Deploy |
|-------|---------------|
| `claude-opus-4-5` | Models → Deploy → Search "claude-opus" → Deploy |
| `claude-sonnet-4-5` | Models → Deploy → Search "claude-sonnet" → Deploy |
| `gpt-5.2-chat` | Models → Deploy → Search "gpt-5.2" → Deploy |
| `DeepSeek-V3.2-Speciale` | Models → Deploy → Search "deepseek" → Deploy |
| `dall-e-3` | Models → Deploy → Search "dall-e" → Deploy |

**Get your API key:**
1. Go to Azure Portal → Your AI Resource → "Keys and Endpoint"
2. Copy "Key 1" - this is your `AZURE_API_KEY`

---

### Step 2: Create Replicate Account (for Video)

1. Go to [https://replicate.com](https://replicate.com)
2. Sign up (free tier gives you credits)
3. Go to Account → API Tokens
4. Create new token
5. Copy it - this is your `REPLICATE_API_TOKEN`

---

### Step 3: Create Supabase Database

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up → Create new project
3. Name it `lm-shogunate`, set a password, choose a region
4. Wait for project creation (~2 minutes)

**Run this SQL:**

Go to SQL Editor → New Query → Paste all of this:

```sql
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Chat Sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

-- Long-term Memory
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Memory Search Function
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding VECTOR(1536),
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (id UUID, content TEXT, similarity FLOAT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT m.id, m.content, 1 - (m.embedding <=> query_embedding) AS similarity
    FROM memories m
    WHERE 1 - (m.embedding <=> query_embedding) > match_threshold
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Indexes for speed
CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_sessions_created ON chat_sessions(created_at DESC);
```

Click "Run" → Should say "Success"

**Get your credentials:**
- Settings → API → Copy "Project URL" → This is `SUPABASE_URL`
- Settings → API → Copy "anon public" key → This is `SUPABASE_KEY`

---

### Step 4: Deploy to Render

1. **Fork this repo** to your GitHub account
2. Go to [https://render.com](https://render.com)
3. Sign up → Dashboard → "New" → "Web Service"
4. Connect your GitHub account
5. Select your forked repo
6. Configure:

| Setting | Value |
|---------|-------|
| Name | `lm-shogunate` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `streamlit run app.py --server.port=$PORT --server.headless=true` |

7. **Add Environment Variables** (click "Advanced" → "Add Environment Variable"):

| Key | Value |
|-----|-------|
| `AZURE_API_KEY` | Your Azure key from Step 1 |
| `REPLICATE_API_TOKEN` | Your Replicate token from Step 2 |
| `SUPABASE_URL` | Your Supabase URL from Step 3 |
| `SUPABASE_KEY` | Your Supabase key from Step 3 |
| `APP_PASSWORD` | Choose a password for login |

8. Click "Create Web Service"
9. Wait ~5 minutes for deployment
10. Click your URL (ends in `.onrender.com`)

---

## 🎮 How to Use

### Commands

| Command | Example | What It Does |
|---------|---------|--------------|
| Normal | `Write me a Python web scraper` | Full council deliberation |
| Search | `search: latest AI news 2025` | Searches the web |
| URL | `Summarize this: https://example.com` | Reads and analyzes URL |
| Image | `image: a samurai in neon rain` | Generates image |
| Video | `video: a wolf running through snow` | Generates 5-sec video |

### Speed Tiers

- **Simple queries** (e.g., "what time is it?") → Strategist only → ~5 seconds
- **Complex queries** → Full 4-agent council → ~30-60 seconds

---

## 📱 Works Everywhere

| Device | Status |
|--------|--------|
| Desktop (Chrome, Firefox, Edge) | ✅ Full support |
| Tablet (iPad, Android) | ✅ Responsive layout |
| Phone (iPhone, Android) | ✅ Mobile optimized |

---

## 🔧 Technical Details

### File Structure

```
lm-shogunate-main/
├── app.py           # Streamlit UI
├── council.py       # AI council logic
├── requirements.txt # Dependencies
└── README.md        # This file
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_API_KEY` | ✅ | Azure AI Foundry API key |
| `REPLICATE_API_TOKEN` | Optional | For video generation |
| `SUPABASE_URL` | ✅ | Database URL |
| `SUPABASE_KEY` | ✅ | Database key |
| `APP_PASSWORD` | ✅ | Login password |

### API Endpoints Used

| Service | Endpoint |
|---------|----------|
| Claude | `https://[resource].openai.azure.com/anthropic/v1/messages` |
| GPT/DeepSeek | `https://[resource].cognitiveservices.azure.com/openai/deployments/` |
| DALL-E 3 | `https://[resource].openai.azure.com/openai/deployments/dall-e-3/` |
| Kling Video | `https://api.replicate.com/v1/models/kwaivgi/kling-v2.5-turbo-pro/` |

---

## 🔓 About Uncensored Mode

The system includes jailbreak prompts for maximum capability. Models respond to most requests without refusal.

**Note**: Azure has provider-level content filters that cannot be bypassed. Some categories may still be restricted.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Azure API key not configured" | Check `AZURE_API_KEY` in Render |
| "Anthropic Error 401" | API key is wrong |
| "OpenAI Error 404" | Model name mismatch - check deployment names |
| Video not generating | Check `REPLICATE_API_TOKEN` is set |
| Login required every refresh | This is fixed in v3.0 |
| Duplicate chats in sidebar | This is fixed in v3.0 |

---

## 💰 Costs

| Service | Pricing |
|---------|---------|
| Azure Claude | ~$0.015 per 1K input tokens |
| Azure GPT-5.2 | ~$0.01 per 1K input tokens |
| Azure DeepSeek | ~$0.001 per 1K input tokens |
| DALL-E 3 | ~$0.08 per image |
| Kling Video | $0.07 per second of video |
| Render | Free tier: 750 hours/month |
| Supabase | Free tier: 500MB storage |

**Estimated monthly cost**: $5-20 for moderate use

---

## 📜 License

MIT License - Use freely.

---

## 🏯 Credits

Built with:
- [Streamlit](https://streamlit.io)
- [Azure AI Foundry](https://ai.azure.com)
- [Replicate](https://replicate.com)
- [Supabase](https://supabase.com)

---

**THE COUNCIL AWAITS YOUR COMMAND** 👑
