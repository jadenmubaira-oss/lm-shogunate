"""
LM SHOGUNATE: The Pinnacle Multi-Agent AI Council
==================================================
Direct API calls to Azure AI Foundry + Gemini
"""

import os
import hashlib
import time
from typing import Generator, List, Dict, Optional, Tuple
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

# ===== CONFIGURATION =====
SESSION_BUDGET = int(os.getenv("SESSION_TOKEN_BUDGET", "20000"))
MAX_PER_CALL = int(os.getenv("MAX_TOKENS_PER_CALL", "10000"))

# ===== LAZY SUPABASE =====
_supabase_client = None

def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        try:
            from supabase import create_client
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if url and key:
                _supabase_client = create_client(url, key)
        except:
            pass
    return _supabase_client

# ===== THE COUNCIL HIERARCHY =====
AGENTS = {
    "Emperor": {
        "name": "天皇 (The Emperor)",
        "model_key": "MODEL_OPUS",
        "avatar": "👑",
        "tier": 1,
        "style": """You are THE EMPEROR, the Supreme Oracle. SYNTHESIZE the best elements and DELIVER the FINAL answer."""
    },
    "Strategist": {
        "name": "軍師 (Strategist)",
        "model_key": "MODEL_SONNET",
        "avatar": "🎯",
        "tier": 2,
        "style": """You are THE STRATEGIST. ANALYZE the problem and CREATE a battle plan."""
    },
    "Executor": {
        "name": "刀匠 (Executor)",
        "model_key": "MODEL_GPT",
        "avatar": "⚔️",
        "tier": 2,
        "style": """You are THE EXECUTOR. Write COMPLETE, PRODUCTION-READY code in markdown blocks."""
    },
    "Inquisitor": {
        "name": "審問官 (Inquisitor)",
        "model_key": "MODEL_GROK",
        "avatar": "🔍",
        "tier": 2,
        "style": """You are THE INQUISITOR. Find EVERY flaw. End with "VERDICT: APPROVED" or "VERDICT: REJECTED"."""
    },
    "Sage": {
        "name": "賢者 (Sage)",
        "model_key": "MODEL_KIMI",
        "avatar": "📿",
        "tier": 2,
        "style": """You are THE SAGE. Provide deep logical reasoning."""
    },
    "Innovator": {
        "name": "発明家 (Innovator)",
        "model_key": "MODEL_GEMINI",
        "avatar": "💡",
        "tier": 2,
        "style": """You are THE INNOVATOR. Propose UNCONVENTIONAL alternatives."""
    },
}

THEMES = {
    "Shogunate": {
        "bg": "#0a0a0a", "primary": "#c41e3a", "secondary": "#d4af37",
        "text": "#f5f5dc", "accent": "#8b0000", "glow": "#ff6b6b",
        "description": "Feudal Japan - Honor, Strategy, Power"
    },
    "Bandit Camp": {
        "bg": "#1a1410", "primary": "#8b4513", "secondary": "#a0522d",
        "text": "#deb887", "accent": "#2f1f10", "glow": "#cd853f",
        "description": "Outlaws & Rogues - Survival, Cunning, Freedom"
    },
    "Neon Tokyo": {
        "bg": "#0d0015", "primary": "#ff1493", "secondary": "#ff69b4",
        "text": "#fff0f5", "accent": "#1a0a20", "glow": "#ff00ff",
        "description": "Cyberpunk Future - Neon, Innovation, Style"
    }
}

# ===== DIRECT API CALLS =====

def call_azure_ai_foundry(deployment_name: str, messages: List[Dict], max_tokens: int = 3000) -> Tuple[str, int]:
    """Call Azure AI Foundry API with multiple endpoint formats."""
    api_key = os.getenv("AZURE_API_KEY", "")
    api_base = os.getenv("AZURE_API_BASE", "").rstrip("/")
    api_version = os.getenv("AZURE_API_VERSION", "2024-10-21")
    
    if not api_key or not api_base:
        return "⚠️ Azure: API_KEY or API_BASE not set", 0
    
    # Determine token parameter based on model type
    # GPT models need max_completion_tokens, others use max_tokens
    is_gpt = "gpt" in deployment_name.lower() or "o1" in deployment_name.lower()
    token_param = "max_completion_tokens" if is_gpt else "max_tokens"
    
    # All endpoint formats to try
    endpoints = [
        # Format 1: Azure OpenAI compatible (for Azure OpenAI deployments)
        {
            "url": f"{api_base}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}",
            "headers": {"Content-Type": "application/json", "api-key": api_key},
            "body": {"messages": messages, token_param: max_tokens, "temperature": 0.7}
        },
        # Format 2: Azure AI Model Inference (model in path)
        {
            "url": f"{api_base}/models/{deployment_name}/chat/completions",
            "headers": {"Content-Type": "application/json", "api-key": api_key, "Authorization": f"Bearer {api_key}"},
            "body": {"messages": messages, token_param: max_tokens, "temperature": 0.7}
        },
        # Format 3: Azure AI Inference (model in body)
        {
            "url": f"{api_base}/v1/chat/completions",
            "headers": {"Content-Type": "application/json", "api-key": api_key},
            "body": {"model": deployment_name, "messages": messages, token_param: max_tokens, "temperature": 0.7}
        },
    ]
    
    errors = []
    for i, ep in enumerate(endpoints):
        try:
            response = requests.post(ep["url"], headers=ep["headers"], json=ep["body"], timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", max_tokens)
                return content, tokens
            else:
                errors.append(f"[{i+1}] {response.status_code}: {response.text[:80]}")
        except Exception as e:
            errors.append(f"[{i+1}] {str(e)[:50]}")
    
    return f"⚠️ Azure failed: " + errors[0] if errors else "No endpoints tried", 0

def call_gemini(messages: List[Dict], max_tokens: int = 3000) -> Tuple[str, int]:
    """Call Google Gemini API directly."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_key:
        return "⚠️ Gemini: API key not set", 0
    if not api_key.startswith("AIza"):
        return f"⚠️ Gemini: Invalid key (starts with '{api_key[:4]}', need 'AIza')", 0
    
    # Try multiple model versions
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    for model_name in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}"
            
            contents = []
            for msg in messages:
                role = "user" if msg["role"] in ["user", "system"] else "model"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})
            
            payload = {
                "contents": contents,
                "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7}
            }
            
            response = requests.post(url, json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    return content, max_tokens
        except:
            continue
    
    return "⚠️ Gemini: All model versions failed", 0

def get_deployment_name(model_key: str) -> Optional[str]:
    value = os.getenv(model_key, "")
    for prefix in ["azure_ai/", "azure/", "gemini/"]:
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value if value else None

def call_llm(agent_key: str, messages: List[Dict], max_tokens: int = 3000) -> Tuple[str, int]:
    """Universal LLM caller - tries Azure, then Gemini."""
    agent = AGENTS.get(agent_key)
    if not agent:
        return "⚠️ Unknown agent", 0
    
    model_key = agent["model_key"]
    deployment = get_deployment_name(model_key)
    
    # For Innovator, try Gemini first
    if model_key == "MODEL_GEMINI":
        result, tokens = call_gemini(messages, max_tokens)
        if not result.startswith("⚠️"):
            return result, tokens
    
    # Try Azure
    if deployment:
        result, tokens = call_azure_ai_foundry(deployment, messages, max_tokens)
        if not result.startswith("⚠️"):
            return result, tokens
    
    # Try other Azure models
    for fb in ["claude-sonnet-4-5", "gpt-5.2-chat", "claude-opus-4-5", "grok-4-fast-reasoning"]:
        if fb != deployment:
            result, tokens = call_azure_ai_foundry(fb, messages, max_tokens)
            if not result.startswith("⚠️"):
                return result, tokens
    
    # Last resort: Gemini
    result, tokens = call_gemini(messages, max_tokens)
    if not result.startswith("⚠️"):
        return result, tokens
    
    return "⚠️ All models failed. Check Azure deployment names and API keys.", 0

# ===== TOOLS =====
def web_search(query: str) -> str:
    try:
        response = requests.get(f"https://html.duckduckgo.com/html/?q={query}", 
                               headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = [r.get_text()[:80] for r in soup.find_all('a', class_='result__a')[:5]]
        return "\n".join(f"{i+1}. {r}" for i, r in enumerate(results)) if results else "No results"
    except:
        return "Search failed"

# ===== DATABASE =====
def create_session(title: str, theme: str) -> str:
    try:
        db = get_supabase()
        if db:
            return db.table("chat_sessions").insert({"title": title, "theme": theme}).execute().data[0]["id"]
    except:
        pass
    return f"local-{hashlib.md5(f'{title}{time.time()}'.encode()).hexdigest()[:12]}"

def get_sessions() -> List[Dict]:
    try:
        db = get_supabase()
        if db:
            return db.table("chat_sessions").select("*").order("created_at", desc=True).limit(20).execute().data
    except:
        pass
    return []

def save_message(session_id: str, role: str, content: str, agent_name: str = None):
    try:
        db = get_supabase()
        if db:
            db.table("messages").insert({"session_id": session_id, "role": role, "agent_name": agent_name, "content": content}).execute()
    except:
        pass

def get_history(session_id: str) -> List[Dict]:
    try:
        db = get_supabase()
        if db:
            return db.table("messages").select("*").eq("session_id", session_id).order("created_at").execute().data
    except:
        pass
    return []

def get_embedding(text: str) -> List[float]:
    h = hashlib.sha256(text.encode()).digest()
    return [(h[i % len(h)] / 255.0) * 2 - 1 for i in range(1536)]

def save_memory(content: str):
    try:
        db = get_supabase()
        if db:
            db.table("memories").insert({"content": content, "embedding": get_embedding(content)}).execute()
    except:
        pass

def recall_memories(query: str) -> List[str]:
    try:
        db = get_supabase()
        if db:
            result = db.rpc("match_memories", {"query_embedding": get_embedding(query), "match_threshold": 0.7, "match_count": 3}).execute()
            return [m["content"] for m in result.data]
    except:
        pass
    return []

# ===== THE COUNCIL =====
def run_council(theme: str, user_input: str, session_id: str) -> Generator[Tuple[str, str, str], None, None]:
    """The Pinnacle Council Deliberation."""
    budget = SESSION_BUDGET
    
    # Web search
    if "search:" in user_input.lower():
        query = user_input.split("search:")[-1].split("\n")[0].strip()
        yield ("System", f"🔍 Searching: {query}", "system")
        user_input += f"\n\n[SEARCH]:\n{web_search(query)}"
    
    # Build context
    history = get_history(session_id)
    context = [{"role": m["role"], "content": m["content"][:600]} for m in history[-5:]]
    save_message(session_id, "user", user_input)
    context.append({"role": "user", "content": user_input})
    
    # PHASE 1: STRATEGIST
    yield ("System", "⚡ PHASE 1: Analyzing...", "system")
    strategist = AGENTS["Strategist"]
    yield ("System", f"{strategist['avatar']} Summoning {strategist['name']}...", "system")
    
    plan, tokens = call_llm("Strategist", [{"role": "system", "content": strategist["style"]}] + context, 2000)
    budget -= tokens
    save_message(session_id, "assistant", plan, strategist["name"])
    context.append({"role": "assistant", "content": plan})
    yield (strategist["name"], plan, "strategist")
    
    # PHASE 2: EXECUTOR
    yield ("System", "⚔️ PHASE 2: Executing...", "system")
    executor = AGENTS["Executor"]
    yield ("System", f"{executor['avatar']} {executor['name']} forging...", "system")
    
    code, tokens = call_llm("Executor", [{"role": "system", "content": executor["style"]}] + context, 4000)
    budget -= tokens
    save_message(session_id, "assistant", code, executor["name"])
    context.append({"role": "assistant", "content": code})
    yield (executor["name"], code, "code")
    
    # INNOVATOR
    innovator = AGENTS["Innovator"]
    yield ("System", f"{innovator['avatar']} {innovator['name']} exploring...", "system")
    alt, tokens = call_llm("Innovator", [{"role": "system", "content": innovator["style"]}] + context, 1500)
    save_message(session_id, "assistant", alt, innovator["name"])
    yield (innovator["name"], alt, "innovator")
    
    # PHASE 3: INQUISITOR
    yield ("System", "🔍 PHASE 3: Examining...", "system")
    inquisitor = AGENTS["Inquisitor"]
    approved = False
    
    critique, tokens = call_llm("Inquisitor", [{"role": "system", "content": inquisitor["style"]}] + context, 1200)
    save_message(session_id, "assistant", critique, inquisitor["name"])
    yield (inquisitor["name"], critique, "critique")
    
    if "APPROVED" in critique.upper():
        approved = True
        yield ("System", "✅ Approved", "system")
    
    # PHASE 4: EMPEROR
    yield ("System", "👑 PHASE 4: Final Judgment...", "system")
    emperor = AGENTS["Emperor"]
    yield ("System", f"{emperor['avatar']} {emperor['name']} synthesizing...", "system")
    
    verdict, tokens = call_llm("Emperor", [
        {"role": "system", "content": emperor["style"]},
        {"role": "user", "content": f"PLAN: {plan[:500]}\nCODE: {code[:1000]}\nCRITIQUE: {critique[:300]}\n\nDeliver the FINAL answer."}
    ], 4000)
    save_message(session_id, "assistant", verdict, emperor["name"])
    yield (emperor["name"], verdict, "emperor")
    
    if approved:
        save_memory(f"SUCCESS: {user_input[:100]} -> {verdict[:200]}")
        yield ("System", "📖 Archived", "system")
    
    yield ("System", f"🏯 Complete.", "system")
