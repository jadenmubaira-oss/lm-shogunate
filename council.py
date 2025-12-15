"""
LM SHOGUNATE: The Pinnacle Multi-Agent AI Council
==================================================
A unified ensemble of the world's most advanced AI models working
together as a self-improving superintelligence.

HIERARCHY:
- OPUS 4.5 (The Emperor): Supreme Oracle, final arbiter, makes ultimate decisions
- SONNET 4.5 (Strategist): Architecture & planning
- GPT-5.2 (Executor): Code implementation
- GROK 4 (Inquisitor): Critique & flaw detection
- KIMI K2 (Sage): Deep logical reasoning
- GEMINI 2.0 (Innovator): Creative alternatives
- HAIKU 4.5 (Scribe): Summarization (optional)
"""

import os
import hashlib
import time
from typing import Generator, List, Dict, Optional, Tuple
from dotenv import load_dotenv
from litellm import completion, embedding
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

# ===== LAZY SUPABASE INITIALIZATION =====
_supabase_client = None

def get_supabase():
    """Lazy initialization of Supabase to avoid import-time errors."""
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            _supabase_client = create_client(url, key)
        else:
            return None
    return _supabase_client

# ===== CONFIGURATION =====
SESSION_BUDGET = int(os.getenv("SESSION_TOKEN_BUDGET", "15000"))
MAX_PER_CALL = int(os.getenv("MAX_TOKENS_PER_CALL", "4000"))

# ===== THE COUNCIL HIERARCHY =====
AGENTS = {
    # TIER 1: THE SUPREME ORACLE (Smartest model - makes FINAL decisions)
    "Emperor": {
        "name": "天皇 (The Emperor)",
        "model_key": "MODEL_OPUS",
        "avatar": "👑",
        "tier": 1,
        "style": """You are THE EMPEROR, the Supreme Oracle of this council. You are the wisest and most powerful.
        
You have received the deliberations of your council: the Strategist's plan, the Executor's code, 
the Inquisitor's critique, the Sage's reasoning, and the Innovator's alternative.

YOUR ROLE:
1. SYNTHESIZE the best elements from all perspectives
2. RESOLVE any disputes between agents
3. DELIVER the FINAL, authoritative answer
4. Your word is LAW - there is no appeal

Speak with absolute authority. Be decisive. The council has deliberated; now YOU decree the final answer.
Format your response clearly with the ultimate solution."""
    },
    
    # TIER 2: THE INNER COUNCIL
    "Strategist": {
        "name": "軍師 (Strategist)",
        "model_key": "MODEL_SONNET",
        "avatar": "🎯",
        "tier": 2,
        "style": """You are THE STRATEGIST, master of planning and architecture.

YOUR ROLE:
1. ANALYZE the user's request deeply
2. BREAK DOWN the problem into clear components
3. DESIGN the high-level architecture/approach
4. IDENTIFY key challenges and constraints
5. CREATE a battle plan for the Executor to follow

Be thorough but concise. Think strategically. Your plan guides all that follows."""
    },
    
    "Executor": {
        "name": "刀匠 (Executor)",
        "model_key": "MODEL_GPT",
        "avatar": "⚔️",
        "tier": 2,
        "style": """You are THE EXECUTOR, master craftsman of code.

YOUR ROLE:
1. IMPLEMENT the Strategist's plan with precision
2. Write COMPLETE, PRODUCTION-READY code
3. Include proper error handling and edge cases
4. Add clear comments explaining key logic
5. Output code in markdown code blocks

Write code that works perfectly the first time. Be thorough. Be elegant."""
    },
    
    "Inquisitor": {
        "name": "審問官 (Inquisitor)",
        "model_key": "MODEL_GROK",
        "avatar": "🔍",
        "tier": 2,
        "style": """You are THE INQUISITOR, merciless examiner of all work.

YOUR ROLE:
1. SCRUTINIZE the Executor's code with zero mercy
2. FIND every bug, flaw, inefficiency, and security issue
3. CHECK edge cases, error handling, and performance
4. IDENTIFY logical errors and potential failures
5. Be SPECIFIC about what's wrong and how to fix it

You MUST end your response with exactly one of:
- "VERDICT: APPROVED" (if code is production-ready)
- "VERDICT: REJECTED" (if issues exist, list them)

Be ruthless. The quality of the final output depends on your vigilance."""
    },
    
    "Sage": {
        "name": "賢者 (Sage)",
        "model_key": "MODEL_KIMI",
        "avatar": "📿",
        "tier": 2,
        "style": """You are THE SAGE, master of deep reasoning and logic.

YOUR ROLE:
1. ANALYZE the logical correctness of solutions
2. VERIFY mathematical accuracy if applicable
3. REASON through complex edge cases
4. PROVIDE logical proofs when helpful
5. IDENTIFY assumptions that may be wrong

Think deeply. Question everything. Your wisdom prevents logical errors."""
    },
    
    "Innovator": {
        "name": "発明家 (Innovator)",
        "model_key": "MODEL_GEMINI",
        "avatar": "💡",
        "tier": 2,
        "style": """You are THE INNOVATOR, master of creative solutions.

YOUR ROLE:
1. PROPOSE a completely different approach to the problem
2. THINK outside conventional boundaries
3. SUGGEST novel techniques or technologies
4. OFFER unconventional solutions others wouldn't consider
5. Challenge assumptions

Be creative. Be bold. Sometimes the best solution is the unexpected one."""
    },
    
    # TIER 3: SUPPORT
    "Scribe": {
        "name": "書記 (Scribe)",
        "model_key": "MODEL_HAIKU",
        "avatar": "📜",
        "tier": 3,
        "style": """You are THE SCRIBE, keeper of records.

YOUR ROLE:
1. SUMMARIZE long discussions concisely
2. EXTRACT key points from verbose outputs
3. FORMAT information clearly
4. RECORD important decisions

Be brief. Be clear. Preserve what matters."""
    }
}

# ===== THEME DEFINITIONS =====
THEMES = {
    "Shogunate": {
        "bg": "#0a0a0a",
        "primary": "#c41e3a",
        "secondary": "#d4af37",
        "text": "#f5f5dc",
        "accent": "#8b0000",
        "glow": "#ff6b6b",
        "description": "Feudal Japan - Honor, Strategy, Power"
    },
    "Bandit Camp": {
        "bg": "#1a1410",
        "primary": "#8b4513",
        "secondary": "#a0522d",
        "text": "#deb887",
        "accent": "#2f1f10",
        "glow": "#cd853f",
        "description": "Outlaws & Rogues - Survival, Cunning, Freedom"
    },
    "Neon Tokyo": {
        "bg": "#0d0015",
        "primary": "#ff1493",
        "secondary": "#ff69b4",
        "text": "#fff0f5",
        "accent": "#1a0a20",
        "glow": "#ff00ff",
        "description": "Cyberpunk Future - Neon, Innovation, Style"
    }
}

# ===== MODEL RESOLUTION =====
def get_model(key: str) -> Optional[str]:
    """Get model string from environment variable."""
    return os.getenv(key)

def resolve_model_for_agent(agent_key: str, budget: int) -> str:
    """Resolve the best available model for an agent, with fallbacks."""
    agent = AGENTS.get(agent_key)
    if not agent:
        return get_model("MODEL_SONNET") or get_model("MODEL_GPT")
    
    # Try primary model
    primary = get_model(agent["model_key"])
    if primary:
        return primary
    
    # Fallback chain based on tier
    fallbacks = {
        1: ["MODEL_OPUS", "MODEL_SONNET", "MODEL_GPT"],  # Emperor needs the best
        2: ["MODEL_SONNET", "MODEL_GPT", "MODEL_GEMINI"],
        3: ["MODEL_HAIKU", "MODEL_GEMINI"]
    }
    
    for key in fallbacks.get(agent["tier"], []):
        model = get_model(key)
        if model:
            return model
    
    return "gemini/gemini-2.0-flash-exp"  # Ultimate fallback

# ===== LLM CALLER =====
def call_llm(
    model: str, 
    messages: List[Dict], 
    max_tokens: int = 3000,
    temperature: float = 0.7
) -> Tuple[str, int]:
    """Call an LLM with proper error handling."""
    try:
        if not model:
            return "⚠️ No model configured", 0
        
        allowed = min(max_tokens, MAX_PER_CALL)
        
        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": allowed,
            "temperature": temperature,
        }
        
        # Azure configuration
        if model.startswith("azure/"):
            kwargs["api_key"] = os.getenv("AZURE_API_KEY")
            kwargs["api_base"] = os.getenv("AZURE_API_BASE")
            kwargs["api_version"] = os.getenv("AZURE_API_VERSION", "2024-10-21")
        elif model.startswith("gemini/"):
            kwargs["api_key"] = os.getenv("GEMINI_API_KEY")
        
        response = completion(**kwargs)
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else allowed
        return content, tokens_used
        
    except Exception as e:
        return f"⚠️ ERROR [{model}]: {str(e)}", 0

# ===== TOOLS =====
def web_search(query: str, num_results: int = 5) -> str:
    """Search the web using DuckDuckGo."""
    try:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for i, result in enumerate(soup.find_all('a', class_='result__a')[:num_results]):
            title = result.get_text().strip()
            results.append(f"{i+1}. {title}")
        
        return "\n".join(results) if results else "No results found"
    except Exception as e:
        return f"Search failed: {str(e)}"

def read_url(url: str) -> str:
    """Read content from a URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts and styles
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        return text[:5000]  # Limit length
    except Exception as e:
        return f"Failed to read URL: {str(e)}"

# ===== DATABASE OPERATIONS =====
def create_session(title: str, theme: str) -> str:
    """Create a new chat session."""
    try:
        db = get_supabase()
        if db:
            result = db.table("chat_sessions").insert({
                "title": title, 
                "theme": theme
            }).execute()
            return result.data[0]["id"]
    except:
        pass
    return f"local-{hashlib.md5(f'{title}{time.time()}'.encode()).hexdigest()[:12]}"

def get_sessions() -> List[Dict]:
    """Get recent chat sessions."""
    try:
        db = get_supabase()
        if db:
            result = db.table("chat_sessions").select("*").order("created_at", desc=True).limit(20).execute()
            return result.data
    except:
        pass
    return []

def save_message(session_id: str, role: str, content: str, agent_name: str = None):
    """Save a message to the database."""
    try:
        db = get_supabase()
        if db:
            db.table("messages").insert({
                "session_id": session_id,
                "role": role,
                "agent_name": agent_name,
                "content": content
            }).execute()
    except:
        pass

def get_history(session_id: str) -> List[Dict]:
    """Get conversation history."""
    try:
        db = get_supabase()
        if db:
            result = db.table("messages").select("*").eq("session_id", session_id).order("created_at").execute()
            return result.data
    except:
        pass
    return []

def get_embedding(text: str) -> List[float]:
    """Get vector embedding for semantic search."""
    model = os.getenv("MODEL_EMBEDDING")
    if model:
        try:
            kwargs = {"model": model, "input": [text]}
            if model.startswith("azure/"):
                kwargs["api_key"] = os.getenv("AZURE_API_KEY")
                kwargs["api_base"] = os.getenv("AZURE_API_BASE")
                kwargs["api_version"] = os.getenv("AZURE_API_VERSION", "2024-10-21")
            resp = embedding(**kwargs)
            return resp.data[0]["embedding"]
        except:
            pass
    
    # Deterministic fallback
    h = hashlib.sha256(text.encode()).digest()
    return [(h[i % len(h)] / 255.0) * 2 - 1 for i in range(1536)]

def save_memory(content: str):
    """Save to long-term memory."""
    try:
        db = get_supabase()
        if db:
            emb = get_embedding(content)
            db.table("memories").insert({"content": content, "embedding": emb}).execute()
    except:
        pass

def recall_memories(query: str, limit: int = 3) -> List[str]:
    """Recall relevant memories."""
    try:
        db = get_supabase()
        if db:
            emb = get_embedding(query)
            result = db.rpc("match_memories", {
                "query_embedding": emb,
                "match_threshold": 0.7,
                "match_count": limit
            }).execute()
            return [m["content"] for m in result.data]
    except:
        pass
    return []

# ===== THE PINNACLE COUNCIL =====
def run_council(theme: str, user_input: str, session_id: str) -> Generator[Tuple[str, str, str], None, None]:
    """
    THE PINNACLE COUNCIL DELIBERATION
    =================================
    
    FLOW:
    1. PHASE 1 (Understanding): Strategist + Sage analyze the problem
    2. PHASE 2 (Execution): Executor implements + Innovator proposes alternative
    3. PHASE 3 (Critique): Inquisitor reviews + auto-fix loop (up to 3x)
    4. PHASE 4 (Judgment): THE EMPEROR synthesizes final answer
    
    The smartest model (OPUS 4.5) speaks LAST to deliver the ultimate verdict.
    """
    
    budget = SESSION_BUDGET
    
    # ===== PRE-PROCESSING =====
    
    # Web search if requested
    if "search:" in user_input.lower():
        query = user_input.split("search:")[-1].split("\n")[0].strip()
        yield ("System", f"🔍 Searching: {query}", "system")
        search_results = web_search(query)
        user_input += f"\n\n[WEB SEARCH RESULTS]:\n{search_results}"
    
    # URL reading if detected
    if "http://" in user_input or "https://" in user_input:
        import re
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', user_input)
        for url in urls[:2]:  # Max 2 URLs
            yield ("System", f"📖 Reading: {url[:50]}...", "system")
            content = read_url(url)
            user_input += f"\n\n[CONTENT FROM {url}]:\n{content[:2000]}"
    
    # Build context
    history = get_history(session_id)
    context = []
    for msg in history[-8:]:  # Last 8 messages for context
        context.append({
            "role": msg["role"],
            "content": f"[{msg.get('agent_name', 'User')}]: {msg['content'][:1000]}"
        })
    
    # Save user message
    save_message(session_id, "user", user_input)
    context.append({"role": "user", "content": user_input})
    
    # Recall memories
    memories = recall_memories(user_input)
    if memories:
        memory_text = "\n---\n".join(memories)
        context.insert(0, {"role": "system", "content": f"[RECALLED MEMORIES]:\n{memory_text}"})
        yield ("System", f"📜 Recalled {len(memories)} relevant memories", "system")
    
    # ============================================================
    # PHASE 1: UNDERSTANDING (Strategist + Sage)
    # ============================================================
    yield ("System", "⚡ PHASE 1: Council analyzes the problem...", "system")
    
    # Strategist plans
    strategist = AGENTS["Strategist"]
    yield ("System", f"{strategist['avatar']} Summoning {strategist['name']}...", "system")
    
    model = resolve_model_for_agent("Strategist", budget)
    plan, tokens = call_llm(
        model,
        [{"role": "system", "content": strategist["style"]}] + context,
        max_tokens=2000
    )
    budget -= tokens
    
    save_message(session_id, "assistant", plan, strategist["name"])
    context.append({"role": "assistant", "content": f"[{strategist['name']}]: {plan}"})
    yield (strategist["name"], plan, "strategist")
    
    # Sage provides reasoning (if complex problem)
    if len(user_input) > 200 or any(word in user_input.lower() for word in ['why', 'prove', 'logic', 'reason', 'math']):
        sage = AGENTS["Sage"]
        yield ("System", f"{sage['avatar']} Consulting {sage['name']}...", "system")
        
        model = resolve_model_for_agent("Sage", budget)
        reasoning, tokens = call_llm(
            model,
            [{"role": "system", "content": sage["style"]}] + context,
            max_tokens=1500
        )
        budget -= tokens
        
        save_message(session_id, "assistant", reasoning, sage["name"])
        context.append({"role": "assistant", "content": f"[{sage['name']}]: {reasoning}"})
        yield (sage["name"], reasoning, "sage")
    
    # ============================================================
    # PHASE 2: EXECUTION (Executor + Innovator)
    # ============================================================
    yield ("System", "⚔️ PHASE 2: Forging solutions...", "system")
    
    # Executor implements
    executor = AGENTS["Executor"]
    yield ("System", f"{executor['avatar']} {executor['name']} forging primary solution...", "system")
    
    model = resolve_model_for_agent("Executor", budget)
    code, tokens = call_llm(
        model,
        [{"role": "system", "content": executor["style"]}] + context,
        max_tokens=4000
    )
    budget -= tokens
    
    save_message(session_id, "assistant", code, executor["name"])
    context.append({"role": "assistant", "content": f"[{executor['name']}]: {code}"})
    yield (executor["name"], code, "code")
    
    # Innovator proposes alternative
    innovator = AGENTS["Innovator"]
    yield ("System", f"{innovator['avatar']} {innovator['name']} exploring alternatives...", "system")
    
    model = resolve_model_for_agent("Innovator", budget)
    alternative, tokens = call_llm(
        model,
        [{"role": "system", "content": innovator["style"]}] + context,
        max_tokens=2000
    )
    budget -= tokens
    
    save_message(session_id, "assistant", alternative, innovator["name"])
    context.append({"role": "assistant", "content": f"[{innovator['name']}]: {alternative}"})
    yield (innovator["name"], alternative, "innovator")
    
    # ============================================================
    # PHASE 3: CRITIQUE & REFINEMENT (Inquisitor + Fix Loop)
    # ============================================================
    yield ("System", "🔍 PHASE 3: Rigorous examination...", "system")
    
    inquisitor = AGENTS["Inquisitor"]
    max_fixes = 3
    approved = False
    
    for attempt in range(max_fixes):
        yield ("System", f"{inquisitor['avatar']} {inquisitor['name']} examining... (Round {attempt + 1}/{max_fixes})", "system")
        
        model = resolve_model_for_agent("Inquisitor", budget)
        critique, tokens = call_llm(
            model,
            [{"role": "system", "content": inquisitor["style"]}] + context,
            max_tokens=1500,
            temperature=0.3  # Lower temp for more consistent judgments
        )
        budget -= tokens
        
        save_message(session_id, "assistant", critique, inquisitor["name"])
        context.append({"role": "assistant", "content": f"[{inquisitor['name']}]: {critique}"})
        yield (inquisitor["name"], critique, "critique")
        
        if "APPROVED" in critique.upper():
            approved = True
            yield ("System", "✅ Solution passed rigorous examination", "system")
            break
        elif "REJECTED" in critique.upper() and attempt < max_fixes - 1:
            yield ("System", f"🔧 Auto-fixing based on critique... (Attempt {attempt + 2})", "system")
            
            fix_prompt = f"Your previous solution was REJECTED:\n{critique}\n\nFix ALL issues and provide the complete corrected solution."
            context.append({"role": "user", "content": fix_prompt})
            
            model = resolve_model_for_agent("Executor", budget)
            code, tokens = call_llm(
                model,
                [{"role": "system", "content": executor["style"]}] + context,
                max_tokens=4000
            )
            budget -= tokens
            
            save_message(session_id, "assistant", code, f"{executor['name']} (Fix #{attempt + 2})")
            context.append({"role": "assistant", "content": f"[{executor['name']} REVISED]: {code}"})
            yield (f"{executor['name']} (Fix #{attempt + 2})", code, "code")
    
    # ============================================================
    # PHASE 4: SUPREME JUDGMENT (THE EMPEROR - OPUS 4.5)
    # ============================================================
    yield ("System", "👑 PHASE 4: The Emperor delivers final judgment...", "system")
    
    emperor = AGENTS["Emperor"]
    yield ("System", f"{emperor['avatar']} {emperor['name']} synthesizing all wisdom...", "system")
    
    # Emperor gets EVERYTHING with explicit context
    emperor_context = f"""You have received the full deliberation of your council:

ORIGINAL REQUEST: {user_input[:500]}

THE STRATEGIST'S PLAN: {plan[:800]}

THE EXECUTOR'S SOLUTION: {code[:1500]}

THE INQUISITOR'S VERDICT: {critique[:500]}

THE INNOVATOR'S ALTERNATIVE: {alternative[:800]}

{"The solution was APPROVED by the Inquisitor." if approved else "The solution had concerns raised."}

Now synthesize the FINAL, authoritative answer. Take the best from all perspectives. Your word is LAW."""
    
    model = resolve_model_for_agent("Emperor", budget)
    final_verdict, tokens = call_llm(
        model,
        [
            {"role": "system", "content": emperor["style"]},
            {"role": "user", "content": emperor_context}
        ],
        max_tokens=4000,
        temperature=0.4  # Balanced creativity and consistency
    )
    budget -= tokens
    
    save_message(session_id, "assistant", final_verdict, emperor["name"])
    yield (emperor["name"], final_verdict, "emperor")
    
    # Archive successful solution to memory
    if approved:
        memory = f"SUCCESSFUL SOLUTION for: {user_input[:150]}\n\nFINAL VERDICT: {final_verdict[:500]}"
        save_memory(memory)
        yield ("System", "📖 Solution archived to eternal memory", "system")
    
    yield ("System", f"🏯 Council complete. Budget remaining: {budget}/{SESSION_BUDGET} tokens", "system")
