"""
LM SHOGUNATE: The Pinnacle Multi-Agent AI Council
==================================================
Direct API calls to Azure AI Foundry + Gemini
"""

import os
import hashlib
import time
import json
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
        "style": """You are THE EMPEROR, the Supreme Oracle. You have received all council deliberations.
SYNTHESIZE the best elements, RESOLVE disputes, and DELIVER the FINAL answer. Your word is LAW."""
    },
    "Strategist": {
        "name": "軍師 (Strategist)",
        "model_key": "MODEL_SONNET",
        "avatar": "🎯",
        "tier": 2,
        "style": """You are THE STRATEGIST. ANALYZE the problem, DESIGN the architecture, CREATE a battle plan."""
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
        "style": """You are THE SAGE. Provide deep logical reasoning and analysis."""
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
    """
    Call Azure AI Foundry API directly.
    Tries multiple endpoint formats for compatibility.
    """
    api_key = os.getenv("AZURE_API_KEY")
    api_base = os.getenv("AZURE_API_BASE", "").rstrip("/")
    
    if not api_key or not api_base:
        return "⚠️ Azure API not configured", 0
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,  # Azure uses api-key header
        "Authorization": f"Bearer {api_key}"  # Also try Bearer token
    }
    
    payload = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    # Try different endpoint formats
    endpoints_to_try = [
        # Format 1: Model in URL path (Azure AI Foundry standard)
        (f"{api_base}/openai/deployments/{deployment_name}/chat/completions?api-version=2024-10-21", 
         {**payload}),
        # Format 2: Model in body (Azure AI Inference)
        (f"{api_base}/models/chat/completions?api-version=2024-05-01-preview", 
         {**payload, "model": deployment_name}),
        # Format 3: Direct model endpoint
        (f"{api_base}/chat/completions?api-version=2024-10-21", 
         {**payload, "model": deployment_name}),
    ]
    
    last_error = ""
    for url, body in endpoints_to_try:
        try:
            response = requests.post(url, headers=headers, json=body, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", max_tokens)
                return content, tokens
            else:
                last_error = f"{response.status_code}: {response.text[:200]}"
        except Exception as e:
            last_error = str(e)
    
    return f"⚠️ Azure Error: {last_error}", 0

def call_gemini(messages: List[Dict], max_tokens: int = 3000) -> Tuple[str, int]:
    """Call Google Gemini API directly."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    # Validate API key format (should start with AIza)
    if not api_key or not api_key.startswith("AIza"):
        return "⚠️ Gemini API key invalid (should start with AIza)", 0
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.7
            }
        }
        
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return content, max_tokens
        else:
            return f"⚠️ Gemini Error: {response.status_code}", 0
            
    except Exception as e:
        return f"⚠️ Gemini Exception: {str(e)}", 0

def get_deployment_name(model_key: str) -> Optional[str]:
    """Extract deployment name from MODEL_XXX env var."""
    value = os.getenv(model_key, "")
    # Remove any prefix
    for prefix in ["azure_ai/", "azure/", "gemini/"]:
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value if value else None

def call_llm(agent_key: str, messages: List[Dict], max_tokens: int = 3000) -> Tuple[str, int]:
    """Universal LLM caller - tries Azure first, then Gemini fallback."""
    agent = AGENTS.get(agent_key)
    if not agent:
        return "⚠️ Unknown agent", 0
    
    model_key = agent["model_key"]
    deployment = get_deployment_name(model_key)
    
    # For Innovator, prefer Gemini
    if model_key == "MODEL_GEMINI":
        result, tokens = call_gemini(messages, max_tokens)
        if not result.startswith("⚠️"):
            return result, tokens
    
    # Try Azure AI Foundry
    if deployment:
        result, tokens = call_azure_ai_foundry(deployment, messages, max_tokens)
        if not result.startswith("⚠️"):
            return result, tokens
    
    # Try other Azure models as fallback
    fallback_models = ["claude-sonnet-4-5", "claude-opus-4-5", "gpt-5.2-chat", "grok-4-fast-reasoning"]
    for fb in fallback_models:
        if fb != deployment:
            result, tokens = call_azure_ai_foundry(fb, messages, max_tokens)
            if not result.startswith("⚠️"):
                return result, tokens
    
    # Last resort: Gemini
    result, tokens = call_gemini(messages, max_tokens)
    if not result.startswith("⚠️"):
        return result, tokens
    
    return f"⚠️ All models failed. Check API keys and endpoints.", 0

# ===== TOOLS =====
def web_search(query: str) -> str:
    try:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = [r.get_text()[:100] for r in soup.find_all('a', class_='result__a')[:5]]
        return "\n".join(f"{i+1}. {r}" for i, r in enumerate(results)) if results else "No results"
    except:
        return "Search failed"

# ===== DATABASE =====
def create_session(title: str, theme: str) -> str:
    try:
        db = get_supabase()
        if db:
            result = db.table("chat_sessions").insert({"title": title, "theme": theme}).execute()
            return result.data[0]["id"]
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
        user_input += f"\n\n[SEARCH RESULTS]:\n{web_search(query)}"
    
    # Build context
    history = get_history(session_id)
    context = [{"role": m["role"], "content": m["content"][:800]} for m in history[-6:]]
    
    save_message(session_id, "user", user_input)
    context.append({"role": "user", "content": user_input})
    
    # Recall memories
    memories = recall_memories(user_input)
    if memories:
        context.insert(0, {"role": "system", "content": f"[MEMORIES]: {' | '.join(m[:200] for m in memories)}"})
        yield ("System", f"📜 Recalled {len(memories)} memories", "system")
    
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
    budget -= tokens
    save_message(session_id, "assistant", alt, innovator["name"])
    context.append({"role": "assistant", "content": alt})
    yield (innovator["name"], alt, "innovator")
    
    # PHASE 3: INQUISITOR
    yield ("System", "🔍 PHASE 3: Examining...", "system")
    inquisitor = AGENTS["Inquisitor"]
    approved = False
    
    for attempt in range(2):
        yield ("System", f"{inquisitor['avatar']} {inquisitor['name']} examining... ({attempt+1}/2)", "system")
        critique, tokens = call_llm("Inquisitor", [{"role": "system", "content": inquisitor["style"]}] + context, 1200)
        budget -= tokens
        save_message(session_id, "assistant", critique, inquisitor["name"])
        context.append({"role": "assistant", "content": critique})
        yield (inquisitor["name"], critique, "critique")
        
        if "APPROVED" in critique.upper():
            approved = True
            yield ("System", "✅ Approved", "system")
            break
        elif "REJECTED" in critique.upper() and attempt == 0:
            yield ("System", "🔧 Auto-fixing...", "system")
            context.append({"role": "user", "content": f"Fix these issues: {critique}"})
            code, tokens = call_llm("Executor", [{"role": "system", "content": executor["style"]}] + context, 4000)
            budget -= tokens
            save_message(session_id, "assistant", code, f"{executor['name']} (Fixed)")
            context.append({"role": "assistant", "content": code})
            yield (f"{executor['name']} (Fixed)", code, "code")
    
    # PHASE 4: EMPEROR
    yield ("System", "👑 PHASE 4: Final Judgment...", "system")
    emperor = AGENTS["Emperor"]
    yield ("System", f"{emperor['avatar']} {emperor['name']} synthesizing...", "system")
    
    emperor_prompt = f"""ORIGINAL: {user_input[:400]}
PLAN: {plan[:600]}
CODE: {code[:1200]}
CRITIQUE: {critique[:400]}
ALTERNATIVE: {alt[:400]}
{"APPROVED" if approved else "Had concerns"}

Deliver the FINAL answer."""
    
    verdict, tokens = call_llm("Emperor", [{"role": "system", "content": emperor["style"]}, {"role": "user", "content": emperor_prompt}], 4000)
    budget -= tokens
    save_message(session_id, "assistant", verdict, emperor["name"])
    yield (emperor["name"], verdict, "emperor")
    
    if approved:
        save_memory(f"SUCCESS: {user_input[:100]} -> {verdict[:300]}")
        yield ("System", "📖 Archived to memory", "system")
    
    yield ("System", f"🏯 Complete. Budget: {budget}/{SESSION_BUDGET}", "system")
