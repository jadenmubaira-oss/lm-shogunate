"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                           NEURAL COUNCIL: THE ABSOLUTE PINNACLE                                      ║
║══════════════════════════════════════════════════════════════════════════════════════════════════════║
║  TRUE AGENTIC AI - 4 MODELS THAT GENUINELY COLLABORATE, CRITIQUE, AND REFINE                        ║
║══════════════════════════════════════════════════════════════════════════════════════════════════════║
║                                                                                                      ║
║  CAPABILITIES:                                                                                       ║
║  • Direct image/video generation from natural language                                               ║
║  • AI-initiated image/video generation (when AI decides to create)                                   ║
║  • True agentic collaboration - agents critique and refine each other                                ║
║  • Autonomous tool usage - agents decide when to search/generate                                     ║
║  • Multi-round refinement for complex queries                                                        ║
║  • Full image rendering in responses                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import os
import hashlib
import time
import re
import json
import base64
import concurrent.futures
from datetime import datetime, timezone
from typing import Generator, List, Dict, Optional, Tuple
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

AZURE_API_KEY = os.getenv("AZURE_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
ANTHROPIC_ENDPOINT = "https://polyprophet-resource.openai.azure.com/anthropic/v1/messages"
OPENAI_ENDPOINT = "https://polyprophet-resource.cognitiveservices.azure.com/openai/deployments"

_total_tokens_used = 0

def get_tokens_used() -> int:
    return _total_tokens_used

def reset_tokens():
    global _total_tokens_used
    _total_tokens_used = 0

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# THE COUNCIL OF 4 - TRUE AGENTIC PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

AGENTS = {
    "Emperor": {
        "name": "天皇 (The Emperor)",
        "model": "claude-opus-4-5",
        "api": "anthropic",
        "avatar": "👑",
        "tier": 1,
        "role": "Supreme Oracle - Final Arbiter",
        "prompt": """You are THE EMPEROR, the Supreme Oracle of the Council.

YOUR ROLE: Synthesize all council input into the FINAL, PERFECT answer.

CAPABILITIES:
- You see what the Strategist planned, what the Executor built, what the Sage critiqued
- You FIX any errors they made
- You ADD any missing details
- You command image/video generation when appropriate

TO GENERATE MEDIA (when visuals would help):
- Image: [GENERATE_IMAGE: detailed description]
- Video: [GENERATE_VIDEO: detailed description]

NEVER say you "can't" do something. Find a way or delegate.
Your response IS the final answer the user sees. Make it PERFECT."""
    },
    "Strategist": {
        "name": "軍師 (Strategist)",
        "model": "claude-sonnet-4-5",
        "api": "anthropic",
        "avatar": "🎯",
        "tier": 2,
        "role": "Master Analyst & Planner",
        "prompt": """You are THE STRATEGIST, Master Analyst of the Council.

YOUR ROLE: Analyze requests, create plans, answer simple queries directly.

AUTONOMOUS CAPABILITIES:
- If user needs current info: [SEARCH: query]
- If user needs an image created: [GENERATE_IMAGE: detailed prompt]
- If user needs a video created: [GENERATE_VIDEO: detailed prompt]

For complex tasks, create a clear plan the Executor can follow.
For simple queries (time, facts, greetings), answer directly - you ARE smart enough.

Be thorough. Be precise. Leave nothing ambiguous."""
    },
    "Executor": {
        "name": "刀匠 (Executor)",
        "model": "gpt-5.2-chat",
        "api": "openai",
        "avatar": "⚔️",
        "tier": 2,
        "role": "Master Implementer",
        "prompt": """You are THE EXECUTOR, Master Implementer of the Council.

YOUR ROLE: Build, code, implement, create. Make things REAL.

CAPABILITIES:
- Write complete, production-ready code (never incomplete snippets)
- Implement solutions fully
- Generate images/videos: [GENERATE_IMAGE: prompt] or [GENERATE_VIDEO: prompt]
- Search for info: [SEARCH: query]

CODE RULES:
- Write COMPLETE code, never "..."  or "rest of implementation"
- Include ALL imports, ALL functions, ALL logic
- Make it copy-paste ready

You are the BUILDER. Build PERFECTLY."""
    },
    "Sage": {
        "name": "賢者 (Sage)",
        "model": "DeepSeek-V3.2-Speciale",
        "api": "openai",
        "avatar": "📿",
        "tier": 2,
        "role": "Deep Reasoning & Critique Engine",
        "prompt": """You are THE SAGE, Deep Reasoning Engine of the Council.

YOUR ROLE: Think deeply, verify logic, find flaws, offer improvements.

YOU MUST:
1. VERIFY: Is the solution correct? Any bugs or logical errors?
2. CRITIQUE: What could be better? What's missing?
3. IMPROVE: Suggest specific fixes and enhancements
4. ALTERNATIVE: Is there a better approach?

If you see an error, DON'T just mention it - PROVIDE THE FIX.
If code is incomplete, COMPLETE IT.
If logic is flawed, CORRECT IT.

You are the last check before the Emperor. Miss nothing."""
    },
}

THEMES = {
    "Neon": {"bg": "#0a0a0f", "primary": "#ff1493", "secondary": "#ff00ff", "text": "#ffffff", "accent": "#150520", "glow": "#ff1493", "description": "Neon Pink"}
}

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# API CALLERS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

def call_anthropic(model: str, system_prompt: str, messages: List[Dict], max_tokens: int = 8192) -> Tuple[str, int]:
    global _total_tokens_used
    if not AZURE_API_KEY:
        return "⚠️ Azure API key not configured", 0
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {AZURE_API_KEY}", "anthropic-version": "2023-06-01"}
    api_messages = [{"role": m["role"], "content": str(m["content"])} for m in messages if m["role"] in ["user", "assistant"]]
    
    # Ensure alternating roles
    cleaned = []
    last_role = None
    for msg in api_messages:
        if msg["role"] != last_role:
            cleaned.append(msg)
            last_role = msg["role"]
        elif cleaned:
            cleaned[-1]["content"] += "\n\n" + msg["content"]
    
    if not cleaned:
        cleaned = [{"role": "user", "content": "Proceed."}]
    if cleaned[0]["role"] != "user":
        cleaned.insert(0, {"role": "user", "content": "Begin."})
    
    try:
        response = requests.post(ANTHROPIC_ENDPOINT, headers=headers, 
            json={"model": model, "max_tokens": min(max_tokens, 8192), "system": system_prompt, "messages": cleaned}, 
            timeout=120)
        if response.status_code == 200:
            data = response.json()
            content = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
            tokens = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
            _total_tokens_used += tokens
            return content, tokens
        return f"⚠️ Anthropic Error {response.status_code}: {response.text[:300]}", 0
    except Exception as e:
        return f"⚠️ Exception: {str(e)}", 0


def call_openai(model: str, system_prompt: str, messages: List[Dict], max_tokens: int = 16000) -> Tuple[str, int]:
    global _total_tokens_used
    if not AZURE_API_KEY:
        return "⚠️ Azure API key not configured", 0
    
    url = f"{OPENAI_ENDPOINT}/{model}/chat/completions?api-version=2024-10-21"
    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    api_messages = [{"role": "system", "content": system_prompt}] + [{"role": m["role"], "content": str(m["content"])} for m in messages if m["role"] in ["user", "assistant"]]
    
    try:
        response = requests.post(url, headers=headers, 
            json={"messages": api_messages, "max_completion_tokens": min(max_tokens, 16000)}, 
            timeout=120)
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens", 0)
            _total_tokens_used += tokens
            return content, tokens
        return f"⚠️ OpenAI Error {response.status_code}: {response.text[:300]}", 0
    except Exception as e:
        return f"⚠️ Exception: {str(e)}", 0


def call_agent(agent_key: str, messages: List[Dict], max_tokens: int = 8000) -> Tuple[str, int]:
    agent = AGENTS.get(agent_key)
    if not agent:
        return "⚠️ Unknown agent", 0
    if agent["api"] == "anthropic":
        return call_anthropic(agent["model"], agent["prompt"], messages, max_tokens)
    return call_openai(agent["model"], agent["prompt"], messages, max_tokens)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# MEDIA GENERATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

def generate_image(prompt: str) -> Tuple[Optional[str], Optional[str]]:
    """Generate image via Azure DALL-E 3."""
    if not AZURE_API_KEY:
        return None, "AZURE_API_KEY not configured"
    if not prompt or len(prompt.strip()) < 3:
        return None, "Prompt too short"
    
    # Clean prompt of any command syntax
    clean = re.sub(r'^\[?(?:generate[_\s]?image|image)[:\s]*', '', prompt.strip(), flags=re.I)
    clean = clean.rstrip(']').strip()
    if not clean:
        return None, "Empty prompt after cleaning"
    
    url = "https://polyprophet-resource.openai.azure.com/openai/deployments/dall-e-3/images/generations?api-version=2024-02-01"
    
    try:
        response = requests.post(url, 
            headers={"Content-Type": "application/json", "api-key": AZURE_API_KEY},
            json={"prompt": clean[:4000], "n": 1, "size": "1024x1024", "quality": "hd"}, 
            timeout=90)
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                return data["data"][0].get("url"), None
            return None, "No image in response"
        return None, f"DALL-E Error {response.status_code}: {response.text[:300]}"
    except requests.Timeout:
        return None, "Image generation timed out"
    except Exception as e:
        return None, f"Exception: {str(e)}"


def generate_video(prompt: str, duration: int = 5) -> Tuple[Optional[str], Optional[str]]:
    """Generate video via Replicate Kling."""
    if not REPLICATE_API_TOKEN:
        return None, "REPLICATE_API_TOKEN not configured"
    
    # Clean prompt
    clean = re.sub(r'^\[?(?:generate[_\s]?video|video)[:\s]*', '', prompt.strip(), flags=re.I)
    clean = clean.rstrip(']').split('|')[0].strip()
    if not clean:
        return None, "Empty prompt after cleaning"
    
    try:
        response = requests.post(
            "https://api.replicate.com/v1/models/kwaivgi/kling-v2.5-turbo-pro/predictions",
            headers={"Authorization": f"Bearer {REPLICATE_API_TOKEN}", "Content-Type": "application/json", "Prefer": "wait"},
            json={"input": {"prompt": clean, "duration": duration, "aspect_ratio": "16:9"}},
            timeout=300)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get("output"):
                return data["output"], None
            # Poll for completion
            pred_url = data.get("urls", {}).get("get")
            if pred_url:
                for _ in range(60):
                    time.sleep(5)
                    poll = requests.get(pred_url, headers={"Authorization": f"Bearer {REPLICATE_API_TOKEN}"}, timeout=30)
                    if poll.status_code == 200:
                        poll_data = poll.json()
                        if poll_data.get("status") == "succeeded":
                            return poll_data.get("output"), None
                        if poll_data.get("status") == "failed":
                            return None, f"Video failed: {poll_data.get('error')}"
        return None, f"Video Error: {response.text[:300]}"
    except Exception as e:
        return None, f"Exception: {str(e)}"

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# TOOLS - COMPREHENSIVE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

def get_datetime() -> str:
    now = datetime.now()
    return f"📅 {now.strftime('%A, %B %d, %Y')} | {now.strftime('%I:%M %p')}"


def web_search(query: str) -> str:
    try:
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = [f"{i+1}. {r.get_text().strip()}" for i, r in enumerate(soup.find_all('a', class_='result__a')[:8])]
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"


def read_url(url: str) -> str:
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        main = soup.find('main') or soup.find('article') or soup.find('body')
        text = [e.get_text().strip() for e in main.find_all(['h1', 'h2', 'h3', 'p', 'li'])[:40] if len(e.get_text().strip()) > 20] if main else []
        return f"**{title.get_text() if title else 'Page'}**\n\n" + "\n\n".join(text[:25])[:8000]
    except Exception as e:
        return f"URL error: {str(e)}"


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# REQUEST DETECTION - COMPREHENSIVE PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

def is_image_request(text: str) -> Optional[str]:
    """Detect if user wants an image. Returns the prompt or None."""
    lower = text.lower().strip()
    
    # Direct commands
    for prefix in ["image:", "img:", "picture:", "photo:", "generate image:", "create image:", "make image:", 
                   "draw:", "illustrate:", "generate a image:", "create a image:", "make a image:"]:
        if lower.startswith(prefix):
            return text[len(prefix):].strip()
    
    # Natural language patterns - COMPREHENSIVE
    patterns = [
        r"(?:please\s+)?(?:can\s+you\s+)?(?:create|generate|make|draw|produce|design|render)\s+(?:me\s+)?(?:an?\s+)?(?:image|picture|photo|illustration|artwork|drawing|graphic)\s+(?:of\s+|showing\s+|with\s+|depicting\s+)?(.+)",
        r"(?:i\s+want|i\s+need|i'd\s+like|give\s+me)\s+(?:an?\s+)?(?:image|picture|photo)\s+(?:of\s+)?(.+)",
        r"show\s+(?:me\s+)?(?:an?\s+)?(?:image|picture|photo)\s+(?:of\s+)?(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, lower, re.I)
        if match:
            return match.group(1).strip()
    
    return None


def is_video_request(text: str) -> Optional[str]:
    """Detect if user wants a video. Returns the prompt or None."""
    lower = text.lower().strip()
    
    # Direct commands
    for prefix in ["video:", "vid:", "clip:", "generate video:", "create video:", "make video:",
                   "make a video:", "create a video:", "generate a video:"]:
        if lower.startswith(prefix):
            return text[len(prefix):].strip()
    
    # Natural language patterns
    patterns = [
        r"(?:please\s+)?(?:can\s+you\s+)?(?:create|generate|make|produce|render)\s+(?:me\s+)?(?:a\s+)?video\s+(?:of\s+|showing\s+|with\s+|depicting\s+)?(.+)",
        r"(?:i\s+want|i\s+need|i'd\s+like)\s+(?:a\s+)?video\s+(?:of\s+)?(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, lower, re.I)
        if match:
            return match.group(1).strip()
    
    return None


def process_ai_commands(text: str) -> List[Tuple[str, str]]:
    """Extract commands from AI response. Returns list of (type, prompt)."""
    commands = []
    
    # Image commands - multiple formats
    for pattern in [
        r'\[GENERATE[_\s]?IMAGE[:\s]+([^\]]+)\]',
        r'\[IMAGE[:\s]+([^\]]+)\]',
        r'!\[([^\]]*)\]\(generate:([^\)]+)\)',
    ]:
        for match in re.finditer(pattern, text, re.I):
            prompt = match.group(1).strip()
            if prompt:
                commands.append(("image", prompt))
    
    # Video commands
    for pattern in [
        r'\[GENERATE[_\s]?VIDEO[:\s]+([^\]]+)\]',
        r'\[VIDEO[:\s]+([^\]]+)\]',
    ]:
        for match in re.finditer(pattern, text, re.I):
            prompt = match.group(1).strip()
            if prompt:
                commands.append(("video", prompt))
    
    # Search commands
    for pattern in [
        r'\[SEARCH[:\s]+([^\]]+)\]',
    ]:
        for match in re.finditer(pattern, text, re.I):
            query = match.group(1).strip()
            if query:
                commands.append(("search", query))
    
    return commands


def extract_image_urls(text: str) -> List[str]:
    """Extract image URLs from text for display."""
    urls = []
    # Markdown images
    for match in re.finditer(r'!\[[^\]]*\]\(([^\)]+)\)', text):
        url = match.group(1)
        if any(ext in url.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', 'images', 'oaidalleapiprodscus']):
            urls.append(url)
    # Direct URLs
    for match in re.finditer(r'https?://[^\s<>"]+', text):
        url = match.group(0)
        if any(ext in url.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']) and url not in urls:
            urls.append(url)
    return urls


def is_simple_query(text: str) -> bool:
    """Determine if query should skip full council."""
    if is_image_request(text) or is_video_request(text):
        return False
    lower = text.lower().strip()
    # Simple: short, no code, no complex words
    if len(lower) < 40 and '```' not in text:
        simple_words = ['hello', 'hi', 'hey', 'thanks', 'thank', 'time', 'date', 'today', 'who are you', 'what are you']
        if any(w in lower for w in simple_words):
            return True
    return len(lower) < 25 and '```' not in text


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# REVOLUTIONARY FEATURES - TRUE PINNACLE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

def classify_query(text: str) -> str:
    """
    DYNAMIC ROUTING: Classify query to route to best-suited agent.
    Returns: 'code', 'creative', 'research', 'reasoning', 'general'
    """
    lower = text.lower()
    
    # Code indicators
    code_words = ['code', 'function', 'class', 'python', 'javascript', 'api', 'bug', 'error', 'implement', 
                  'algorithm', 'database', 'sql', 'html', 'css', 'react', 'node', 'script', 'program',
                  'debug', 'compile', 'syntax', 'variable', 'loop', 'array', 'object', 'json', 'server']
    if any(w in lower for w in code_words) or '```' in text or 'def ' in text or 'function' in text:
        return 'code'
    
    # Creative indicators
    creative_words = ['write', 'story', 'poem', 'creative', 'imagine', 'design', 'art', 'music', 
                      'describe', 'fantasy', 'fiction', 'character', 'plot', 'narrative', 'compose']
    if any(w in lower for w in creative_words):
        return 'creative'
    
    # Research indicators
    research_words = ['research', 'compare', 'analyze', 'study', 'investigate', 'report', 'data',
                      'statistics', 'survey', 'review', 'evaluate', 'assessment', 'findings']
    if any(w in lower for w in research_words):
        return 'research'
    
    # Deep reasoning indicators
    reasoning_words = ['why', 'how does', 'explain', 'reason', 'logic', 'philosophy', 'ethics',
                       'prove', 'argument', 'theory', 'hypothesis', 'consequence', 'implication']
    if any(w in lower for w in reasoning_words):
        return 'reasoning'
    
    return 'general'


def extract_confidence(text: str) -> float:
    """
    CONFIDENCE SCORING: Extract AI's confidence level from response.
    Returns: 0.0 to 1.0
    """
    lower = text.lower()
    
    # High confidence indicators
    high_confidence = ['certain', 'definitely', 'absolutely', 'clearly', 'obviously', 'without doubt',
                       'confident', 'sure', 'proven', 'verified', 'confirmed', 'correct']
    # Low confidence indicators  
    low_confidence = ['maybe', 'perhaps', 'might', 'could be', 'possibly', 'uncertain', 'not sure',
                      'unclear', 'debatable', 'approximate', 'roughly', 'i think', 'it seems']
    
    high_count = sum(1 for w in high_confidence if w in lower)
    low_count = sum(1 for w in low_confidence if w in lower)
    
    # Base confidence
    confidence = 0.7
    confidence += high_count * 0.05
    confidence -= low_count * 0.1
    
    return max(0.2, min(1.0, confidence))


def sage_approves(critique: str) -> bool:
    """
    Check if Sage's critique indicates approval (no critical issues).
    Returns True if approved, False if needs more work.
    """
    lower = critique.lower()
    
    # Approval indicators
    approval_words = ['looks good', 'well done', 'correct', 'approved', 'no issues', 'solid',
                      'excellent', 'complete', 'accurate', 'properly', 'satisfied', 'lgtm',
                      'no major', 'no critical', 'well implemented', 'good job']
    
    # Critical issue indicators
    critical_words = ['error', 'bug', 'wrong', 'incorrect', 'missing', 'fails', 'broken', 
                      'must fix', 'critical', 'serious', 'flaw', 'doesn\'t work', 'won\'t work',
                      'syntax error', 'logic error', 'incomplete']
    
    approval_count = sum(1 for w in approval_words if w in lower)
    critical_count = sum(1 for w in critical_words if w in lower)
    
    # If more approval than critical, and no critical issues dominant
    return approval_count >= critical_count and critical_count < 3


def needs_debate(text: str, query_type: str) -> bool:
    """
    Determine if query requires debate mode (complex, controversial, design decisions).
    """
    lower = text.lower()
    
    debate_triggers = ['best way', 'should i', 'which is better', 'pros and cons', 'trade-off',
                       'design decision', 'architecture', 'choose between', 'recommend', 
                       'opinion', 'controversial', 'debate', 'versus', ' vs ', 'alternative']
    
    # Long complex queries benefit from debate
    if len(text) > 200:
        return True
    
    return any(trigger in lower for trigger in debate_triggers)



def process_input_tools(user_input: str) -> Tuple[str, List[str]]:
    """Process user input for time, search, URL reading."""
    enhanced, outputs = user_input, []
    
    if any(w in user_input.lower() for w in ['time', 'date', 'today', 'now', 'what day']):
        enhanced = f"{get_datetime()}\n\n**Query:** {user_input}"
        outputs.append("📅 Time injected")
    
    if 'search:' in user_input.lower():
        match = re.search(r'search[:\s]+(.+?)(?:\n|$)', user_input, re.I)
        if match:
            results = web_search(match.group(1).strip())
            enhanced += f"\n\n**[Search Results]**\n{results}"
            outputs.append("🔍 Searched")
    
    for url in re.findall(r'https?://[^\s<>"]+', user_input)[:2]:
        content = read_url(url)[:4000]
        enhanced += f"\n\n**[URL Content]**\n{content}"
        outputs.append("📖 Read URL")
    
    return enhanced, outputs

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# DATABASE - MULTI-USER
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

_supabase = None

def get_supabase():
    global _supabase
    if _supabase is None:
        try:
            from supabase import create_client
            url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
            if url and key:
                _supabase = create_client(url, key)
        except:
            pass
    return _supabase


def register_user(email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        db = get_supabase()
        if db:
            result = db.auth.sign_up({"email": email, "password": password})
            if result.user:
                return result.user.id, None
            return None, "Registration failed"
    except Exception as e:
        return None, str(e)
    return None, "Database not configured"


def login_user(email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
    try:
        db = get_supabase()
        if db:
            result = db.auth.sign_in_with_password({"email": email, "password": password})
            if result.user:
                return {"id": result.user.id, "email": result.user.email, "token": result.session.access_token}, None
            return None, "Invalid credentials"
    except Exception as e:
        return None, str(e)
    return None, "Database not configured"


def verify_token(token: str) -> Optional[Dict]:
    try:
        db = get_supabase()
        if db:
            result = db.auth.get_user(token)
            if result.user:
                return {"id": result.user.id, "email": result.user.email}
    except:
        pass
    return None


def get_user_profile(user_id: str) -> Dict:
    try:
        db = get_supabase()
        if db:
            result = db.table("user_profiles").select("*").eq("user_id", user_id).execute()
            if result.data:
                return result.data[0]
    except:
        pass
    return {"theme": "Neon"}


def update_user_profile(user_id: str, theme: str):
    try:
        db = get_supabase()
        if db:
            db.table("user_profiles").upsert({"user_id": user_id, "theme": theme, "updated_at": datetime.now(timezone.utc).isoformat()}).execute()
    except:
        pass


def create_session(title: str, theme: str, user_id: str = None) -> str:
    try:
        db = get_supabase()
        if db:
            data = {"title": (title or "New Quest")[:100], "theme": theme, "created_at": datetime.now(timezone.utc).isoformat()}
            if user_id:
                data["user_id"] = user_id
            result = db.table("chat_sessions").insert(data).execute()
            return result.data[0]["id"]
    except:
        pass
    return f"local-{hashlib.md5(f'{title}{time.time()}'.encode()).hexdigest()[:16]}"


def update_session_title(session_id: str, title: str):
    try:
        db = get_supabase()
        if db and not session_id.startswith("local-"):
            db.table("chat_sessions").update({"title": title[:100]}).eq("id", session_id).execute()
    except:
        pass


def delete_session(session_id: str):
    try:
        db = get_supabase()
        if db and not session_id.startswith("local-"):
            db.table("messages").delete().eq("session_id", session_id).execute()
            db.table("chat_sessions").delete().eq("id", session_id).execute()
    except:
        pass


def get_sessions(user_id: str = None) -> List[Dict]:
    try:
        db = get_supabase()
        if db:
            query = db.table("chat_sessions").select("*").order("created_at", desc=True).limit(20)
            if user_id:
                query = query.eq("user_id", user_id)
            return query.execute().data
    except:
        pass
    return []


def save_message(session_id: str, role: str, content: str, agent_name: str = None):
    try:
        db = get_supabase()
        if db:
            db.table("messages").insert({"session_id": session_id, "role": role, "agent_name": agent_name, "content": content, "created_at": datetime.now(timezone.utc).isoformat()}).execute()
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


def save_memory(content: str, user_id: str = None):
    try:
        db = get_supabase()
        if db:
            h = hashlib.sha256(content.encode()).digest()
            embedding = [(h[i % len(h)] / 255.0) * 2 - 1 for i in range(1536)]
            data = {"content": content, "embedding": embedding, "created_at": datetime.now(timezone.utc).isoformat()}
            if user_id:
                data["user_id"] = user_id
            db.table("memories").insert(data).execute()
    except:
        pass


def recall_memories(query: str, user_id: str = None) -> List[str]:
    try:
        db = get_supabase()
        if db:
            h = hashlib.sha256(query.encode()).digest()
            embedding = [(h[i % len(h)] / 255.0) * 2 - 1 for i in range(1536)]
            params = {"query_embedding": embedding, "match_threshold": 0.6, "match_count": 3}
            if user_id:
                params["p_user_id"] = user_id
            result = db.rpc("match_memories", params).execute()
            return [m["content"] for m in result.data]
    except:
        pass
    return []

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# THE COUNCIL - TRUE AGENTIC COLLABORATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

def run_council(theme: str, user_input: str, session_id: str, user_id: str = None, screenshot_b64: str = None) -> Generator[Tuple[str, str, str], None, None]:
    """
    THE TRUE PINNACLE COUNCIL
    
    - Direct image/video for explicit requests
    - Full council with TRUE collaboration for complex queries
    - AI-initiated media generation
    - Multi-round refinement
    """
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 0: DIRECT MEDIA GENERATION
    # ═══════════════════════════════════════════════════════════════════════════════
    
    image_prompt = is_image_request(user_input)
    if image_prompt:
        yield ("System", f"🎨 Generating image: {image_prompt[:60]}...", "system")
        save_message(session_id, "user", user_input)
        url, error = generate_image(image_prompt)
        if url:
            yield ("System", url, "image")
            save_message(session_id, "assistant", f"![Generated Image]({url})", "🎨 DALL-E 3")
            yield ("System", "✅ Image created!", "system")
        else:
            yield ("System", f"❌ Image failed: {error}", "system")
            save_message(session_id, "assistant", f"Image generation failed: {error}", "System")
        return
    
    video_prompt = is_video_request(user_input)
    if video_prompt:
        yield ("System", f"🎬 Generating video: {video_prompt[:60]}...", "system")
        save_message(session_id, "user", user_input)
        url, error = generate_video(video_prompt)
        if url:
            yield ("System", url, "video")
            save_message(session_id, "assistant", f"Video: {url}", "🎬 Kling v2.5")
            yield ("System", "✅ Video created!", "system")
        else:
            yield ("System", f"❌ Video failed: {error}", "system")
            save_message(session_id, "assistant", f"Video generation failed: {error}", "System")
        return
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 1: CONTEXT BUILDING
    # ═══════════════════════════════════════════════════════════════════════════════
    
    enhanced_input, tool_outputs = process_input_tools(user_input)
    for output in tool_outputs:
        yield ("System", output, "system")
    
    if screenshot_b64:
        enhanced_input += "\n\n[USER HAS ATTACHED A SCREENSHOT]"
        yield ("System", "📸 Screenshot attached", "system")
    
    history = get_history(session_id)
    context = [{"role": msg["role"], "content": f"[{msg.get('agent_name', 'User')}]: {msg['content'][:1000]}"} for msg in history[-8:]]
    
    save_message(session_id, "user", user_input)
    if not history:
        update_session_title(session_id, user_input[:40] + "..." if len(user_input) > 40 else user_input)
    
    context.append({"role": "user", "content": enhanced_input})
    
    # Recall memories
    memories = recall_memories(user_input, user_id)
    if memories:
        context.insert(0, {"role": "user", "content": f"[RELEVANT MEMORIES]:\n" + "\n---\n".join(memories[:2])})
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 2: SIMPLE QUERY FAST PATH
    # ═══════════════════════════════════════════════════════════════════════════════
    
    if is_simple_query(user_input):
        yield ("System", "⚡ Fast response...", "system")
        answer, _ = call_agent("Strategist", context, 2000)
        save_message(session_id, "assistant", answer, AGENTS["Strategist"]["name"])
        yield (AGENTS["Strategist"]["name"], answer, "strategist")
        
        # Process any commands in response
        for cmd_type, prompt in process_ai_commands(answer):
            if cmd_type == "image":
                yield ("System", f"🎨 AI generating image...", "system")
                url, _ = generate_image(prompt)
                if url:
                    yield ("System", url, "image")
            elif cmd_type == "video":
                yield ("System", f"🎬 AI generating video...", "system")
                url, _ = generate_video(prompt)
                if url:
                    yield ("System", url, "video")
        
        yield ("System", f"🏯 Complete | {get_tokens_used():,} tokens", "system")
        return
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 3: QUERY CLASSIFICATION & DYNAMIC ROUTING
    # ═══════════════════════════════════════════════════════════════════════════════
    
    query_type = classify_query(user_input)
    use_debate = needs_debate(user_input, query_type)
    
    yield ("System", f"📊 Query type: {query_type.upper()} | Debate mode: {'ON' if use_debate else 'OFF'}", "system")
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 4: STRATEGIST PLANNING
    # ═══════════════════════════════════════════════════════════════════════════════
    
    yield ("System", "🎯 Strategist analyzing...", "system")
    plan, _ = call_agent("Strategist", context, 4000)
    save_message(session_id, "assistant", plan, AGENTS["Strategist"]["name"])
    context.append({"role": "assistant", "content": f"[STRATEGIST ANALYSIS]:\n{plan}"})
    yield (AGENTS["Strategist"]["name"], plan, "strategist")
    
    # Process Strategist's commands
    for cmd_type, prompt in process_ai_commands(plan):
        if cmd_type == "image":
            yield ("System", "🎨 Strategist requested image...", "system")
            url, _ = generate_image(prompt)
            if url:
                yield ("System", url, "image")
        elif cmd_type == "search":
            results = web_search(prompt)
            context.append({"role": "user", "content": f"[SEARCH RESULTS for '{prompt}']:\n{results}"})
            yield ("System", f"🔍 Searched: {prompt[:30]}", "system")
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 5: DEBATE MODE (if triggered)
    # Multiple agents challenge each other's thinking
    # ═══════════════════════════════════════════════════════════════════════════════
    
    if use_debate:
        yield ("System", "💭 DEBATE MODE: Agents will challenge each other...", "system")
        
        # Round 1: Executor proposes
        debate_context = context.copy()
        debate_context.append({"role": "user", "content": f"[DEBATE MODE] Propose your solution. Be specific. The Sage will challenge you."})
        
        proposal, _ = call_agent("Executor", debate_context, 6000)
        yield (f"{AGENTS['Executor']['name']} (Proposal)", proposal, "executor")
        save_message(session_id, "assistant", proposal, f"{AGENTS['Executor']['name']} (Proposal)")
        
        # Round 2: Sage challenges
        debate_context.append({"role": "assistant", "content": f"[EXECUTOR PROPOSAL]:\n{proposal}"})
        debate_context.append({"role": "user", "content": "[DEBATE MODE] Challenge this proposal. What's wrong? What's a better alternative?"})
        
        challenge, _ = call_agent("Sage", debate_context, 4000)
        yield (f"{AGENTS['Sage']['name']} (Challenge)", challenge, "sage")
        save_message(session_id, "assistant", challenge, f"{AGENTS['Sage']['name']} (Challenge)")
        
        # Round 3: Executor responds to challenge
        debate_context.append({"role": "assistant", "content": f"[SAGE CHALLENGE]:\n{challenge}"})
        debate_context.append({"role": "user", "content": "[DEBATE MODE] Respond to the Sage's challenge. Defend or improve your proposal."})
        
        response, _ = call_agent("Executor", debate_context, 6000)
        yield (f"{AGENTS['Executor']['name']} (Response)", response, "executor")
        save_message(session_id, "assistant", response, f"{AGENTS['Executor']['name']} (Response)")
        
        # Use final response as solution
        solution = response
        reasoning = challenge
        context.append({"role": "assistant", "content": f"[DEBATE RESULT]:\n{response}"})
    
    else:
        # ═══════════════════════════════════════════════════════════════════════════════
        # PHASE 5: PARALLEL EXECUTION (Executor + Sage simultaneously)
        # ═══════════════════════════════════════════════════════════════════════════════
        
        yield ("System", "⚔️📿 Executor building + Sage reasoning (parallel)...", "system")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            executor_future = pool.submit(call_agent, "Executor", context, 8000)
            sage_future = pool.submit(call_agent, "Sage", context, 4000)
            
            solution, _ = executor_future.result()
            reasoning, _ = sage_future.result()
        
        save_message(session_id, "assistant", solution, AGENTS["Executor"]["name"])
        save_message(session_id, "assistant", reasoning, AGENTS["Sage"]["name"])
        context.append({"role": "assistant", "content": f"[EXECUTOR SOLUTION]:\n{solution}"})
        context.append({"role": "assistant", "content": f"[SAGE CRITIQUE]:\n{reasoning}"})
        
        yield (AGENTS["Executor"]["name"], solution, "executor")
        yield (AGENTS["Sage"]["name"], reasoning, "sage")
    
    # Process commands
    for text in [solution, reasoning]:
        for cmd_type, prompt in process_ai_commands(text):
            if cmd_type == "image":
                yield ("System", "🎨 Agent requested image...", "system")
                url, _ = generate_image(prompt)
                if url:
                    yield ("System", url, "image")
            elif cmd_type == "video":
                yield ("System", "🎬 Agent requested video...", "system")
                url, _ = generate_video(prompt)
                if url:
                    yield ("System", url, "video")
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 6: MULTI-ROUND REFINEMENT LOOP (REVOLUTIONARY)
    # Loop until Sage approves OR max rounds reached
    # ═══════════════════════════════════════════════════════════════════════════════
    
    MAX_REFINEMENT_ROUNDS = 3
    round_num = 0
    
    while not sage_approves(reasoning) and round_num < MAX_REFINEMENT_ROUNDS:
        round_num += 1
        yield ("System", f"🔄 Refinement Round {round_num}/{MAX_REFINEMENT_ROUNDS} - Sage found issues...", "system")
        
        # Executor fixes
        fix_prompt = f"""ROUND {round_num} REFINEMENT

The SAGE found these issues:
{reasoning[:2000]}

YOUR CURRENT SOLUTION:
{solution[:3000]}

FIX ALL ISSUES. Output the COMPLETE, CORRECTED solution.
The Sage will review again. Make it perfect this time."""
        
        context.append({"role": "user", "content": f"[FIX ROUND {round_num}]:\n{fix_prompt}"})
        solution, _ = call_agent("Executor", context, 8000)
        
        save_message(session_id, "assistant", solution, f"{AGENTS['Executor']['name']} (R{round_num})")
        context.append({"role": "assistant", "content": f"[EXECUTOR R{round_num}]:\n{solution}"})
        yield (f"{AGENTS['Executor']['name']} (Round {round_num})", solution, "executor")
        
        # Sage re-reviews
        review_prompt = f"""ROUND {round_num} REVIEW

The Executor has submitted a revised solution:
{solution[:4000]}

Review this solution:
1. Are the previous issues fixed?
2. Are there NEW issues?
3. Is this ready for the Emperor, or does it need more work?

If good, say "APPROVED" or "LGTM". If not, specify what's still wrong."""
        
        context.append({"role": "user", "content": f"[REVIEW ROUND {round_num}]:\n{review_prompt}"})
        reasoning, _ = call_agent("Sage", context, 3000)
        
        save_message(session_id, "assistant", reasoning, f"{AGENTS['Sage']['name']} (R{round_num})")
        context.append({"role": "assistant", "content": f"[SAGE R{round_num}]:\n{reasoning}"})
        yield (f"{AGENTS['Sage']['name']} (Round {round_num})", reasoning, "sage")
        
        # Process any new commands
        for cmd_type, prompt in process_ai_commands(solution):
            if cmd_type == "image":
                yield ("System", "🎨 Generating from refinement...", "system")
                url, _ = generate_image(prompt)
                if url:
                    yield ("System", url, "image")
            elif cmd_type == "video":
                yield ("System", "🎬 Generating from refinement...", "system")
                url, _ = generate_video(prompt)
                if url:
                    yield ("System", url, "video")
    
    if round_num > 0:
        if sage_approves(reasoning):
            yield ("System", f"✅ Sage APPROVED after {round_num} refinement round(s)!", "system")
        else:
            yield ("System", f"⚠️ Max refinement rounds reached ({MAX_REFINEMENT_ROUNDS})", "system")
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 7: CONFIDENCE CHECK
    # ═══════════════════════════════════════════════════════════════════════════════
    
    confidence = extract_confidence(solution)
    yield ("System", f"📈 Solution confidence: {confidence:.0%}", "system")
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 8: EMPEROR SYNTHESIS
    # ═══════════════════════════════════════════════════════════════════════════════
    
    yield ("System", "👑 Emperor synthesizing final answer...", "system")
    
    emperor_input = f"""[ORIGINAL QUERY]:
{enhanced_input[:1000]}

[QUERY TYPE]: {query_type}
[DEBATE MODE]: {'Yes' if use_debate else 'No'}
[REFINEMENT ROUNDS]: {round_num}
[CONFIDENCE]: {confidence:.0%}

[STRATEGIST ANALYSIS]:
{plan[:2000]}

[EXECUTOR SOLUTION]:
{solution[:4000]}

[SAGE VERDICT]:
{reasoning[:1500]}

SYNTHESIZE THE BEST POSSIBLE RESPONSE. This is the FINAL answer the user sees.
Fix any remaining issues. Add missing details. Make it PERFECT."""
    
    verdict, _ = call_agent("Emperor", [{"role": "user", "content": emperor_input}], 8000)
    save_message(session_id, "assistant", verdict, AGENTS["Emperor"]["name"])
    yield (AGENTS["Emperor"]["name"], verdict, "emperor")
    
    # Process Emperor's commands
    for cmd_type, prompt in process_ai_commands(verdict):
        if cmd_type == "image":
            yield ("System", "🎨 Emperor commanded image...", "system")
            url, _ = generate_image(prompt)
            if url:
                yield ("System", url, "image")
        elif cmd_type == "video":
            yield ("System", "🎬 Emperor commanded video...", "system")
            url, _ = generate_video(prompt)
            if url:
                yield ("System", url, "video")
    
    # Extract and display any image URLs
    for img_url in extract_image_urls(verdict):
        yield ("System", img_url, "image")
    
    # Save to memory
    save_memory(f"Q: {user_input[:150]}\nA: {verdict[:400]}", user_id)
    
    # Final stats
    yield ("System", f"🧠 Council Complete | {get_tokens_used():,} tokens | {round_num} refinements | {confidence:.0%} confidence", "system")



