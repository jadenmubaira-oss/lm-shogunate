import os
import json
from typing import Generator, List, Dict
from dotenv import load_dotenv
from litellm import completion, embedding
from supabase import create_client, Client
import requests
from bs4 import BeautifulSoup

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ===== THEME DEFINITIONS =====
THEMES = {
    "Shogunate": {
        "bg": "#0a0a0a",
        "primary": "#c41e3a",
        "secondary": "#d4af37",
        "text": "#f5f5dc",
        "accent": "#8b0000",
        "personas": {
            "Architect": {"name": "大将軍", "model": "MODEL_OPUS", "avatar": "⚔️", "style": "Supreme Commander. Ancient wisdom. Plan strategy."},
            "Coder": {"name": "刀鍛冶", "model": "MODEL_OPUS", "avatar": "🔨", "style": "Master craftsman. Elegant code with Japanese comments."},
            "Critic": {"name": "奉行", "model": "MODEL_GROK", "avatar": "⚖️", "style": "Ruthless judge. Find every flaw. Say APPROVED or REJECTED."},
            "Wildcard": {"name": "浪人", "model": "MODEL_GEMINI", "avatar": "🌸", "style": "Masterless samurai. Unconventional solutions."}
        }
    },
    "Bandit Camp": {
        "bg": "#1a1410",
        "primary": "#654321",
        "secondary": "#8b7355",
        "text": "#d2b48c",
        "accent": "#2f1f10",
        "personas": {
            "Architect": {"name": "Warlord", "model": "MODEL_OPUS", "avatar": "🪓", "style": "Survivalist. Aggressive raid planning."},
            "Coder": {"name": "Scavenger", "model": "MODEL_OPUS", "avatar": "🔧", "style": "Function over form. Make it work."},
            "Critic": {"name": "Scout", "model": "MODEL_GROK", "avatar": "🔭", "style": "Paranoid. Check for traps."},
            "Wildcard": {"name": "Mystic", "model": "MODEL_GEMINI", "avatar": "🔮", "style": "Cryptic visions. See patterns."}
        }
    },
    "Neon Tokyo": {
        "bg": "#1b0036",
        "primary": "#ff4da6",
        "secondary": "#ff9ad9",
        "text": "#fff0f6",
        "accent": "#ff66b2",
        "personas": {
            "Architect": {"name": "Synth-Lord", "model": "MODEL_OPUS", "avatar": "🌃", "style": "A E S T H E T I C. Vaporwave vibes."},
            "Coder": {"name": "Net-Runner", "model": "MODEL_OPUS", "avatar": "💾", "style": "Cyberpunk hacker. L33t comments."},
            "Critic": {"name": "System-Admin", "model": "MODEL_GROK", "avatar": "🤖", "style": "Cold logic. Zero inefficiency."},
            "Wildcard": {"name": "Glitch", "model": "MODEL_GEMINI", "avatar": "✨", "style": "Chaotic art. Beauty in errors."}
        }
    }
}

# ===== HELPER FUNCTIONS =====
def get_model_name(key: str) -> str:
    return os.getenv(key)

def count_tokens(text: str) -> int:
    return max(1, len(text) // 4)

SESSION_BUDGET = int(os.getenv("SESSION_TOKEN_BUDGET", "8000"))
MAX_PER_CALL = int(os.getenv("MAX_TOKENS_PER_CALL", "4000"))

FALLBACK = {
    "Architect": ["MODEL_OPUS", "MODEL_GPT", "MODEL_SONNET"],
    "Coder": ["MODEL_OPUS", "MODEL_GPT", "MODEL_SONNET"],
    "Critic": ["MODEL_GROK", "MODEL_SONNET", "MODEL_GPT"],
    "Wildcard": ["MODEL_GEMINI", "MODEL_SONNET"]
}

def resolve_model(role: str, budget: int) -> str:
    if budget < 800:
        return os.getenv("MODEL_GEMINI") or os.getenv("MODEL_HAIKU")
    for k in FALLBACK.get(role, []):
        if os.getenv(k):
            return os.getenv(k)
    return os.getenv("MODEL_GPT")

def call_model(model: str, messages: List[Dict], max_tokens: int = 3000, budget: int = None) -> tuple:
    try:
        if model.startswith("MODEL_"):
            model = os.getenv(model)
        allowed = min(max_tokens, MAX_PER_CALL, budget or 9999)
        response = completion(
            model=model,
            messages=messages,
            max_tokens=allowed,
            temperature=0.7,
            api_key=os.getenv("AZURE_API_KEY"),
            api_base=os.getenv("AZURE_API_BASE"),
            api_version=os.getenv("AZURE_API_VERSION", "2024-10-21")
        )
        content = response.choices[0].message.content
        return content, allowed
    except Exception as e:
        return f"⚠️ ERROR: {str(e)}", 0

# ===== WEB SEARCH =====
def web_search(query: str) -> str:
    try:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for result in soup.find_all('a', class_='result__a')[:3]:
            results.append(f"- {result.get_text()}: {result.get('href')}")
        return "\n".join(results) if results else "No results"
    except:
        return "Search failed"

# ===== DATABASE =====
def create_session(title: str, theme: str) -> str:
    result = supabase.table("chat_sessions").insert({"title": title, "theme": theme}).execute()
    return result.data[0]["id"]

def get_sessions() -> List[Dict]:
    result = supabase.table("chat_sessions").select("*").order("created_at", desc=True).limit(20).execute()
    return result.data

def save_message(session_id: str, role: str, content: str, agent_name: str = None):
    supabase.table("messages").insert({
        "session_id": session_id,
        "role": role,
        "agent_name": agent_name,
        "content": content
    }).execute()

def get_history(session_id: str) -> List[Dict]:
    result = supabase.table("messages").select("*").eq("session_id", session_id).order("created_at").execute()
    return result.data

def save_memory(content: str, embedding_vec: List[float]):
    supabase.table("memories").insert({"content": content, "embedding": embedding_vec}).execute()

def recall_memories(query_embedding: List[float]) -> List[str]:
    try:
        result = supabase.rpc("match_memories", {
            "query_embedding": query_embedding,
            "match_threshold": 0.75,
            "match_count": 3
        }).execute()
        return [m["content"] for m in result.data]
    except:
        return []

def get_embedding(text: str) -> List[float]:
    model = os.getenv("MODEL_EMBEDDING")
    if model:
        try:
            resp = embedding(
                model=model,
                input=[text],
                api_key=os.getenv("AZURE_API_KEY"),
                api_base=os.getenv("AZURE_API_BASE"),
                api_version=os.getenv("AZURE_API_VERSION", "2024-10-21")
            )
            return resp.data[0]["embedding"]
        except:
            pass
    # Deterministic fallback
    import hashlib
    h = hashlib.sha256(text.encode()).digest()
    return [(h[i % len(h)] / 255.0) * 2 - 1 for i in range(1536)]

# ===== THE COUNCIL =====
def run_council(theme: str, user_input: str, session_id: str) -> Generator[tuple, None, None]:
    personas = THEMES[theme]["personas"]
    history = get_history(session_id)
    budget = SESSION_BUDGET
    
    # Check for web search request
    if "search:" in user_input.lower():
        query = user_input.split("search:")[-1].strip()
        search_results = web_search(query)
        user_input += f"\n\n[WEB SEARCH RESULTS]:\n{search_results}"
    
    api_history = []
    for msg in history[-10:]:
        api_history.append({
            "role": msg["role"],
            "content": f"[{msg.get('agent_name', 'User')}]: {msg['content']}"
        })
    
    save_message(session_id, "user", user_input)
    api_history.append({"role": "user", "content": user_input})
    
    # Recall memories
    query_emb = get_embedding(user_input)
    memories = recall_memories(query_emb)
    if memories:
        memory_context = "\n[ARCHIVES]:\n" + "\n".join(memories)
        api_history.append({"role": "system", "content": memory_context})
        yield ("System", f"📜 Recalled {len(memories)} memories", "system")
    
    # PHASE 1: ARCHITECT
    arch = personas["Architect"]
    yield ("System", f"{arch['avatar']} Summoning {arch['name']}...", "system")
    model = resolve_model("Architect", budget) or get_model_name(arch["model"])
    plan, used = call_model(model, [{"role": "system", "content": arch["style"]}] + api_history, 2000, budget)
    budget -= used
    save_message(session_id, "assistant", plan, arch["name"])
    api_history.append({"role": "assistant", "content": f"[{arch['name']}]: {plan}"})
    yield (arch["name"], plan, "architect")
    
    # PHASE 2: CODER
    coder = personas["Coder"]
    yield ("System", f"{coder['avatar']} {coder['name']} forging...", "system")
    model = resolve_model("Coder", budget) or get_model_name(coder["model"])
    code, used = call_model(model, [{"role": "system", "content": coder["style"] + "\nOutput code in markdown blocks."}] + api_history, 3500, budget)
    budget -= used
    save_message(session_id, "assistant", code, coder["name"])
    api_history.append({"role": "assistant", "content": f"[{coder['name']}]: {code}"})
    yield (coder["name"], code, "code")
    
    # PHASE 3: CRITIC (auto-fix loop)
    critic = personas["Critic"]
    for attempt in range(3):
        yield ("System", f"{critic['avatar']} {critic['name']} examining...", "system")
        model = resolve_model("Critic", budget) or get_model_name(critic["model"])
        critique, used = call_model(model, [{"role": "system", "content": critic["style"] + "\nMUST end with APPROVED or REJECTED."}] + api_history, 1000, budget)
        budget -= used
        save_message(session_id, "assistant", critique, critic["name"])
        api_history.append({"role": "assistant", "content": f"[{critic['name']}]: {critique}"})
        yield (critic["name"], critique, "critique")
        
        if "APPROVED" in critique.upper():
            memory_text = f"SUCCESS: {user_input}\n\nPLAN:\n{plan[:500]}\n\nCODE:\n{code[:1000]}"
            save_memory(memory_text, get_embedding(memory_text))
            yield ("System", "✅ Approved & archived", "system")
            break
        
        if "REJECTED" in critique.upper() and attempt < 2:
            yield ("System", f"⚠️ Flaw detected. Retry {attempt + 2}/3", "system")
            fix_prompt = f"Previous code rejected:\n{critique}\n\nFix and rewrite complete solution."
            api_history.append({"role": "user", "content": fix_prompt})
            code, used = call_model(resolve_model("Coder", budget) or get_model_name(coder["model"]), [{"role": "system", "content": coder["style"]}] + api_history, 3500, budget)
            budget -= used
            save_message(session_id, "assistant", code, f"{coder['name']} (Fixed)")
            api_history.append({"role": "assistant", "content": f"[{coder['name']} FIX]: {code}"})
            yield (f"{coder['name']} (Fix {attempt + 2})", code, "code")
    
    # PHASE 4: WILDCARD
    wild = personas["Wildcard"]
    yield ("System", f"{wild['avatar']} {wild['name']} offering alternative...", "system")
    model = resolve_model("Wildcard", budget) or get_model_name(wild["model"])
    alt, used = call_model(model, [{"role": "system", "content": wild["style"] + "\nOffer completely different approach."}] + api_history, 2000, budget)
    save_message(session_id, "assistant", alt, wild["name"])
    yield (wild["name"], alt, "wildcard")
