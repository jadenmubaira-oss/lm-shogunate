# 🏯 LM SHOGUNATE: The Pinnacle Multi-Agent AI Council

> **A unified ensemble of the world's most advanced AI models working together as a self-improving superintelligence.**

When you ask a question, it's not answered by one AI — it's deliberated by a **council of 6 AI Lords**, each with distinct capabilities, who debate, critique, refine, and converge on the optimal solution.

## 👑 The Council Hierarchy

| Tier | Agent | Model | Role | Description |
|------|-------|-------|------|-------------|
| **1** | 天皇 (Emperor) | **Claude Opus 4.5** | Supreme Oracle | **THE SMARTEST MODEL** - Speaks LAST, makes FINAL decisions, resolves disputes |
| **2** | 軍師 (Strategist) | Claude Sonnet 4.5 | Planner | Analyzes problems, designs architecture, creates battle plans |
| **2** | 刀匠 (Executor) | GPT-5.2 | Coder | Implements production-ready code with precision |
| **2** | 審問官 (Inquisitor) | Grok 4 | Critic | Ruthlessly examines code, finds every flaw |
| **2** | 賢者 (Sage) | Kimi K2 | Reasoner | Deep logical reasoning, mathematical proofs |
| **2** | 発明家 (Innovator) | Gemini 2.0 | Creative | Unconventional approaches, out-of-box thinking |

## ⚡ How It Works

```
USER QUERY
    ↓
┌─────────────────────────────────────────────┐
│ PHASE 1: UNDERSTANDING                       │
│  • Strategist analyzes the problem           │
│  • Sage identifies logical constraints       │
│  • Memory recalls relevant past solutions    │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ PHASE 2: EXECUTION                           │
│  • Executor writes the primary solution      │
│  • Innovator proposes alternatives           │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ PHASE 3: CRITIQUE (Auto-fix loop x3)        │
│  • Inquisitor examines the code              │
│  • If REJECTED → Executor auto-fixes         │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ PHASE 4: SUPREME JUDGMENT                    │
│  👑 THE EMPEROR (Opus 4.5)                   │
│  • Receives ALL prior outputs                │
│  • Synthesizes the best elements             │
│  • Delivers the FINAL, authoritative answer  │
└─────────────────────────────────────────────┘
    ↓
UNIFIED RESPONSE
```

## 🎨 Themes

Switch between three immersive aesthetic eras:

- **⚔️ Shogunate**: Feudal Japan — Honor, Strategy, Power
- **🪓 Bandit Camp**: Outlaws & Rogues — Survival, Cunning, Freedom  
- **🌃 Neon Tokyo**: Cyberpunk Future — Neon, Innovation, Style

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Multi-Model Council** | 6 frontier AI models collaborating |
| **Opus as Emperor** | Smartest model makes final decisions |
| **Auto-Fix Loop** | Self-correcting code with 3 retry cycles |
| **Web Search** | Type `search: query` to search the web |
| **URL Reading** | Paste URLs to analyze web content |
| **File Upload** | Analyze PDFs, code files, documents |
| **Vector Memory** | Semantic recall of past solutions |
| **Theme System** | Three immersive visual themes |
| **Mobile-Ready** | Fully responsive design |

## 📋 Environment Variables

```env
# === AZURE AI FOUNDRY ===
AZURE_API_KEY=your_azure_key
AZURE_API_BASE=https://your-resource.services.ai.azure.com
AZURE_API_VERSION=2024-10-21

# === GOOGLE GEMINI ===
GEMINI_API_KEY=your_gemini_key

# === SUPABASE (Memory) ===
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# === APP ===
APP_PASSWORD=shogun2024

# === MODEL MAPPING ===
MODEL_OPUS=azure/claude-opus-4-5
MODEL_SONNET=azure/claude-sonnet-4-5
MODEL_GPT=azure/gpt-5.2-chat
MODEL_GROK=azure/grok-4-fast-reasoning
MODEL_KIMI=azure/Kimi-K2-Thinking
MODEL_HAIKU=azure/claude-haiku-4-5
MODEL_GEMINI=gemini/gemini-2.0-flash-exp

# === BUDGET ===
SESSION_TOKEN_BUDGET=15000
MAX_TOKENS_PER_CALL=4000
```

## 🗄️ Supabase Schema

Run this in your Supabase SQL Editor:

```sql
-- Enable vector extension
create extension if not exists vector;

-- Chat sessions
create table chat_sessions (
  id uuid default gen_random_uuid() primary key,
  created_at timestamptz default now(),
  title text not null,
  theme text default 'Shogunate'
);

-- Messages
create table messages (
  id bigserial primary key,
  session_id uuid references chat_sessions(id) on delete cascade,
  role text not null,
  agent_name text,
  content text not null,
  created_at timestamptz default now()
);

-- Long-term memory
create table memories (
  id bigserial primary key,
  content text not null,
  embedding vector(1536),
  created_at timestamptz default now()
);

-- Memory search function
create or replace function match_memories(
  query_embedding vector(1536),
  match_threshold float default 0.7,
  match_count int default 3
) returns table (id bigint, content text, similarity float)
language plpgsql as $$
begin
  return query
  select memories.id, memories.content,
         1 - (memories.embedding <=> query_embedding) as similarity
  from memories
  where 1 - (memories.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
end;
$$;
```

## 🌐 Deploy to Render

1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your repository
4. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
5. Add all environment variables
6. Click "Manual Deploy" → "Clear build cache & deploy"

## 💡 Usage

- **Basic Query**: Just type your question
- **Web Search**: `search: latest AI news`
- **URL Analysis**: Paste any URL in your message
- **File Upload**: Click the upload button to attach files

## 🏆 Why This Is The Pinnacle

1. **Opus 4.5 as Emperor**: The smartest model doesn't waste tokens on first drafts — it receives ALL context and makes the FINAL call
2. **Specialization**: Each model does what it's best at
3. **Self-Correcting**: Auto-fix loop with ruthless critics
4. **Dispute Resolution**: When agents disagree, the Emperor arbitrates
5. **Memory**: Learns from every successful solution
6. **Immersive Design**: Theme system makes it engaging

---

*Built with 🏯 for the AI Council*
