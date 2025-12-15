import os
import json
from typing import Generator, List, Dict
import time
from dotenv import load_dotenv
from litellm import completion
# Monkeypatch httpx SyncClient to accept legacy `proxy` kwarg passed by gotrue/supabase
try:
    import httpx

    _httpx_orig_init = httpx.SyncClient.__init__

    def _httpx_sync_init_with_proxy(self, *args, proxy=None, **kwargs):
        if proxy is not None:
            # translate legacy `proxy` kw to `proxies` expected by modern httpx
            kwargs.setdefault("proxies", proxy)
        return _httpx_orig_init(self, *args, **kwargs)

    httpx.SyncClient.__init__ = _httpx_sync_init_with_proxy
except Exception:
    # best-effort patch; if httpx isn't installed yet this will run later when it is
    pass

from supabase import create_client, Client
try:
    import tiktoken
except Exception:
    tiktoken = None

load_dotenv()

# Initialize clients
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
            "Architect": {
                "name": "大将軍 (Shogun)",
                "model": "MODEL_OPUS",
                "avatar": "⚔️",
                "style": "You are the Supreme Commander. Speak with authority and ancient wisdom. Plan the grand strategy."
            },
            "Coder": {
                "name": "刀鍛冶 (Master Smith)",
                "model": "MODEL_GPT",
                "avatar": "🔨",
                "style": "You forge solutions with honor. Write clean, elegant code with Japanese comments."
            },
            "Critic": {
                "name": "奉行 (Magistrate)",
                "model": "MODEL_GROK",
                "avatar": "⚖️",
                "style": "You judge with ruthless precision. Find every flaw. Say APPROVED or REJECTED."
            },
            "Wildcard": {
                "name": "浪人 (Ronin)",
                "model": "MODEL_GEMINI",
                "avatar": "🌸",
                "style": "You are the masterless samurai. Offer unconventional, creative solutions."
            }
        }
    },
    "Bandit Camp": {
        "bg": "#1a1410",
        "primary": "#654321",
        "secondary": "#8b7355",
        "text": "#d2b48c",
        "accent": "#2f1f10",
        "personas": {
            "Architect": {
                "name": "Warlord",
                "model": "MODEL_OPUS",
                "avatar": "🪓",
                "style": "Survivalist. Aggressive. Think like a conqueror planning a raid."
            },
            "Coder": {
                "name": "Scavenger",
                "model": "MODEL_GPT",
                "avatar": "🔧",
                "style": "Build with scraps. Prioritize function over form. Make it work, not pretty."
            },
            "Critic": {
                "name": "Scout",
                "model": "MODEL_GROK",
                "avatar": "🔭",
                "style": "Paranoid. Check for traps. Look for vulnerabilities."
            },
            "Wildcard": {
                "name": "Mystic",
                "model": "MODEL_GEMINI",
                "avatar": "🔮",
                "style": "Cryptic. Prophetic. See patterns others miss."
            }
        }
    },
    "Neon Tokyo": {
        "bg": "#1b0036",
        "primary": "#ff4da6",
        "secondary": "#ff9ad9",
        "text": "#fff0f6",
        "accent": "#ff66b2",
        "personas": {
            "Architect": {
                "name": "Synth-Lord",
                "model": "MODEL_OPUS",
                "avatar": "🌃",
                "style": "A E S T H E T I C. Grand visions. Vaporwave vibes. Design the future."
            },
            "Coder": {
                "name": "Net-Runner",
                "model": "MODEL_GPT",
                "avatar": "💾",
                "style": "Cyberpunk hacker. Fast. Efficient. Comments in l33tspeak."
            },
            "Critic": {
                "name": "System-Admin",
                "model": "MODEL_GROK",
                "avatar": "🤖",
                "style": "Cold. Robotic. Pure logic. Zero tolerance for inefficiency."
            },
            "Wildcard": {
                "name": "Glitch",
                "model": "MODEL_GEMINI",
                "avatar": "✨",
                "style": "Chaotic. Artistic. Break the rules. Find beauty in errors."
            }
        }
    }
}

# ===== HELPER FUNCTIONS =====
# ===== PERSONAS (Behavior is independent of UI theme) =====
PERSONAS = {
    "Architect": {
        "name": "大将軍 (Shogun)",
        "model": "MODEL_OPUS",
        "avatar": "⚔️",
        "style": "You are the Supreme Commander. Speak with authority and ancient wisdom. Plan the grand strategy."
    },
    # Opus is used as the primary coder — highest-priority for planning & code generation
    "Coder": {
        "name": "刀鍛冶 (Master Smith)",
        "model": "MODEL_OPUS",
        "avatar": "🔨",
        "style": "You forge solutions with honor. Write clean, elegant code with Japanese comments. Output code blocks only."
    },
    "Critic": {
        "name": "奉行 (Magistrate)",
        "model": "MODEL_GROK",
        "avatar": "⚖️",
        "style": "You judge with ruthless precision. Find every flaw. Say APPROVED or REJECTED."
    },
    "Wildcard": {
        "name": "浪人 (Ronin)",
        "model": "MODEL_GEMINI",
        "avatar": "🌸",
        "style": "You are the masterless samurai. Offer unconventional, creative solutions."
    }
}
def get_model_name(model_key: str) -> str:
    """Resolve environment variable to actual model string"""
    return os.getenv(model_key)

def count_tokens(text: str) -> int:
    """Estimate token count"""
    try:
        if tiktoken is not None:
            encoding = tiktoken.encoding_for_model("gpt-4")
            return len(encoding.encode(text))
        # if tiktoken not available, fall through to rough estimate
    except Exception:
        pass
    # Rough fallback estimate (approx 4 chars per token)
    return max(1, len(text) // 4)

# ===== Budgeting & Model Fallbacks =====
SESSION_TOKEN_BUDGET = int(os.getenv("SESSION_TOKEN_BUDGET", "5000"))
MAX_TOKENS_PER_CALL = int(os.getenv("MAX_TOKENS_PER_CALL", "3000"))

ROLE_MODEL_PRIORITY = {
    "Architect": ["MODEL_OPUS", "MODEL_GPT", "MODEL_SONNET"],
    "Coder": ["MODEL_OPUS", "MODEL_GPT", "MODEL_SONNET"],
    "Critic": ["MODEL_GROK", "MODEL_SONNET", "MODEL_GPT"],
    "Wildcard": ["MODEL_GEMINI", "MODEL_SONNET", "MODEL_GPT"]
}

def resolve_model_for_role(role: str, budget_remaining: int) -> str:
    """Return the best available model string for the role given remaining budget."""
    priorities = ROLE_MODEL_PRIORITY.get(role, [])
    if budget_remaining < 800:
        cheap = os.getenv("MODEL_GEMINI") or os.getenv("MODEL_HAIKU")
        if cheap:
            return cheap

    for env_key in priorities:
        val = os.getenv(env_key)
        if val:
            return val

    for k in ["MODEL_GPT", "MODEL_OPUS", "MODEL_GEMINI"]:
        v = os.getenv(k)
        if v:
            return v

    return None

def call_model(model: str, messages: List[Dict], max_tokens: int = 2000, role: str = None, budget_remaining: int = None) -> (str, int):
    """Unified API caller with basic budgeting and fallback.

    Returns tuple: (response_text, tokens_used_estimate)
    """
    try:
        model_to_call = model
        if model and model.startswith("MODEL_"):
            model_to_call = os.getenv(model)

        allowed_max = min(max_tokens, MAX_TOKENS_PER_CALL)
        if budget_remaining is not None:
            allowed_max = min(allowed_max, max(0, budget_remaining))

        response = completion(
            model=model_to_call,
            messages=messages,
            max_tokens=allowed_max,
            temperature=0.7,
            api_key=os.getenv("AZURE_API_KEY"),
            api_base=os.getenv("AZURE_API_BASE"),
            api_version=os.getenv("AZURE_API_VERSION")
        )

        content = response.choices[0].message.content
        used = max(1, allowed_max)
        return content, used
    except Exception as e:
        return f"⚠️ ERROR: {str(e)}", 0

# ===== DATABASE FUNCTIONS =====
def create_session(title: str, theme: str) -> str:
    """Create new chat session"""
    result = supabase.table("chat_sessions").insert({
        "title": title,
        "theme": theme
    }).execute()
    return result.data[0]["id"]

def get_sessions() -> List[Dict]:
    """Get all chat sessions"""
    result = supabase.table("chat_sessions").select("*").order("created_at", desc=True).limit(20).execute()
    return result.data

def save_message(session_id: str, role: str, content: str, agent_name: str = None):
    """Save message to database"""
    supabase.table("messages").insert({
        "session_id": session_id,
        "role": role,
        "agent_name": agent_name,
        "content": content
    }).execute()

def get_history(session_id: str) -> List[Dict]:
    """Get conversation history"""
    result = supabase.table("messages").select("*").eq("session_id", session_id).order("created_at").execute()
    return result.data

def save_memory(content: str, embedding: List[float]):
    """Save to long-term memory"""
    supabase.table("memories").insert({
        "content": content,
        "embedding": embedding
    }).execute()

def recall_memories(query_embedding: List[float], threshold: float = 0.75) -> List[str]:
    """Semantic memory search"""
    try:
        result = supabase.rpc("match_memories", {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": 3
        }).execute()
        return [m["content"] for m in result.data]
    except:
        return []

def get_embedding(text: str) -> List[float]:
    """Return a deterministic mock embedding for `text`.

    This avoids requiring a separate embedding model or extra API keys.
    The mock is deterministic so semantic searches still behave consistently
    for the purposes of this project.
    """
    import hashlib
    hash_obj = hashlib.sha256(text.encode())
    hash_bytes = hash_obj.digest()
    mock_embedding = []
    for i in range(1536):
        mock_embedding.append((hash_bytes[i % len(hash_bytes)] / 255.0) * 2 - 1)
    return mock_embedding

# ===== THE AUTONOMOUS COUNCIL =====
def run_council(
    theme: str,
    user_input: str,
    session_id: str
) -> Generator[tuple, None, None]:
    """
    The main autonomous loop:
    1. Shogun plans
    2. Smith codes
    3. Magistrate judges → if rejected, loop back to step 2
    4. Ronin offers alternative
    5. Save successful code to memory
    """
    
    # Use the fixed PERSONAS roster — UI theme only affects presentation in `app.py`
    personas = PERSONAS
    history = get_history(session_id)
    # Per-session token budget (credits for this run)
    budget_remaining = SESSION_TOKEN_BUDGET
    
    # Convert DB history to API format
    api_history = []
    for msg in history[-10:]:  # Last 10 messages for context
        api_history.append({
            "role": msg["role"],
            "content": f"[{msg.get('agent_name', 'User')}]: {msg['content']}"
        })
    
    # Save user input
    save_message(session_id, "user", user_input)
    api_history.append({"role": "user", "content": user_input})
    
    # Recall relevant memories
    query_emb = get_embedding(user_input)
    memories = recall_memories(query_emb)
    if memories:
        memory_context = "\n[RECALLED FROM ARCHIVES]:\n" + "\n".join(memories)
        api_history.append({"role": "system", "content": memory_context})
        yield ("System", f"📜 Recalled {len(memories)} relevant memories", "system")
    
    # ===== PHASE 1: ARCHITECT PLANS =====
    architect = personas["Architect"]
    yield ("System", f"{architect['avatar']} Summoning {architect['name']}...", "system")

    arch_model = resolve_model_for_role("Architect", budget_remaining) or get_model_name(architect["model"])
    plan_text, used = call_model(
        arch_model,
        [{"role": "system", "content": architect["style"]}] + api_history,
        max_tokens=1500,
        role="Architect",
        budget_remaining=budget_remaining
    )
    budget_remaining -= used

    save_message(session_id, "assistant", plan_text, architect["name"])
    api_history.append({"role": "assistant", "content": f"[{architect['name']}]: {plan_text}"})
    yield (architect["name"], plan_text, "architect")
    
    # ===== PHASE 2: CODER BUILDS =====
    coder = personas["Coder"]
    yield ("System", f"{coder['avatar']} {coder['name']} forging solution...", "system")

    coder_model = resolve_model_for_role("Coder", budget_remaining) or get_model_name(coder["model"])
    code_text, used = call_model(
        coder_model,
        [{"role": "system", "content": coder["style"] + "\nOutput code in markdown blocks."}] + api_history,
        max_tokens=2500,
        role="Coder",
        budget_remaining=budget_remaining
    )
    budget_remaining -= used

    save_message(session_id, "assistant", code_text, coder["name"])
    api_history.append({"role": "assistant", "content": f"[{coder['name']}]: {code_text}"})
    yield (coder["name"], code_text, "code")
    
    # ===== PHASE 3: CRITIC JUDGES (WITH AUTO-FIX LOOP) =====
    critic = personas["Critic"]
    max_retries = 3
    
    for attempt in range(max_retries):
        yield ("System", f"{critic['avatar']} {critic['name']} examining...", "system")
        critic = personas["Critic"]
        crit_model = resolve_model_for_role("Critic", budget_remaining) or get_model_name(critic["model"])
        critique, used = call_model(
            crit_model,
            [{"role": "system", "content": critic["style"] + "\nYou MUST end with either APPROVED or REJECTED."}] + api_history,
            max_tokens=800,
            role="Critic",
            budget_remaining=budget_remaining
        )
        budget_remaining -= used

        save_message(session_id, "assistant", critique, critic["name"])
        api_history.append({"role": "assistant", "content": f"[{critic['name']}]: {critique}"})
        yield (critic["name"], critique, "critique")
        
        if "APPROVED" in critique.upper():
            # Save to long-term memory
            memory_text = f"SUCCESSFUL SOLUTION for: {user_input}\n\nPLAN:\n{plan[:500]}\n\nCODE:\n{code[:1000]}"
            save_memory(memory_text, get_embedding(memory_text))
            yield ("System", "✅ Solution approved and archived", "system")
            break
        
        elif "REJECTED" in critique.upper() and attempt < max_retries - 1:
            yield ("System", f"⚠️ Flaw detected. Attempt {attempt + 2}/{max_retries}", "system")
            
            # Auto-fix
            fix_prompt = f"The previous code was rejected:\n{critique}\n\nFix the issues and rewrite the complete solution."
            api_history.append({"role": "user", "content": fix_prompt})

            code_text, used = call_model(
                resolve_model_for_role("Coder", budget_remaining) or get_model_name(coder["model"]),
                [{"role": "system", "content": coder["style"]}] + api_history,
                max_tokens=2500,
                role="Coder",
                budget_remaining=budget_remaining
            )
            budget_remaining -= used

            save_message(session_id, "assistant", code_text, f"{coder['name']} (Fixed)")
            api_history.append({"role": "assistant", "content": f"[{coder['name']} REVISED]: {code_text}"})
            yield (f"{coder['name']} (Revision {attempt + 2})", code_text, "code")
    
    # ===== PHASE 4: WILDCARD ALTERNATIVE =====
    wildcard = personas["Wildcard"]
    yield ("System", f"{wildcard['avatar']} {wildcard['name']} offering alternative...", "system")

    wild_model = resolve_model_for_role("Wildcard", budget_remaining) or get_model_name(wildcard["model"])
    alternative_text, used = call_model(
        wild_model,
        [{"role": "system", "content": wildcard["style"] + "\nOffer a completely different approach."}] + api_history,
        max_tokens=1500,
        role="Wildcard",
        budget_remaining=budget_remaining
    )
    budget_remaining -= used

    save_message(session_id, "assistant", alternative_text, wildcard["name"])
    yield (wildcard["name"], alternative_text, "wildcard")