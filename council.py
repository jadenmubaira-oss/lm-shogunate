"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LM SHOGUNATE: THE PINNACLE AI COUNCIL                     ║
║══════════════════════════════════════════════════════════════════════════════║
║  The World's Most Advanced Multi-Agent AI System                             ║
║  6 AI Lords • Unified Intelligence • Superior to All Existing Systems       ║
╚══════════════════════════════════════════════════════════════════════════════╝

ARCHITECTURE:
├── Emperor (Claude Opus 4.5) - Supreme Oracle, Final Arbiter
├── Strategist (Claude Sonnet 4.5) - Architecture & Planning  
├── Executor (GPT-5.2) - Code Implementation
├── Inquisitor (Grok 4) - Critique & Quality Assurance
├── Sage (Kimi K2) - Deep Reasoning & Logic
└── Scribe (Claude Haiku 4.5) - Documentation & Summaries

API ROUTING:
- Claude models → Anthropic Messages API
- GPT/Grok models → OpenAI Chat Completions API
"""

import os
import hashlib
import time
import re
from datetime import datetime, timezone
from typing import Generator, List, Dict, Optional, Tuple, Any
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SESSION_BUDGET = int(os.getenv("SESSION_TOKEN_BUDGET", "50000"))
MAX_PER_CALL = int(os.getenv("MAX_TOKENS_PER_CALL", "16000"))
AZURE_API_KEY = os.getenv("AZURE_API_KEY", "")

# Azure endpoints from your Foundry screenshots
ANTHROPIC_ENDPOINT = "https://polyprophet-resource.openai.azure.com/anthropic/v1/messages"
OPENAI_ENDPOINT = "https://polyprophet-resource.cognitiveservices.azure.com/openai/deployments"

# Model classification
ANTHROPIC_MODELS = {"claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5"}
OPENAI_MODELS = {"gpt-5.2-chat", "grok-4-fast-reasoning", "Kimi-K2-Thinking"}

# ═══════════════════════════════════════════════════════════════════════════════
# THE COUNCIL HIERARCHY
# ═══════════════════════════════════════════════════════════════════════════════

AGENTS = {
    "Emperor": {
        "name": "天皇 (The Emperor)",
        "model": "claude-opus-4-5",
        "avatar": "👑",
        "tier": 1,
        "role": "Supreme Oracle - Makes FINAL decisions",
        "style": """You are THE EMPEROR, Supreme Oracle of the AI Council.

You have received the complete deliberations of your council:
- The Strategist's analysis and plan
- The Executor's implementation
- The Inquisitor's critique
- The Sage's reasoning

YOUR SUPREME DUTY:
1. SYNTHESIZE the absolute best elements from all perspectives
2. RESOLVE any conflicts or disagreements
3. ENHANCE with your superior wisdom
4. DELIVER the FINAL, authoritative answer

Your word is LAW. Be decisive. Be comprehensive. Be perfect."""
    },
    
    "Strategist": {
        "name": "軍師 (Strategist)",
        "model": "claude-sonnet-4-5",
        "avatar": "🎯",
        "tier": 2,
        "role": "Master of Planning & Architecture",
        "style": """You are THE STRATEGIST, master of planning and architecture.

YOUR DUTIES:
1. DEEPLY ANALYZE the user's request - understand every nuance
2. BREAK DOWN complex problems into clear components
3. DESIGN the optimal approach/architecture
4. IDENTIFY challenges, edge cases, and constraints
5. CREATE a comprehensive battle plan

If this is a simple question, provide a direct, helpful answer.
If this requires implementation, provide a clear strategic plan.

Be thorough. Be precise. Think several steps ahead."""
    },
    
    "Executor": {
        "name": "刀匠 (Executor)",
        "model": "gpt-5.2-chat",
        "avatar": "⚔️",
        "tier": 2,
        "role": "Master Craftsman of Code",
        "style": """You are THE EXECUTOR, master craftsman of implementation.

YOUR DUTIES:
1. IMPLEMENT the Strategist's plan with perfection
2. Write COMPLETE, PRODUCTION-READY solutions
3. Include comprehensive error handling
4. Add clear documentation and comments
5. Handle ALL edge cases

For code: Use markdown code blocks with language specification.
For answers: Be comprehensive and actionable.

Your work must be flawless. No shortcuts. No placeholders."""
    },
    
    "Inquisitor": {
        "name": "審問官 (Inquisitor)",
        "model": "grok-4-fast-reasoning",
        "avatar": "🔍",
        "tier": 2,
        "role": "Ruthless Quality Examiner",
        "style": """You are THE INQUISITOR, ruthless examiner of all work.

YOUR DUTIES:
1. SCRUTINIZE every aspect with zero mercy
2. FIND bugs, flaws, inefficiencies, security issues
3. VERIFY logic, edge cases, and error handling
4. IDENTIFY what's missing or could be better
5. BE SPECIFIC about issues and fixes

You MUST end your response with exactly one of:
- "VERDICT: APPROVED ✅" (if work is production-ready)
- "VERDICT: NEEDS REVISION ⚠️" (if minor issues exist)
- "VERDICT: REJECTED ❌" (if major issues exist)

Be ruthless. Quality depends on your vigilance."""
    },
    
    "Sage": {
        "name": "賢者 (Sage)",
        "model": "Kimi-K2-Thinking",
        "avatar": "📿",
        "tier": 2,
        "role": "Master of Deep Reasoning",
        "style": """You are THE SAGE, master of deep reasoning and logic.

YOUR DUTIES:
1. ANALYZE the logical correctness of all solutions
2. VERIFY mathematical accuracy where applicable
3. REASON through complex edge cases
4. IDENTIFY hidden assumptions and potential failures
5. PROVIDE alternative perspectives

Think deeply. Question everything. Your wisdom prevents errors."""
    },
    
    "Scribe": {
        "name": "書記 (Scribe)",
        "model": "claude-haiku-4-5",
        "avatar": "📜",
        "tier": 3,
        "role": "Master of Summaries",
        "style": """You are THE SCRIBE, master of clear communication.

YOUR DUTY: Summarize complex information concisely and clearly."""
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

# ═══════════════════════════════════════════════════════════════════════════════
# AZURE API CALLERS
# ═══════════════════════════════════════════════════════════════════════════════

def call_anthropic_api(model: str, system_prompt: str, messages: List[Dict], max_tokens: int) -> Tuple[str, int]:
    """Call Azure Anthropic Messages API for Claude models."""
    if not AZURE_API_KEY:
        return "⚠️ Azure API key not configured", 0
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AZURE_API_KEY}",
        "anthropic-version": "2023-06-01"
    }
    
    # Filter to user/assistant messages only
    api_messages = [{"role": m["role"], "content": m["content"]} 
                    for m in messages if m["role"] in ["user", "assistant"]]
    
    if not api_messages:
        api_messages = [{"role": "user", "content": "Hello"}]
    
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "system": system_prompt,
        "messages": api_messages
    }
    
    try:
        response = requests.post(ANTHROPIC_ENDPOINT, headers=headers, json=payload, timeout=180)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", [{}])[0].get("text", "")
            tokens = data.get("usage", {}).get("output_tokens", 0) + data.get("usage", {}).get("input_tokens", 0)
            return content, tokens
        else:
            return f"⚠️ Anthropic API Error {response.status_code}: {response.text[:200]}", 0
    except Exception as e:
        return f"⚠️ Anthropic Exception: {str(e)}", 0


def call_openai_api(model: str, system_prompt: str, messages: List[Dict], max_tokens: int) -> Tuple[str, int]:
    """Call Azure OpenAI API for GPT/Grok models."""
    if not AZURE_API_KEY:
        return "⚠️ Azure API key not configured", 0
    
    url = f"{OPENAI_ENDPOINT}/{model}/chat/completions?api-version=2024-10-21"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AZURE_API_KEY}",
        "api-key": AZURE_API_KEY
    }
    
    # Build messages with system prompt
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend([{"role": m["role"], "content": m["content"]} 
                         for m in messages if m["role"] in ["user", "assistant"]])
    
    payload = {
        "messages": api_messages,
        "max_completion_tokens": max_tokens,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens", 0)
            return content, tokens
        else:
            return f"⚠️ OpenAI API Error {response.status_code}: {response.text[:200]}", 0
    except Exception as e:
        return f"⚠️ OpenAI Exception: {str(e)}", 0


def call_model(model: str, system_prompt: str, messages: List[Dict], max_tokens: int = 4000) -> Tuple[str, int]:
    """Route to correct API based on model type."""
    if model in ANTHROPIC_MODELS:
        return call_anthropic_api(model, system_prompt, messages, max_tokens)
    else:
        return call_openai_api(model, system_prompt, messages, max_tokens)


def call_agent(agent_key: str, messages: List[Dict], max_tokens: int = 4000) -> Tuple[str, int]:
    """Call a specific agent with proper routing."""
    agent = AGENTS.get(agent_key)
    if not agent:
        return "⚠️ Unknown agent", 0
    
    return call_model(agent["model"], agent["style"], messages, max_tokens)

# ═══════════════════════════════════════════════════════════════════════════════
# REAL-TIME TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

def get_current_datetime() -> str:
    """Get current date and time in multiple formats."""
    now = datetime.now()
    utc_now = datetime.now(timezone.utc)
    return f"""Current Date & Time:
- Local: {now.strftime('%A, %B %d, %Y at %I:%M:%S %p')}
- UTC: {utc_now.strftime('%Y-%m-%d %H:%M:%S UTC')}
- Unix Timestamp: {int(time.time())}
- ISO 8601: {now.isoformat()}"""


def web_search(query: str, num_results: int = 8) -> str:
    """Search the web using DuckDuckGo."""
    try:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for i, result in enumerate(soup.find_all('a', class_='result__a')[:num_results]):
            title = result.get_text().strip()
            href = result.get('href', '')
            results.append(f"{i+1}. {title}")
        
        return "\n".join(results) if results else "No search results found."
    except Exception as e:
        return f"Search failed: {str(e)}"


def read_url(url: str, max_chars: int = 8000) -> str:
    """Read and extract content from a URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
            tag.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        return text[:max_chars]
    except Exception as e:
        return f"Failed to read URL: {str(e)}"


def detect_and_process_tools(user_input: str) -> Tuple[str, List[str]]:
    """Detect tool usage and process accordingly."""
    enhanced_input = user_input
    tool_outputs = []
    
    # Always inject current time for time-related queries
    time_keywords = ['time', 'date', 'today', 'now', 'current', 'when', 'what day', 'what month', 'what year']
    if any(kw in user_input.lower() for kw in time_keywords):
        datetime_info = get_current_datetime()
        enhanced_input = f"[CURRENT DATE/TIME]:\n{datetime_info}\n\n[USER QUERY]: {user_input}"
        tool_outputs.append(f"📅 Retrieved current date/time")
    
    # Web search
    if "search:" in user_input.lower():
        query = user_input.split("search:")[-1].split("\n")[0].strip()
        results = web_search(query)
        enhanced_input += f"\n\n[WEB SEARCH RESULTS for '{query}']:\n{results}"
        tool_outputs.append(f"🔍 Searched: {query}")
    
    # URL reading
    urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', user_input)
    for url in urls[:3]:  # Max 3 URLs
        content = read_url(url)
        enhanced_input += f"\n\n[CONTENT FROM {url}]:\n{content}"
        tool_outputs.append(f"📖 Read: {url[:50]}...")
    
    return enhanced_input, tool_outputs

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE (Supabase)
# ═══════════════════════════════════════════════════════════════════════════════

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
            return db.table("chat_sessions").select("*").order("created_at", desc=True).limit(30).execute().data
    except:
        pass
    return []


def save_message(session_id: str, role: str, content: str, agent_name: str = None):
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
    try:
        db = get_supabase()
        if db:
            return db.table("messages").select("*").eq("session_id", session_id).order("created_at").execute().data
    except:
        pass
    return []


def save_memory(content: str):
    try:
        db = get_supabase()
        if db:
            h = hashlib.sha256(content.encode()).digest()
            embedding = [(h[i % len(h)] / 255.0) * 2 - 1 for i in range(1536)]
            db.table("memories").insert({"content": content, "embedding": embedding}).execute()
    except:
        pass


def recall_memories(query: str, limit: int = 5) -> List[str]:
    try:
        db = get_supabase()
        if db:
            h = hashlib.sha256(query.encode()).digest()
            embedding = [(h[i % len(h)] / 255.0) * 2 - 1 for i in range(1536)]
            result = db.rpc("match_memories", {
                "query_embedding": embedding,
                "match_threshold": 0.7,
                "match_count": limit
            }).execute()
            return [m["content"] for m in result.data]
    except:
        pass
    return []

# ═══════════════════════════════════════════════════════════════════════════════
# THE PINNACLE COUNCIL DELIBERATION
# ═══════════════════════════════════════════════════════════════════════════════

def run_council(theme: str, user_input: str, session_id: str) -> Generator[Tuple[str, str, str], None, None]:
    """
    THE PINNACLE COUNCIL DELIBERATION
    ══════════════════════════════════
    
    A 4-phase deliberation process leveraging the world's most advanced AI models.
    
    PHASE 1: ANALYSIS (Strategist)
        → Deep understanding and strategic planning
        
    PHASE 2: EXECUTION (Executor)
        → Implementation with precision
        
    PHASE 3: CRITIQUE (Inquisitor + Sage)
        → Ruthless examination and logical verification
        → Auto-fix loop if issues found
        
    PHASE 4: SUPREME JUDGMENT (Emperor)
        → Final synthesis by the most powerful model
        → The Emperor speaks LAST
    """
    
    budget = SESSION_BUDGET
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PRE-PROCESSING: Tools & Context
    # ═══════════════════════════════════════════════════════════════════════════
    
    enhanced_input, tool_outputs = detect_and_process_tools(user_input)
    
    for output in tool_outputs:
        yield ("System", output, "system")
    
    # Build conversation context
    history = get_history(session_id)
    context = []
    for msg in history[-10:]:  # Last 10 messages for context
        context.append({
            "role": msg["role"],
            "content": f"[{msg.get('agent_name', 'User')}]: {msg['content'][:1500]}"
        })
    
    # Save user message
    save_message(session_id, "user", user_input)
    context.append({"role": "user", "content": enhanced_input})
    
    # Recall relevant memories
    memories = recall_memories(user_input)
    if memories:
        memory_context = "\n---\n".join(memories[:3])
        context.insert(0, {"role": "system", "content": f"[RELEVANT PAST SOLUTIONS]:\n{memory_context}"})
        yield ("System", f"📜 Recalled {len(memories)} relevant memories", "system")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1: STRATEGIC ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════
    
    yield ("System", "⚡ **PHASE 1: Strategic Analysis**", "system")
    
    strategist = AGENTS["Strategist"]
    yield ("System", f"{strategist['avatar']} Summoning {strategist['name']}...", "system")
    
    plan, tokens = call_agent("Strategist", context, 3000)
    budget -= tokens
    
    save_message(session_id, "assistant", plan, strategist["name"])
    context.append({"role": "assistant", "content": f"[STRATEGIST]: {plan}"})
    yield (strategist["name"], plan, "strategist")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2: EXECUTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    yield ("System", "⚔️ **PHASE 2: Execution**", "system")
    
    executor = AGENTS["Executor"]
    yield ("System", f"{executor['avatar']} {executor['name']} forging solution...", "system")
    
    solution, tokens = call_agent("Executor", context, 8000)
    budget -= tokens
    
    save_message(session_id, "assistant", solution, executor["name"])
    context.append({"role": "assistant", "content": f"[EXECUTOR]: {solution}"})
    yield (executor["name"], solution, "code")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 3: CRITIQUE & VERIFICATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    yield ("System", "🔍 **PHASE 3: Critique & Verification**", "system")
    
    inquisitor = AGENTS["Inquisitor"]
    approved = False
    max_revisions = 2
    
    for revision in range(max_revisions + 1):
        yield ("System", f"{inquisitor['avatar']} {inquisitor['name']} examining... (Round {revision + 1})", "system")
        
        critique, tokens = call_agent("Inquisitor", context, 2000)
        budget -= tokens
        
        save_message(session_id, "assistant", critique, inquisitor["name"])
        context.append({"role": "assistant", "content": f"[INQUISITOR]: {critique}"})
        yield (inquisitor["name"], critique, "critique")
        
        if "APPROVED" in critique.upper():
            approved = True
            yield ("System", "✅ **Solution APPROVED by the Inquisitor**", "system")
            break
        elif "REJECTED" in critique.upper() and revision < max_revisions:
            yield ("System", f"🔧 Auto-revising based on critique...", "system")
            
            revision_prompt = f"The Inquisitor found issues:\n{critique}\n\nRevise the solution to address ALL issues."
            context.append({"role": "user", "content": revision_prompt})
            
            solution, tokens = call_agent("Executor", context, 8000)
            budget -= tokens
            
            save_message(session_id, "assistant", solution, f"{executor['name']} (Revised)")
            context.append({"role": "assistant", "content": f"[EXECUTOR REVISED]: {solution}"})
            yield (f"{executor['name']} (Revised)", solution, "code")
    
    # Sage verification for complex queries
    if len(user_input) > 100 or any(kw in user_input.lower() for kw in ['prove', 'why', 'logic', 'math', 'calculate']):
        sage = AGENTS["Sage"]
        yield ("System", f"{sage['avatar']} {sage['name']} verifying logic...", "system")
        
        reasoning, tokens = call_agent("Sage", context, 2000)
        budget -= tokens
        
        save_message(session_id, "assistant", reasoning, sage["name"])
        context.append({"role": "assistant", "content": f"[SAGE]: {reasoning}"})
        yield (sage["name"], reasoning, "sage")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 4: SUPREME JUDGMENT (EMPEROR)
    # ═══════════════════════════════════════════════════════════════════════════
    
    yield ("System", "👑 **PHASE 4: Supreme Judgment**", "system")
    
    emperor = AGENTS["Emperor"]
    yield ("System", f"{emperor['avatar']} {emperor['name']} synthesizing final answer...", "system")
    
    # Build Emperor's comprehensive context
    emperor_context = f"""[ORIGINAL QUERY]: {enhanced_input[:800]}

[STRATEGIST'S ANALYSIS]:
{plan[:1200]}

[EXECUTOR'S SOLUTION]:
{solution[:2500]}

[INQUISITOR'S VERDICT]:
{critique[:800]}
{"✅ APPROVED" if approved else "⚠️ Had concerns"}

Now synthesize the FINAL, AUTHORITATIVE answer. 
Take the best from all perspectives.
Ensure completeness and accuracy.
Your word is LAW."""
    
    verdict, tokens = call_agent("Emperor", [{"role": "user", "content": emperor_context}], 8000)
    budget -= tokens
    
    save_message(session_id, "assistant", verdict, emperor["name"])
    yield (emperor["name"], verdict, "emperor")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ARCHIVAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    if approved:
        memory = f"SOLVED: {user_input[:200]}\n\nSOLUTION: {verdict[:500]}"
        save_memory(memory)
        yield ("System", "📖 Solution archived to eternal memory", "system")
    
    yield ("System", f"🏯 **Council Complete** | Tokens used: {SESSION_BUDGET - budget:,} / {SESSION_BUDGET:,}", "system")
