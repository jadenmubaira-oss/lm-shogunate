import os
import json
from typing import Generator, List, Dict
from dotenv import load_dotenv
from litellm import completion
from supabase import create_client, Client
import tiktoken

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
        "bg": "#0d0221",
        "primary": "#ff006e",
        "secondary": "#8338ec",
        "text": "#ffffff",
        "accent": "#fb5607",
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
def get_model_name(model_key: str) -> str:
    """Resolve environment variable to actual model string"""
    return os.getenv(model_key)

def count_tokens(text: str) -> int:
    """Estimate token count"""
    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(text))
    except:
        return len(text) // 4  # Rough estimate

def call_model(model: str, messages: List[Dict], max_tokens: int = 2000) -> str:
    """Unified API caller with fallback"""
    try:
        response = completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            api_key=os.getenv("AZURE_API_KEY"),
            api_base=os.getenv("AZURE_API_BASE"),
            api_version=os.getenv("AZURE_API_VERSION")
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ ERROR: {str(e)}"

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
    """Get vector embedding (using a simple mock for now)"""
    # In production, use: openai.Embedding.create(input=text, model="text-embedding-ada-002")
    # For now, return mock to avoid extra API calls
    import hashlib
    hash_obj = hashlib.sha256(text.encode())
    hash_bytes = hash_obj.digest()
    # Stretch to 1536 dimensions (required by our DB schema)
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
    
    personas = THEMES[theme]["personas"]
    history = get_history(session_id)
    
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
    
    plan = call_model(
        get_model_name(architect["model"]),
        [{"role": "system", "content": architect["style"]}] + api_history,
        max_tokens=1500
    )
    
    save_message(session_id, "assistant", plan, architect["name"])
    api_history.append({"role": "assistant", "content": f"[{architect['name']}]: {plan}"})
    yield (architect["name"], plan, "architect")
    
    # ===== PHASE 2: CODER BUILDS =====
    coder = personas["Coder"]
    yield ("System", f"{coder['avatar']} {coder['name']} forging solution...", "system")
    
    code = call_model(
        get_model_name(coder["model"]),
        [{"role": "system", "content": coder["style"] + "\nOutput code in markdown blocks."}] + api_history,
        max_tokens=2500
    )
    
    save_message(session_id, "assistant", code, coder["name"])
    api_history.append({"role": "assistant", "content": f"[{coder['name']}]: {code}"})
    yield (coder["name"], code, "code")
    
    # ===== PHASE 3: CRITIC JUDGES (WITH AUTO-FIX LOOP) =====
    critic = personas["Critic"]
    max_retries = 3
    
    for attempt in range(max_retries):
        yield ("System", f"{critic['avatar']} {critic['name']} examining...", "system")
        
        critique = call_model(
            get_model_name(critic["model"]),
            [{"role": "system", "content": critic["style"] + "\nYou MUST end with either APPROVED or REJECTED."}] + api_history,
            max_tokens=800
        )
        
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
            
            code = call_model(
                get_model_name(coder["model"]),
                [{"role": "system", "content": coder["style"]}] + api_history,
                max_tokens=2500
            )
            
            save_message(session_id, "assistant", code, f"{coder['name']} (Fixed)")
            api_history.append({"role": "assistant", "content": f"[{coder['name']} REVISED]: {code}"})
            yield (f"{coder['name']} (Revision {attempt + 2})", code, "code")
    
    # ===== PHASE 4: WILDCARD ALTERNATIVE =====
    wildcard = personas["Wildcard"]
    yield ("System", f"{wildcard['avatar']} {wildcard['name']} offering alternative...", "system")
    
    alternative = call_model(
        get_model_name(wildcard["model"]),
        [{"role": "system", "content": wildcard["style"] + "\nOffer a completely different approach."}] + api_history,
        max_tokens=1500
    )
    
    save_message(session_id, "assistant", alternative, wildcard["name"])
    yield (wildcard["name"], alternative, "wildcard")