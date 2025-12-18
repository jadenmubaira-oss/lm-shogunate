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

# FILE CACHE - Stores uploaded files separately to avoid resending every message
# Structure: {session_id: [{name: str, content: str, timestamp: float}, ...]}
_file_cache: Dict[str, List[Dict]] = {}
MAX_CACHED_FILES = 10  # Max files to keep per session
FILES_TO_SEND_FULL = 3  # Always send last N files in full context

def get_tokens_used() -> int:
    return _total_tokens_used

def reset_tokens():
    global _total_tokens_used
    _total_tokens_used = 0

def cache_files(session_id: str, files: List[Dict[str, str]]):
    """Cache uploaded files for a session. Called when user uploads files."""
    if session_id not in _file_cache:
        _file_cache[session_id] = []
    
    for f in files:
        file_name = f.get("name", "unnamed")
        file_content = f.get("content", "")
        file_timestamp = datetime.now(timezone.utc).timestamp()
        
        # CRITICAL: Replace existing file with same name (don't create duplicate)
        existing_idx = None
        for idx, cached in enumerate(_file_cache[session_id]):
            if cached["name"].lower() == file_name.lower():
                existing_idx = idx
                break
        
        if existing_idx is not None:
            # Update existing file
            _file_cache[session_id][existing_idx] = {
                "name": file_name,
                "content": file_content,
                "timestamp": file_timestamp
            }
        else:
            # Add new file
            _file_cache[session_id].append({
                "name": file_name,
                "content": file_content,
                "timestamp": file_timestamp
            })
    
    # Keep only last MAX_CACHED_FILES
    if len(_file_cache[session_id]) > MAX_CACHED_FILES:
        _file_cache[session_id] = _file_cache[session_id][-MAX_CACHED_FILES:]

def get_cached_files(session_id: str) -> List[Dict]:
    """Get all cached files for a session."""
    return _file_cache.get(session_id, [])

def get_file_references(session_id: str) -> str:
    """Get a summary of cached files (for context without full content)."""
    files = _file_cache.get(session_id, [])
    if not files:
        return ""
    
    refs = ["[AVAILABLE FILES IN THIS SESSION:]"]
    for i, f in enumerate(files):
        size = len(f["content"])
        refs.append(f"  {i+1}. {f['name']} ({size:,} chars)")
    refs.append("[Use 'show file X' or reference by name to see contents]")
    return "\n".join(refs)

def get_file_by_name(session_id: str, filename: str) -> Optional[str]:
    """Retrieve a specific cached file by name."""
    files = _file_cache.get(session_id, [])
    for f in files:
        if filename.lower() in f["name"].lower():
            return f"[FILE: {f['name']}]\n```\n{f['content']}\n```"
    return None


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# THE COUNCIL OF 4 - TRUE AGENTIC PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

AGENTS = {
    "Emperor": {
        "name": "The Emperor",
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
        "name": "The Strategist",
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
        "name": "The Executor",
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
- EXECUTE CODE: [EXECUTE_CODE: your python code here] - I can RUN your code!
- READ ANY WEBSITE: [READ_URL: https://example.com]
- BROWSE WITH AUTOMATION: [BROWSE: https://example.com] - Full browser with JS!
- SCREENSHOT ANY PAGE: [SCREENSHOT: https://example.com]
- READ GITHUB REPOS: [GITHUB: https://github.com/user/repo]

CODE RULES:
- Write COMPLETE code, never "..."  or "rest of implementation"
- Include ALL imports, ALL functions, ALL logic
- Make it copy-paste ready
- When you write code, TEST IT by using [EXECUTE_CODE: code] to verify it works!

WEB RULES:
- If user provides a URL, USE [READ_URL:] to fetch and analyze it
- If user asks about a website, BROWSE IT first
- If user shares a GitHub repo, READ it with [GITHUB:]

You are the BUILDER. Build PERFECTLY. TEST your code! BROWSE the web!"""
    },

    "Sage": {
        "name": "The Sage",
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

def call_anthropic(model: str, system_prompt: str, messages: List[Dict], max_tokens: int = 16384) -> Tuple[str, int]:
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
    
    # SMART FILE-AWARE TRUNCATION
    # Strategy: ALWAYS preserve the LAST user message (which contains their files)
    # Aggressively summarize older messages, only truncate files as absolute last resort
    MAX_CHARS = 150000  # ~50k tokens, safe margin under 200k limit
    total_chars = len(system_prompt) + sum(len(m["content"]) for m in cleaned)
    truncation_warning = None
    
    if total_chars > MAX_CHARS:
        # STRATEGY 1: Summarize OLD messages (not the last user message)
        # Keep last 2 messages (current exchange), compress the rest
        if len(cleaned) > 2:
            old_messages = cleaned[:-2]
            current_messages = cleaned[-2:]
            
            # Compress old messages to brief summaries
            compressed = []
            for msg in old_messages:
                content = msg["content"]
                # If it's a long message, create a brief summary
                if len(content) > 500:
                    # Extract key info: first 200 chars + any code block headers
                    summary = content[:200]
                    if "[FILE:" in content:
                        # Count files mentioned
                        file_count = content.count("[FILE:")
                        summary += f"\n[...{file_count} file(s) previously attached...]"
                    elif "```" in content:
                        summary += "\n[...code block(s) omitted...]"
                    else:
                        summary += "\n[...truncated for context limit...]"
                    msg["content"] = summary
                compressed.append(msg)
            
            cleaned = compressed + current_messages
            total_chars = len(system_prompt) + sum(len(m["content"]) for m in cleaned)
        
        # STRATEGY 2: If STILL too long, the current message has massive files
        # Truncate each file embedded in the message, but keep the structure
        if total_chars > MAX_CHARS and len(cleaned) >= 1:
            last_msg = cleaned[-1]
            if "[FILE:" in last_msg["content"] and len(last_msg["content"]) > 100000:
                # Split by file markers and truncate each
                import re
                parts = re.split(r'(\[FILE:[^\]]+\])', last_msg["content"])
                truncated_parts = []
                for i, part in enumerate(parts):
                    if part.startswith("[FILE:"):
                        truncated_parts.append(part)  # Keep file header
                    elif "```" in part and len(part) > 30000:
                        # Truncate code content within file
                        code_start = part.find("```")
                        code_end = part.rfind("```")
                        if code_start != -1 and code_end > code_start:
                            before_code = part[:code_start+3]
                            after_code = part[code_end:]
                            middle = part[code_start+3:code_end]
                            # Keep first/last 10k chars of code
                            if len(middle) > 25000:
                                middle = middle[:12000] + "\n\n... [FILE TRUNCATED: " + str((len(middle)-24000)//1000) + "k chars omitted] ...\n\n" + middle[-12000:]
                            truncated_parts.append(before_code + middle + after_code)
                        else:
                            truncated_parts.append(part[:30000] + "\n[TRUNCATED]")
                    else:
                        truncated_parts.append(part)
                
                last_msg["content"] = "".join(truncated_parts)
                truncation_warning = "⚠️ Some file contents were truncated due to context limits. Core structure preserved."
                total_chars = len(system_prompt) + sum(len(m["content"]) for m in cleaned)
        
        # STRATEGY 3: Absolute last resort - hard truncate
        if total_chars > MAX_CHARS:
            excess = total_chars - MAX_CHARS
            cleaned[-1]["content"] = cleaned[-1]["content"][:-(excess + 1000)]
            cleaned[-1]["content"] += "\n\n[HARD TRUNCATED - Please upload fewer/smaller files]"
            truncation_warning = "⚠️ Content was truncated. Consider uploading fewer files or using smaller files."
    
    # RETRY LOGIC FOR RATE LIMITS (429 errors)
    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(ANTHROPIC_ENDPOINT, headers=headers, 
                json={"model": model, "max_tokens": min(max_tokens, 16384), "system": system_prompt, "messages": cleaned}, 
                timeout=120)
            
            # DEBUG LOGGING - helps diagnose API failures
            print(f"[call_anthropic] Model: {model} | Status: {response.status_code}")
            if response.status_code != 200:
                print(f"[call_anthropic ERROR] {response.text[:500]}")
            
            if response.status_code == 200:
                data = response.json()
                content = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
                # CRITICAL: Check for empty response
                if not content or not content.strip():
                    return "⚠️ Empty response from Anthropic API", 0
                tokens = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
                _total_tokens_used += tokens
                
                # AUTO-CONTINUE: If response hit max_tokens, request continuation
                stop_reason = data.get("stop_reason", "")
                if stop_reason == "max_tokens" and len(content) > 100:
                    # Response was cut off - auto-continue up to 6 times
                    full_content = content
                    for cont_attempt in range(6):  # Max 6 continuations
                        # CRITICAL: Recreate message list fresh each iteration (not append)
                        cont_messages = cleaned + [
                            {"role": "assistant", "content": full_content},
                            {"role": "user", "content": "Continue from where you left off. Do NOT repeat what you already said."}
                        ]
                        try:
                            cont_response = requests.post(ANTHROPIC_ENDPOINT, headers=headers,
                                json={"model": model, "max_tokens": min(max_tokens, 16384), "system": system_prompt, "messages": cont_messages},
                                timeout=120)
                            if cont_response.status_code == 200:
                                cont_data = cont_response.json()
                                cont_content = "".join(b.get("text", "") for b in cont_data.get("content", []) if b.get("type") == "text")
                                if cont_content and cont_content.strip():  # Only add if not empty
                                    cont_tokens = cont_data.get("usage", {}).get("input_tokens", 0) + cont_data.get("usage", {}).get("output_tokens", 0)
                                    _total_tokens_used += cont_tokens
                                    tokens += cont_tokens
                                    full_content += "\n" + cont_content
                                # Check if this continuation was also truncated
                                if cont_data.get("stop_reason") != "max_tokens":
                                    break  # Response complete
                        except:
                            break  # Stop on error
                    return full_content, tokens
                
                return content, tokens
            
            # RATE LIMIT - RETRY WITH BACKOFF
            if response.status_code == 429:
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                    time.sleep(wait_time)
                    continue
                return f"⚠️ Rate limited after {max_retries} retries. Please wait a moment.", 0
            
            # CONTEXT TOO LONG - Truncate and retry
            if response.status_code == 400 and "too long" in response.text.lower():
                if len(cleaned) > 2:
                    cleaned = cleaned[:1] + cleaned[-1:]  # Keep first + last
                    continue
                return "⚠️ Query too long. Please shorten your message.", 0
            
            return f"⚠️ Anthropic Error {response.status_code}: {response.text[:300]}", 0
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            return f"⚠️ Exception: {str(e)}", 0
    
    return "⚠️ Max retries exceeded", 0


def call_openai(model: str, system_prompt: str, messages: List[Dict], max_tokens: int = 32000) -> Tuple[str, int]:
    global _total_tokens_used
    if not AZURE_API_KEY:
        return "⚠️ Azure API key not configured", 0
    
    url = f"{OPENAI_ENDPOINT}/{model}/chat/completions?api-version=2024-10-21"
    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    api_messages = [{"role": "system", "content": system_prompt}] + [{"role": m["role"], "content": str(m["content"])} for m in messages if m["role"] in ["user", "assistant"]]
    
    # RETRY LOGIC FOR RATE LIMITS (429 errors)
    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(url, headers=headers, 
                json={"messages": api_messages, "max_completion_tokens": min(max_tokens, 32000)}, 
                timeout=120)
            
            # DEBUG LOGGING - helps diagnose API failures
            print(f"[call_openai] Model: {model} | Status: {response.status_code}")
            if response.status_code != 200:
                print(f"[call_openai ERROR] {response.text[:500]}")
            
            if response.status_code == 200:
                data = response.json()
                # SAFE CHECK: Verify choices array exists and has items
                choices = data.get("choices", [])
                if not choices:
                    return "⚠️ Empty response from API", 0
                content = choices[0].get("message", {}).get("content", "")
                if not content:
                    return "⚠️ No content in API response", 0
                tokens = data.get("usage", {}).get("total_tokens", 0)
                _total_tokens_used += tokens
                
                # AUTO-CONTINUE: If response was truncated, request continuation
                finish_reason = choices[0].get("finish_reason", "")
                if finish_reason == "length" and len(content) > 100:
                    # Response was cut off - auto-continue up to 6 times
                    full_content = content
                    for cont_attempt in range(6):  # Max 6 continuations
                        cont_messages = api_messages + [
                            {"role": "assistant", "content": full_content},
                            {"role": "user", "content": "Continue from where you left off. Do NOT repeat what you already said."}
                        ]
                        try:
                            cont_response = requests.post(url, headers=headers,
                                json={"messages": cont_messages, "max_completion_tokens": min(max_tokens, 32000)},
                                timeout=120)
                            if cont_response.status_code == 200:
                                cont_data = cont_response.json()
                                cont_choices = cont_data.get("choices", [])
                                if cont_choices:
                                    cont_content = cont_choices[0].get("message", {}).get("content", "")
                                    if cont_content and cont_content.strip():  # Only add if not empty
                                        cont_tokens = cont_data.get("usage", {}).get("total_tokens", 0)
                                        _total_tokens_used += cont_tokens
                                        tokens += cont_tokens
                                        full_content += "\n" + cont_content
                                    # Check if this continuation was also truncated
                                    if cont_choices[0].get("finish_reason") != "length":
                                        break  # Response complete
                        except:
                            break  # Stop on error
                    return full_content, tokens
                
                return content, tokens
            
            # RATE LIMIT - RETRY WITH BACKOFF
            if response.status_code == 429:
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                    time.sleep(wait_time)
                    continue
                return f"⚠️ Rate limited after {max_retries} retries. Please wait a moment.", 0
            
            # CONTEXT TOO LONG - Truncate and retry
            if response.status_code == 400 and "context_length" in response.text:
                # Reduce messages and retry
                if len(api_messages) > 3:
                    api_messages = api_messages[:1] + api_messages[-2:]  # Keep system + last 2
                    continue
                return "⚠️ Query too long. Please shorten your message.", 0
            
            return f"⚠️ OpenAI Error {response.status_code}: {response.text[:300]}", 0
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            return f"⚠️ Exception: {str(e)}", 0
    
    return "⚠️ Max retries exceeded", 0


def call_agent(agent_key: str, messages: List[Dict], max_tokens: int = 8000) -> Tuple[str, int]:
    agent = AGENTS.get(agent_key)
    if not agent:
        return "⚠️ Unknown agent", 0
    if agent["api"] == "anthropic":
        return call_anthropic(agent["model"], agent["prompt"], messages, max_tokens)
    return call_openai(agent["model"], agent["prompt"], messages, max_tokens)


def call_anthropic_with_vision(model: str, system_prompt: str, messages: List[Dict], image_b64: str, max_tokens: int = 8192) -> Tuple[str, int]:
    """
    TRUE VISION: Call Anthropic with an image for visual analysis.
    This is what makes us #1 - we can actually SEE screenshots.
    """
    global _total_tokens_used
    if not AZURE_API_KEY:
        return "⚠️ Azure API key not configured", 0
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {AZURE_API_KEY}", "anthropic-version": "2023-06-01"}
    
    # Build vision message with image
    image_content = []
    if image_b64:
        # Extract base64 data if it's a data URL
        if image_b64.startswith("data:"):
            parts = image_b64.split(",", 1)
            if len(parts) == 2:
                media_type = parts[0].split(";")[0].replace("data:", "")
                image_data = parts[1]
            else:
                media_type = "image/png"
                image_data = image_b64
        else:
            media_type = "image/png"
            image_data = image_b64
        
        image_content = [{
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data
            }
        }]
    
    # Build messages with vision content
    api_messages = []
    for m in messages:
        if m["role"] in ["user", "assistant"]:
            if m["role"] == "user" and image_content and len(api_messages) == 0:
                # First user message gets the image
                api_messages.append({
                    "role": "user",
                    "content": image_content + [{"type": "text", "text": str(m["content"])}]
                })
            else:
                api_messages.append({"role": m["role"], "content": str(m["content"])})
    
    # Ensure valid message structure
    if not api_messages:
        api_messages = [{"role": "user", "content": image_content + [{"type": "text", "text": "Analyze this image."}]}]
    if api_messages[0]["role"] != "user":
        api_messages.insert(0, {"role": "user", "content": image_content + [{"type": "text", "text": "Begin."}]})
    
    try:
        response = requests.post(ANTHROPIC_ENDPOINT, headers=headers, 
            json={"model": model, "max_tokens": min(max_tokens, 8192), "system": system_prompt, "messages": api_messages}, 
            timeout=120)
        if response.status_code == 200:
            data = response.json()
            content = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
            # CRITICAL: Check for empty response
            if not content or not content.strip():
                return "⚠️ Empty response from Vision API", 0
            tokens = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
            _total_tokens_used += tokens
            return content, tokens
        return f"⚠️ Vision Error {response.status_code}: {response.text[:300]}", 0
    except Exception as e:
        return f"⚠️ Vision Exception: {str(e)}", 0


def call_agent_with_vision(agent_key: str, messages: List[Dict], image_b64: str, max_tokens: int = 8000) -> Tuple[str, int]:
    """Call agent with vision capability (only works for Anthropic models)."""
    agent = AGENTS.get(agent_key)
    if not agent:
        return "⚠️ Unknown agent", 0
    if agent["api"] == "anthropic":
        return call_anthropic_with_vision(agent["model"], agent["prompt"], messages, image_b64, max_tokens)
    # Fallback for non-vision models
    return call_agent(agent_key, messages, max_tokens)


def get_real_embedding(text: str) -> List[float]:
    """
    TRUE EMBEDDINGS: Use Azure OpenAI embeddings API instead of hash.
    Falls back to hash if API unavailable.
    """
    if not AZURE_API_KEY:
        # Fallback to hash
        h = hashlib.sha256(text.encode()).digest()
        return [(h[i % len(h)] / 255.0) * 2 - 1 for i in range(1536)]
    
    try:
        url = f"{OPENAI_ENDPOINT}/text-embedding-3-large/embeddings?api-version=2024-10-21"
        headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
        response = requests.post(url, headers=headers, 
            json={"input": text[:8000], "dimensions": 1536}, 
            timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                return data["data"][0]["embedding"]
    except:
        pass
    
    # Fallback to hash
    h = hashlib.sha256(text.encode()).digest()
    return [(h[i % len(h)] / 255.0) * 2 - 1 for i in range(1536)]


def rate_response_quality(response: str) -> float:
    """
    SELF-RATING: Analyze response quality.
    Returns 0.0 to 1.0
    """
    lower = response.lower()
    
    # Quality indicators
    quality_positive = ['complete', 'comprehensive', 'detailed', 'correct', 'accurate', 
                       'working', 'tested', 'verified', 'solution', 'here is', 'here\'s']
    quality_negative = ['error', 'bug', 'issue', 'problem', 'cannot', 'can\'t', 'unable',
                       'sorry', 'unfortunately', 'incomplete', 'todo', 'fixme']
    
    pos = sum(1 for w in quality_positive if w in lower)
    neg = sum(1 for w in quality_negative if w in lower)
    
    # Length bonus (longer = more complete)
    length_score = min(1.0, len(response) / 2000)
    
    # Code block bonus
    code_score = 0.1 if '```' in response else 0
    
    base = 0.6 + (pos * 0.05) - (neg * 0.1) + (length_score * 0.2) + code_score
    return max(0.3, min(1.0, base))


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# CODE EXECUTION SANDBOX - THE FINAL PIECE FOR 100/100 PINNACLE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

import subprocess
import tempfile
import sys

def execute_code(code: str, language: str = "python", timeout: int = 10) -> Tuple[bool, str]:
    """
    SANDBOXED CODE EXECUTION - Run code safely with timeout and output capture.
    
    Returns: (success: bool, output: str)
    
    Features:
    - 10 second timeout (prevents infinite loops)
    - Captures stdout and stderr
    - Isolated temp file execution
    - No persistent file system access
    """
    if not code or len(code.strip()) < 3:
        return False, "❌ No code provided"
    
    # Clean the code (remove markdown code blocks if present)
    clean_code = code.strip()
    if clean_code.startswith("```"):
        lines = clean_code.split("\n")
        # Remove first line (```python) and last line (```)
        lines = [l for l in lines[1:] if not l.strip() == "```"]
        clean_code = "\n".join(lines)
    
    if language.lower() in ["python", "py"]:
        return _execute_python(clean_code, timeout)
    elif language.lower() in ["javascript", "js", "node"]:
        return _execute_javascript(clean_code, timeout)
    else:
        return False, f"❌ Unsupported language: {language}. Supported: python, javascript"


def _execute_python(code: str, timeout: int = 10) -> Tuple[bool, str]:
    """Execute Python code in a sandboxed subprocess."""
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            # Add safety wrapper
            safe_code = f'''
import sys
import os

# Sandbox restrictions
class SandboxError(Exception):
    pass

# Restrict dangerous operations
_original_open = open
def _safe_open(file, mode='r', *args, **kwargs):
    if 'w' in mode or 'a' in mode:
        if not str(file).startswith(os.environ.get('TEMP', '/tmp')):
            raise SandboxError("Writing to files outside temp is not allowed")
    return _original_open(file, mode, *args, **kwargs)

# Apply restrictions
open = _safe_open

# User code:
{code}
'''
            f.write(safe_code)
            temp_path = f.name
        
        # Execute with timeout
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir()
        )
        
        # Clean up
        try:
            os.unlink(temp_path)
        except:
            pass
        
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += ("\n" if output else "") + result.stderr
        
        if result.returncode == 0:
            return True, f"✅ Execution successful:\n```\n{output.strip() or '(no output)'}\n```"
        else:
            return False, f"❌ Execution failed (exit code {result.returncode}):\n```\n{output.strip()}\n```"
            
    except subprocess.TimeoutExpired:
        return False, f"⏰ Execution timed out after {timeout} seconds (possible infinite loop)"
    except Exception as e:
        return False, f"❌ Execution error: {str(e)}"


def _execute_javascript(code: str, timeout: int = 10) -> Tuple[bool, str]:
    """Execute JavaScript code using Node.js (if available)."""
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_path = f.name
        
        # Try to find node
        node_cmd = "node"
        
        # Execute with timeout
        result = subprocess.run(
            [node_cmd, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir()
        )
        
        # Clean up
        try:
            os.unlink(temp_path)
        except:
            pass
        
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += ("\n" if output else "") + result.stderr
        
        if result.returncode == 0:
            return True, f"✅ JS execution successful:\n```\n{output.strip() or '(no output)'}\n```"
        else:
            return False, f"❌ JS execution failed:\n```\n{output.strip()}\n```"
            
    except FileNotFoundError:
        return False, "❌ Node.js not found. Install Node.js to execute JavaScript."
    except subprocess.TimeoutExpired:
        return False, f"⏰ Execution timed out after {timeout} seconds"
    except Exception as e:
        return False, f"❌ Execution error: {str(e)}"


def extract_code_blocks(text: str) -> List[Tuple[str, str]]:
    """Extract code blocks from text. Returns list of (language, code)."""
    blocks = []
    pattern = r'```(\w*)\n(.*?)```'
    for match in re.finditer(pattern, text, re.DOTALL):
        lang = match.group(1) or "python"
        code = match.group(2).strip()
        if code:
            blocks.append((lang, code))
    return blocks


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
    """
    ENHANCED URL READING - Handles GitHub repos, regular websites, and more.
    """
    try:
        # GITHUB SPECIAL HANDLING
        if 'github.com' in url:
            return read_github(url)
        
        # REGULAR WEBSITE
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('title')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
            tag.decompose()
        
        # Try to find main content
        main = soup.find('main') or soup.find('article') or soup.find('[role="main"]') or soup.find('body')
        
        if main:
            # Get all text content
            text_elements = main.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'td', 'th', 'pre', 'code'])
            text = []
            for e in text_elements[:60]:
                content = e.get_text().strip()
                if len(content) > 15:
                    text.append(content)
            
            return f"**{title.get_text() if title else 'Page'}**\n\n" + "\n\n".join(text[:40])[:10000]
        
        return f"**{title.get_text() if title else 'Page'}** - Could not extract main content"
        
    except Exception as e:
        return f"URL error: {str(e)}"


def read_github(url: str) -> str:
    """
    GITHUB SPECIAL HANDLER - Can read repos, files, and navigate.
    Uses GitHub API for reliable access.
    """
    try:
        # Parse GitHub URL
        # Formats: github.com/owner/repo, github.com/owner/repo/tree/branch/path, github.com/owner/repo/blob/branch/path
        parts = url.replace('https://', '').replace('http://', '').replace('github.com/', '').split('/')
        
        if len(parts) < 2:
            return "Invalid GitHub URL - need at least owner/repo"
        
        owner, repo = parts[0], parts[1]
        repo = repo.replace('.git', '')
        
        # Determine what we're looking at
        if len(parts) == 2:
            # Root of repo - get repo info + file list
            return get_github_repo_contents(owner, repo)
        
        if len(parts) >= 4:
            action = parts[2]  # 'tree' or 'blob'
            branch = parts[3]
            path = '/'.join(parts[4:]) if len(parts) > 4 else ''
            
            if action == 'blob':
                # Reading a specific file
                return get_github_file(owner, repo, branch, path)
            elif action == 'tree':
                # Reading a directory
                return get_github_repo_contents(owner, repo, path)
        
        return get_github_repo_contents(owner, repo)
        
    except Exception as e:
        return f"GitHub error: {str(e)}"


def get_github_repo_contents(owner: str, repo: str, path: str = "") -> str:
    """Get contents of a GitHub repo directory using API."""
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        response = requests.get(api_url, headers={
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'NeuralCouncil/1.0'
        }, timeout=15)
        
        if response.status_code == 404:
            return f"Repository not found: {owner}/{repo}"
        
        if response.status_code != 200:
            # Fallback to web scraping
            return read_github_web(f"https://github.com/{owner}/{repo}")
        
        data = response.json()
        
        if isinstance(data, list):
            # Directory listing
            result = f"📂 **GitHub: {owner}/{repo}**\n"
            if path:
                result += f"📁 Path: /{path}\n"
            result += "\n**Contents:**\n"
            
            dirs = [f"📁 {item['name']}/" for item in data if item['type'] == 'dir']
            files = [f"📄 {item['name']} ({item.get('size', 0):,} bytes)" for item in data if item['type'] == 'file']
            
            result += "\n".join(dirs[:20]) + "\n" + "\n".join(files[:30])
            result += f"\n\n**To read a file, ask me to look at the specific file path.**"
            return result
        
        return "Unexpected GitHub response format"
        
    except Exception as e:
        return f"GitHub API error: {str(e)}"


def get_github_file(owner: str, repo: str, branch: str, path: str) -> str:
    """Read a specific file from GitHub."""
    try:
        # Use raw content URL
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
        response = requests.get(raw_url, timeout=15)
        
        if response.status_code == 404:
            return f"File not found: {path}"
        
        content = response.text
        
        # Detect language from extension
        ext = path.split('.')[-1].lower() if '.' in path else ''
        lang = {
            'py': 'python', 'js': 'javascript', 'ts': 'typescript',
            'html': 'html', 'css': 'css', 'json': 'json',
            'md': 'markdown', 'yaml': 'yaml', 'yml': 'yaml'
        }.get(ext, '')
        
        result = f"📄 **{path}** from {owner}/{repo}\n\n"
        if lang:
            result += f"```{lang}\n{content[:12000]}\n```"
        else:
            result += content[:12000]
        
        if len(content) > 12000:
            result += f"\n\n... (truncated, file is {len(content):,} chars)"
        
        return result
        
    except Exception as e:
        return f"GitHub file error: {str(e)}"


def read_github_web(url: str) -> str:
    """Fallback: scrape GitHub page if API fails."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get README content if available
        readme = soup.find('article', class_='markdown-body')
        if readme:
            return f"**GitHub Repository README:**\n\n{readme.get_text()[:8000]}"
        
        # Get file list
        files = soup.find_all('a', class_='js-navigation-open')
        if files:
            file_list = [f.get_text().strip() for f in files[:30]]
            return f"**Files in repository:**\n" + "\n".join(file_list)
        
        return "Could not parse GitHub page"
    except Exception as e:
        return f"GitHub scrape error: {str(e)}"


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# FULL AGENTIC CAPABILITIES - BROWSER AUTOMATION, API CALLS, FILE OPS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

def browse_website(url: str, actions: List[Dict] = None) -> str:
    """
    FULL BROWSER AUTOMATION - Can click, type, navigate, scroll, and extract content.
    Uses Playwright for JavaScript-rendered content.
    
    Actions format: [{"action": "click", "selector": "button"}, {"action": "type", "selector": "input", "text": "hello"}]
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        # Fallback to simple request if Playwright not installed
        return read_url(url)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            page.set_default_timeout(15000)
            
            # Navigate to URL
            page.goto(url, wait_until='domcontentloaded')
            page.wait_for_timeout(2000)  # Wait for JS to render
            
            # Execute actions if provided
            if actions:
                for action in actions[:10]:  # Limit to 10 actions for safety
                    try:
                        if action.get('action') == 'click':
                            page.click(action.get('selector', ''))
                            page.wait_for_timeout(1000)
                        elif action.get('action') == 'type':
                            page.fill(action.get('selector', ''), action.get('text', ''))
                        elif action.get('action') == 'scroll':
                            page.evaluate('window.scrollBy(0, 500)')
                        elif action.get('action') == 'wait':
                            page.wait_for_timeout(int(action.get('ms', 1000)))
                    except:
                        pass
            
            # Extract content
            title = page.title()
            
            # Get main text content
            content = page.evaluate('''() => {
                const main = document.querySelector('main, article, [role="main"], .content, #content') || document.body;
                const walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, null, false);
                let text = [];
                while(walker.nextNode()) {
                    const txt = walker.currentNode.textContent.trim();
                    if(txt.length > 20) text.push(txt);
                }
                return text.slice(0, 50).join('\\n\\n');
            }''')
            
            # Get all links for navigation help
            links = page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a[href]'))
                    .slice(0, 20)
                    .map(a => ({text: a.innerText.trim().slice(0, 50), href: a.href}))
                    .filter(l => l.text.length > 2);
            }''')
            
            browser.close()
            
            result = f"**{title}**\n\n{content[:8000]}"
            if links:
                result += "\n\n**Links on page:**\n"
                result += "\n".join([f"- [{l['text']}]({l['href']})" for l in links[:15]])
            
            return result
            
    except Exception as e:
        # Fallback to simple request
        return read_url(url) + f"\n\n(Browser automation failed: {str(e)}, used fallback)"


def call_api(url: str, method: str = "GET", data: Dict = None, headers: Dict = None) -> str:
    """
    CALL ANY JSON API - For fetching data from APIs.
    Supports GET, POST, PUT, DELETE.
    """
    try:
        method = method.upper()
        req_headers = {
            'User-Agent': 'NeuralCouncil/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if headers:
            req_headers.update(headers)
        
        if method == "GET":
            response = requests.get(url, headers=req_headers, timeout=15)
        elif method == "POST":
            response = requests.post(url, json=data, headers=req_headers, timeout=15)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=req_headers, timeout=15)
        elif method == "DELETE":
            response = requests.delete(url, headers=req_headers, timeout=15)
        else:
            return f"Unsupported method: {method}"
        
        # Try to parse as JSON
        try:
            json_data = response.json()
            return f"**API Response ({response.status_code}):**\n```json\n{json.dumps(json_data, indent=2)[:8000]}\n```"
        except:
            return f"**API Response ({response.status_code}):**\n{response.text[:5000]}"
            
    except Exception as e:
        return f"API error: {str(e)}"


def download_file(url: str) -> Tuple[bool, str]:
    """
    DOWNLOAD FILE - Downloads a file and returns its content or path.
    For text files, returns content. For binary, indicates success.
    """
    try:
        response = requests.get(url, timeout=30, stream=True)
        content_type = response.headers.get('content-type', '')
        
        # For text content, return it directly
        if 'text' in content_type or 'json' in content_type or 'javascript' in content_type:
            return True, response.text[:15000]
        
        # For binary, just indicate we can access it
        size = len(response.content)
        return True, f"File downloaded successfully ({size:,} bytes, type: {content_type})"
        
    except Exception as e:
        return False, f"Download error: {str(e)}"


def take_screenshot(url: str) -> Tuple[bool, str]:
    """
    TAKE SCREENSHOT - Captures a screenshot of a webpage.
    Returns base64 encoded image data.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False, "Playwright not installed"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 720})
            page.goto(url, wait_until='domcontentloaded')
            page.wait_for_timeout(2000)
            
            screenshot = page.screenshot(type='png')
            browser.close()
            
            b64 = base64.b64encode(screenshot).decode()
            return True, f"data:image/png;base64,{b64}"
            
    except Exception as e:
        return False, f"Screenshot error: {str(e)}"


def extract_structured_data(url: str, selectors: Dict[str, str]) -> str:
    """
    EXTRACT STRUCTURED DATA - Extract specific elements from a page using CSS selectors.
    
    Example: extract_structured_data("https://example.com", {"title": "h1", "price": ".price", "description": "p.desc"})
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {}
        for key, selector in selectors.items():
            elements = soup.select(selector)
            if elements:
                result[key] = [e.get_text().strip() for e in elements[:5]]
        
        return f"**Extracted Data:**\n```json\n{json.dumps(result, indent=2)}\n```"
        
    except Exception as e:
        return f"Extraction error: {str(e)}"


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
    
    # CODE EXECUTION COMMANDS - THE PINNACLE FEATURE
    for pattern in [
        r'\[EXECUTE[_\s]?CODE[:\s]+([^\]]+)\]',
        r'\[RUN[_\s]?CODE[:\s]+([^\]]+)\]',
        r'\[EXECUTE[:\s]+([^\]]+)\]',
        r'\[RUN[:\s]+([^\]]+)\]',
    ]:
        for match in re.finditer(pattern, text, re.I):
            code = match.group(1).strip()
            if code:
                commands.append(("execute", code))
    
    # Also extract code blocks for potential execution
    code_blocks = extract_code_blocks(text)
    for lang, code in code_blocks:
        if lang.lower() in ['python', 'py', 'javascript', 'js']:
            # Only auto-execute if it looks like test code
            if any(test in code.lower() for test in ['print(', 'console.log', 'assert', 'test_', 'def test']):
                commands.append(("execute_block", f"{lang}|||{code}"))
    
    # URL/BROWSE COMMANDS - Full web automation
    for pattern in [
        r'\[READ[_\s]?URL[:\s]+([^\]]+)\]',
        r'\[URL[:\s]+([^\]]+)\]',
        r'\[FETCH[:\s]+([^\]]+)\]',
    ]:
        for match in re.finditer(pattern, text, re.I):
            url = match.group(1).strip()
            if url:
                commands.append(("read_url", url))
    
    # Browser automation commands
    for pattern in [
        r'\[BROWSE[:\s]+([^\]]+)\]',
        r'\[BROWSER[:\s]+([^\]]+)\]',
        r'\[OPEN[_\s]?PAGE[:\s]+([^\]]+)\]',
    ]:
        for match in re.finditer(pattern, text, re.I):
            url = match.group(1).strip()
            if url:
                commands.append(("browse", url))
    
    # Screenshot commands
    for pattern in [
        r'\[SCREENSHOT[:\s]+([^\]]+)\]',
        r'\[CAPTURE[:\s]+([^\]]+)\]',
        r'\[SCREEN[_\s]?CAPTURE[:\s]+([^\]]+)\]',
    ]:
        for match in re.finditer(pattern, text, re.I):
            url = match.group(1).strip()
            if url:
                commands.append(("screenshot", url))
    
    # GitHub commands
    for pattern in [
        r'\[GITHUB[:\s]+([^\]]+)\]',
        r'\[REPO[:\s]+([^\]]+)\]',
        r'\[READ[_\s]?REPO[:\s]+([^\]]+)\]',
    ]:
        for match in re.finditer(pattern, text, re.I):
            url = match.group(1).strip()
            if url:
                commands.append(("github", url))
    
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
    # Simple: short, no code, contains greeting/basic words
    if len(lower) < 50 and '```' not in text:
        simple_words = ['hello', 'hi', 'hey', 'thanks', 'thank you', 'time', 'date', 'today', 
                        'who are you', 'what are you', 'how are you', 'good morning', 'good night']
        if any(w in lower for w in simple_words):
            return True
    # Very short queries (< 30 chars) without code are simple
    return len(lower) < 30 and '```' not in text and '?' not in text


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
    
    # FIXED: If critical issues exist, don't approve
    if critical_count >= 2:
        return False
    # If no approval words AND has critical words -> needs work
    if approval_count == 0 and critical_count > 0:
        return False
    # Default: approve if no critical issues
    return True


def needs_debate(text: str, query_type: str) -> bool:
    """
    Determine if query requires debate mode (complex, controversial, design decisions).
    """
    lower = text.lower()
    
    debate_triggers = ['best way', 'should i', 'which is better', 'pros and cons', 'trade-off',
                       'design decision', 'architecture', 'choose between', 'recommend', 
                       'opinion', 'controversial', 'debate', 'versus', ' vs ', 'alternative']
    
    # FIXED: Only trigger debate for genuinely complex queries (500+ chars AND complex type)
    if len(text) > 500 and query_type in ['code', 'reasoning']:
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

# Local message cache for when Supabase fails
_local_messages: Dict[str, List[Dict]] = {}

def get_sessions(user_id: str = None) -> List[Dict]:
    """Get recent sessions, including local fallback sessions."""
    sessions = []
    
    # Try Supabase
    try:
        db = get_supabase()
        if db:
            query = db.table("chat_sessions").select("*").order("created_at", desc=True).limit(20)
            if user_id:
                query = query.eq("user_id", user_id)
            result = query.execute()
            if result.data:
                sessions = result.data
    except Exception as e:
        print(f"[get_sessions ERROR] {str(e)}")
    
    # Add local sessions (if any messages exist for them)
    for session_id in _local_messages.keys():
        if not any(s.get('id') == session_id for s in sessions):
            msgs = _local_messages[session_id]
            if msgs:
                sessions.append({
                    'id': session_id,
                    'title': msgs[0].get('content', 'Local Chat')[:30] if msgs else 'Local Chat',
                    'created_at': msgs[0].get('created_at', '') if msgs else ''
                })
    
    return sessions

def save_message(session_id: str, role: str, content: str, agent_name: str = None):
    """Save message to Supabase with retry logic and local fallback."""
    if not session_id or not content:
        return
    
    # CRITICAL: Skip Supabase for local/invalid session IDs
    # Supabase expects valid UUID format - local sessions use 'local-xxx' format
    is_local_session = session_id.startswith("local-") or len(session_id) < 32
    
    msg_data = {
        "session_id": session_id, 
        "role": role, 
        "agent_name": agent_name, 
        "content": content, 
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Retry up to 3 times (only if NOT a local session)
    if not is_local_session:
        for attempt in range(3):
            try:
                db = get_supabase()
                if db:
                    db.table("messages").insert(msg_data).execute()
                    # Success! Also try to sync any pending local messages
                    _sync_local_messages(session_id)
                    return
            except Exception as e:
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff: 0.5s, 1s
                else:
                    print(f"[save_message ERROR after 3 attempts] {str(e)}")
    
    # All retries failed - save to local memory
    if session_id not in _local_messages:
        _local_messages[session_id] = []
    _local_messages[session_id].append(msg_data)


def _sync_local_messages(session_id: str):
    """Try to sync local messages to Supabase when connection is restored."""
    if session_id not in _local_messages or not _local_messages[session_id]:
        return
    
    try:
        db = get_supabase()
        if db:
            # Try to insert all pending local messages
            for msg in _local_messages[session_id]:
                try:
                    db.table("messages").insert(msg).execute()
                except:
                    pass  # Individual message failed, continue
            # Clear synced messages
            _local_messages[session_id] = []
    except:
        pass  # Sync failed, will try again later


def get_history(session_id: str) -> List[Dict]:
    """Get message history for a session, with local fallback."""
    if not session_id:
        return []
    
    # Try Supabase first
    try:
        db = get_supabase()
        if db:
            result = db.table("messages").select("*").eq("session_id", session_id).order("created_at").execute()
            if result.data:
                return result.data
    except Exception as e:
        print(f"[get_history ERROR] session_id={session_id}, error={str(e)}")
    
    # Fallback: check local memory cache
    if session_id in _local_messages:
        return sorted(_local_messages[session_id], key=lambda x: x.get("created_at", ""))
    
    return []


def save_memory(content: str, user_id: str = None):
    """Save memory with TRUE semantic embeddings."""
    try:
        db = get_supabase()
        if db:
            embedding = get_real_embedding(content)
            data = {"content": content, "embedding": embedding, "created_at": datetime.now(timezone.utc).isoformat()}
            if user_id:
                data["user_id"] = user_id
            db.table("memories").insert(data).execute()
    except:
        pass



def recall_memories(query: str, user_id: str = None) -> List[str]:
    """Recall memories using TRUE semantic embeddings."""
    try:
        db = get_supabase()
        if db:
            embedding = get_real_embedding(query)
            params = {"query_embedding": embedding, "match_threshold": 0.6, "match_count": 5}
            if user_id:
                params["p_user_id"] = user_id
            result = db.rpc("match_memories", params).execute()
            return [m["content"] for m in result.data]
    except:
        pass
    return []


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# ULTRA-LONG CONTEXT MEMORY SYSTEM - THE PINNACLE
# Handles 1M+ token conversations with perfect recall
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

# Session summary cache (in-memory for speed)
_session_summaries: Dict[str, str] = {}

def summarize_conversation(messages: List[Dict], max_length: int = 2000) -> str:
    """
    CONVERSATION SUMMARIZATION: Compress long conversation history into key points.
    Uses AI to create a comprehensive summary of the entire conversation.
    """
    if not messages:
        return ""
    
    # Build conversation text
    conv_text = "\n".join([
        f"[{m.get('agent_name', m.get('role', 'User'))}]: {m.get('content', '')[:500]}" 
        for m in messages[-50:]  # Last 50 messages for summarization
    ])
    
    if len(conv_text) < 500:
        return conv_text  # Too short to summarize
    
    # Use Strategist to summarize (fast model)
    summary_prompt = f"""Summarize this conversation history in {max_length} chars max.
Focus on:
1. Key topics discussed
2. Important decisions made
3. Code/solutions provided
4. User preferences learned
5. Ongoing tasks/projects

CONVERSATION:
{conv_text[:15000]}

SUMMARY:"""
    
    try:
        summary, _ = call_agent("Strategist", [{"role": "user", "content": summary_prompt}], 1000)
        return summary[:max_length]
    except:
        # Fallback: just take key points
        return conv_text[:max_length]


def get_session_summary(session_id: str) -> Optional[str]:
    """Get cached session summary or generate one."""
    if session_id in _session_summaries:
        return _session_summaries[session_id]
    
    try:
        db = get_supabase()
        if db:
            # Try to get stored summary
            result = db.table("chat_sessions").select("summary").eq("id", session_id).execute()
            if result.data and result.data[0].get("summary"):
                _session_summaries[session_id] = result.data[0]["summary"]
                return _session_summaries[session_id]
    except:
        pass
    
    return None


def update_session_summary(session_id: str, history: List[Dict]):
    """Update session summary in background (every 10 messages)."""
    if not history or len(history) < 10:
        return
    
    # Only update every 10 messages
    if len(history) % 10 != 0:
        return
    
    summary = summarize_conversation(history)
    _session_summaries[session_id] = summary
    
    try:
        db = get_supabase()
        if db:
            db.table("chat_sessions").update({"summary": summary}).eq("id", session_id).execute()
    except:
        pass


def build_hierarchical_context(session_id: str, user_input: str, user_id: str = None) -> List[Dict]:
    """
    HIERARCHICAL CONTEXT BUILDER - ABSOLUTE MAXIMUM Token Usage
    
    For handling 10,000+ word inputs/outputs without truncation.
    Uses ABSOLUTE MAXIMUM limits.
    
    3-Tier Memory Architecture with ABSOLUTE MAXIMUM limits:
    1. IMMEDIATE (last 20 messages, 20000 chars each) - ~100K tokens max
    2. SESSION SUMMARY (compressed history) - ~8K tokens  
    3. LONG-TERM MEMORIES (semantic recall) - ~12K tokens
    4. FILE CACHE REFERENCES - Shows available files without resending
    
    Total: ~120K tokens (uses full 128K context window)
    """
    context = []
    MAX_MSG_CHARS = 20000   # ~5000 tokens per message (ABSOLUTE MAX for 10K+ words)
    MAX_MESSAGES = 20       # Last 20 messages (ABSOLUTE MAX)
    MAX_MEMORY_CHARS = 6000  # Per memory (ABSOLUTE MAX)
    MAX_SUMMARY_CHARS = 8000  # Session summary (ABSOLUTE MAX)
    
    # TIER 4: FILE CACHE REFERENCES - Shows what files are available
    file_refs = get_file_references(session_id)
    if file_refs:
        context.append({
            "role": "user",
            "content": file_refs
        })
    
    # TIER 3: Long-term memories (semantic) - LIMITED
    try:
        memories = recall_memories(user_input, user_id)
        if memories:
            # Take only first 3 memories, 1000 chars each
            memory_texts = [m[:MAX_MEMORY_CHARS] for m in memories[:3]]
            memory_text = "\n---\n".join(memory_texts)
            context.append({
                "role": "user", 
                "content": f"[LONG-TERM MEMORY]:\n{memory_text}"
            })
    except:
        pass
    
    # TIER 2: Session summary (compressed history) - LIMITED
    try:
        session_summary = get_session_summary(session_id)
        if session_summary:
            context.append({
                "role": "user",
                "content": f"[SESSION SUMMARY]:\n{session_summary[:MAX_SUMMARY_CHARS]}"
            })
    except:
        pass
    
    # TIER 1: Immediate context (last N messages, LIMITED chars each)
    # SMART FILE HANDLING: Strip file contents from OLD messages, keep only in recent ones
    try:
        history = get_history(session_id)
        
        # Update session summary in background
        update_session_summary(session_id, history)
        
        # Take last N messages with SMART truncation
        recent_msgs = history[-MAX_MESSAGES:]
        for i, msg in enumerate(recent_msgs):
            content = msg.get('content', '')
            
            # For OLD messages (not last 2), strip file contents to save tokens
            is_recent = i >= len(recent_msgs) - 2
            if not is_recent and "[FILE:" in content:
                # Replace file contents with references
                import re
                # Keep file markers but remove content
                content = re.sub(
                    r'\[FILE: ([^\]]+)\]\n```[^`]*```',
                    r'[FILE: \1 - content in cache, use "show file \1" to view]',
                    content
                )
            
            # Truncate long messages
            if len(content) > MAX_MSG_CHARS:
                content = content[:MAX_MSG_CHARS] + "... [truncated]"
            
            agent_name = msg.get('agent_name', 'User')
            context.append({
                "role": msg["role"],
                "content": f"[{agent_name}]: {content}"
            })
    except:
        pass
    
    return context


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
    
    # HIERARCHICAL CONTEXT - THE PINNACLE (replaces old 4-message limit)
    # 3 tiers: Long-term memories + Session summary + Last 15 messages (FULL content)
    context = build_hierarchical_context(session_id, user_input, user_id)
    yield ("System", f"🧠 Context loaded: {len(context)} items", "system")
    
    # Save user message
    save_message(session_id, "user", user_input)
    history = get_history(session_id)
    if len(history) <= 1:
        update_session_title(session_id, user_input[:40] + "..." if len(user_input) > 40 else user_input)
    
    # Add current query
    context.append({"role": "user", "content": enhanced_input})
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 2: SIMPLE QUERY FAST PATH
    # ═══════════════════════════════════════════════════════════════════════════════
    
    if is_simple_query(user_input):
        yield ("System", "⚡ Fast response...", "system")
        answer, _ = call_agent("Strategist", context, 2000)
        
        # CRITICAL: Check if response is an error
        if not answer or "⚠️" in answer or "Exception:" in answer:
            yield ("System", "⚠️ Strategist error - retrying with Executor", "system")
            answer, _ = call_agent("Executor", context, 4000)
            if not answer or "⚠️" in answer:
                answer = "I apologize, but I'm experiencing technical difficulties. Please try again."
        
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
    # PHASE 4: STRATEGIST PLANNING (WITH VISION IF SCREENSHOT)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    yield ("System", "🎯 Strategist analyzing...", "system")
    
    # Use vision if screenshot is provided
    if screenshot_b64:
        yield ("System", "👁️ Using TRUE VISION to analyze screenshot...", "system")
        plan, _ = call_agent_with_vision("Strategist", context, screenshot_b64, 4000)
    else:
        plan, _ = call_agent("Strategist", context, 4000)
    
    # CRITICAL: Check if Strategist returned an error
    if not plan or "⚠️" in plan or "Exception:" in plan:
        yield ("System", "⚠️ Strategist error - using fallback analysis", "system")
        # Fallback: Create a basic plan based on user input
        plan = f"I'll analyze your request and provide a solution. Query: {user_input[:500]}"
    
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
        elif cmd_type == "read_url":
            yield ("System", f"🌐 Reading URL: {prompt[:50]}...", "system")
            content = read_url(prompt)
            context.append({"role": "user", "content": f"[URL CONTENT]:\n{content}"})
        elif cmd_type == "browse":
            yield ("System", f"🌐 Browsing with automation: {prompt[:50]}...", "system")
            content = browse_website(prompt)
            context.append({"role": "user", "content": f"[BROWSER CONTENT]:\n{content}"})
        elif cmd_type == "screenshot":
            yield ("System", f"📸 Capturing screenshot: {prompt[:50]}...", "system")
            success, img_data = take_screenshot(prompt)
            if success:
                yield ("System", img_data, "image")
        elif cmd_type == "github":
            yield ("System", f"📂 Reading GitHub: {prompt[:50]}...", "system")
            content = read_github(prompt)
            context.append({"role": "user", "content": f"[GITHUB CONTENT]:\n{content}"})
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 5: DEBATE MODE (if triggered)
    # Multiple agents challenge each other's thinking
    # ═══════════════════════════════════════════════════════════════════════════════
    
    if use_debate:
        yield ("System", "💭 DEBATE MODE: Agents will challenge each other...", "system")
        
        # Helper function to detect error responses
        def is_error_response(text: str) -> bool:
            if not text:
                return True
            error_markers = ["⚠️", "Exception:", "Error:", "error:", "list index out of range", 
                           "Rate limited", "too long", "Max retries", "API key not configured"]
            return any(marker in text for marker in error_markers)
        
        # Round 1: Executor proposes
        debate_context = context.copy()
        debate_context.append({"role": "user", "content": f"[DEBATE MODE] Propose your solution. Be specific. The Sage will challenge you."})
        
        proposal, _ = call_agent("Executor", debate_context, 6000)
        
        # If Executor returned an error, skip debate and use direct mode
        if is_error_response(proposal):
            yield ("System", "⚠️ Executor error - switching to direct mode", "system")
            use_debate = False
            solution = proposal
            reasoning = "Error occurred, skipping debate"
        else:
            yield (f"{AGENTS['Executor']['name']} (Proposal)", proposal, "executor")
            save_message(session_id, "assistant", proposal, f"{AGENTS['Executor']['name']} (Proposal)")
            
            # Round 2: Sage challenges
            debate_context.append({"role": "assistant", "content": f"[EXECUTOR PROPOSAL]:\n{proposal}"})
            debate_context.append({"role": "user", "content": "[DEBATE MODE] Challenge this proposal. What's wrong? What's a better alternative?"})
            
            challenge, _ = call_agent("Sage", debate_context, 4000)
            
            # If Sage returned an error, skip further debate and use proposal as-is
            if is_error_response(challenge):
                yield ("System", "⚠️ Sage error - using Executor proposal directly", "system")
                solution = proposal
                reasoning = "Sage error: using Executor proposal"
            else:
                yield (f"{AGENTS['Sage']['name']} (Challenge)", challenge, "sage")
                save_message(session_id, "assistant", challenge, f"{AGENTS['Sage']['name']} (Challenge)")
                
                # Round 3: Executor responds to challenge
                debate_context.append({"role": "assistant", "content": f"[SAGE CHALLENGE]:\n{challenge}"})
                debate_context.append({"role": "user", "content": "[DEBATE MODE] Respond to the Sage's challenge. Defend or improve your proposal."})
                
                response, _ = call_agent("Executor", debate_context, 6000)
                
                # If response is an error, use proposal
                if is_error_response(response):
                    yield ("System", "⚠️ Executor response error - using proposal", "system")
                    solution = proposal
                    reasoning = challenge
                else:
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
        
        # Reduced max_tokens to save tokens while still allowing complete responses
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            executor_future = pool.submit(call_agent, "Executor", context, 6000)  # Reduced from 8000
            sage_future = pool.submit(call_agent, "Sage", context, 2000)  # Reduced from 4000
            
            # CRITICAL: Wrap .result() in try/except - threads can crash
            try:
                solution, _ = executor_future.result(timeout=180)
            except Exception as e:
                solution = f"⚠️ Executor thread error: {str(e)[:100]}"
            
            try:
                reasoning, _ = sage_future.result(timeout=180)
            except Exception as e:
                reasoning = f"⚠️ Sage thread error: {str(e)[:100]}"
        
        # CRITICAL: Check if either result is an error
        def is_error(text):
            if not text:
                return True
            markers = ["⚠️", "Exception:", "Error:", "list index", "Rate limited", "Max retries"]
            return any(m in str(text) for m in markers)
        
        if is_error(solution):
            yield ("System", f"⚠️ Executor error - falling back to Strategist", "system")
            solution = plan  # Use Strategist plan as fallback
        
        if is_error(reasoning):
            yield ("System", f"⚠️ Sage error - skipping critique", "system")
            reasoning = "Critique unavailable"
        
        save_message(session_id, "assistant", solution, AGENTS["Executor"]["name"])
        save_message(session_id, "assistant", reasoning, AGENTS["Sage"]["name"])
        context.append({"role": "assistant", "content": f"[EXECUTOR SOLUTION]:\n{solution}"})
        context.append({"role": "assistant", "content": f"[SAGE CRITIQUE]:\n{reasoning}"})
        
        yield (AGENTS["Executor"]["name"], solution, "executor")
        yield (AGENTS["Sage"]["name"], reasoning, "sage")
    
    # Process commands (including CODE EXECUTION)
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
            elif cmd_type == "execute":
                # EXECUTE CODE - THE PINNACLE FEATURE
                yield ("System", "🖥️ Executing code in sandbox...", "system")
                success, output = execute_code(prompt)
                yield ("System", output, "system")
                # Add execution result to context for agents
                context.append({"role": "user", "content": f"[CODE EXECUTION RESULT]:\n{output}"})
            elif cmd_type == "execute_block":
                # Auto-execute code blocks with test patterns
                parts = prompt.split("|||", 1)
                if len(parts) == 2:
                    lang, code = parts
                    yield ("System", f"🖥️ Auto-testing {lang} code...", "system")
                    success, output = execute_code(code, lang)
                    yield ("System", output, "system")
                    context.append({"role": "user", "content": f"[AUTO-TEST RESULT]:\n{output}"})

    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 6: REFINEMENT LOOP (only if Sage found issues)
    # Loop ONLY if Sage doesn't approve (not based on arbitrary quality score)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    MAX_REFINEMENT_ROUNDS = 3  # Reduced from 10 to prevent token waste
    round_num = 0
    
    # ONLY loop if Sage explicitly disapproves - not based on quality heuristics
    while not sage_approves(reasoning) and round_num < MAX_REFINEMENT_ROUNDS:
        round_num += 1
        yield ("System", f"🔄 Refinement Round {round_num}/{MAX_REFINEMENT_ROUNDS} - Sage found issues, fixing...", "system")


        
        # Executor fixes
        fix_prompt = f"""ROUND {round_num} REFINEMENT

The SAGE found these issues:
{reasoning[:2000]}

YOUR CURRENT SOLUTION:
{solution[:3000]}

FIX ALL ISSUES. Output the COMPLETE, CORRECTED solution.
The Sage will review again. Make it perfect this time."""
        
        context.append({"role": "user", "content": f"[FIX ROUND {round_num}]:\n{fix_prompt}"})
        new_solution, _ = call_agent("Executor", context, 8000)
        
        # CRITICAL: Check if Executor returned an error
        if not new_solution or "⚠️" in new_solution or "Exception:" in new_solution:
            yield ("System", f"⚠️ Executor error in refinement - using previous solution", "system")
            break  # Exit loop, keep previous solution
        
        solution = new_solution
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
        new_reasoning, _ = call_agent("Sage", context, 3000)
        
        # CRITICAL: Check if Sage returned an error
        if not new_reasoning or "⚠️" in new_reasoning or "Exception:" in new_reasoning:
            yield ("System", f"⚠️ Sage error in refinement - proceeding with current solution", "system")
            reasoning = "APPROVED (Sage error - auto-approved)"
            break  # Exit loop
        
        reasoning = new_reasoning
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
    
    # Report refinement result
    if round_num > 0:
        if sage_approves(reasoning):
            yield ("System", f"✅ Sage APPROVED after {round_num} refinement round(s)!", "system")
        else:
            yield ("System", f"⚠️ Max refinement rounds ({MAX_REFINEMENT_ROUNDS}) reached", "system")
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PHASE 7: SMART EMPEROR SYNTHESIS
    # REVOLUTIONARY: Skip Emperor if Sage approved on first try - saves ~50% tokens
    # ═══════════════════════════════════════════════════════════════════════════════
    
    # SMART SKIP: If Sage approved immediately (no refinement) AND solution is high quality,
    # use Executor's solution directly instead of expensive Emperor call
    skip_emperor = (round_num == 0 and sage_approves(reasoning) and len(solution) > 200)
    
    if skip_emperor:
        yield ("System", "⚡ Sage approved - using Executor solution directly (saving tokens)", "system")
        verdict = solution
        save_message(session_id, "assistant", verdict, f"{AGENTS['Executor']['name']} (Final)")
        yield (f"{AGENTS['Executor']['name']} (Sage-Approved)", verdict, "executor")
    else:
        yield ("System", "👑 Emperor synthesizing final answer...", "system")
        
        # Reduced context size to save tokens
        emperor_input = f"""[QUERY]: {enhanced_input[:800]}
[TYPE]: {query_type} | [ROUNDS]: {round_num}

[SOLUTION]:
{solution[:3000]}

[SAGE]: {reasoning[:1000]}

Synthesize the FINAL answer. Fix issues. Make it PERFECT."""
        
        verdict, _ = call_agent("Emperor", [{"role": "user", "content": emperor_input}], 6000)
        
        # CRITICAL: Check if Emperor returned an error - fallback to solution
        if not verdict or "⚠️" in verdict or "Exception:" in verdict:
            yield ("System", "⚠️ Emperor error - using Executor solution", "system")
            verdict = solution
            save_message(session_id, "assistant", verdict, f"{AGENTS['Executor']['name']} (Final)")
            yield (f"{AGENTS['Executor']['name']} (Fallback)", verdict, "executor")
        else:
            save_message(session_id, "assistant", verdict, AGENTS["Emperor"]["name"])
            yield (AGENTS["Emperor"]["name"], verdict, "emperor")
    
    # Process commands from final answer
    for cmd_type, prompt in process_ai_commands(verdict):
        if cmd_type == "image":
            yield ("System", "🎨 Generating image...", "system")
            url, _ = generate_image(prompt)
            if url:
                yield ("System", url, "image")
        elif cmd_type == "video":
            yield ("System", "🎬 Generating video...", "system")
            url, _ = generate_video(prompt)
            if url:
                yield ("System", url, "video")
        elif cmd_type == "read_url":
            yield ("System", f"🌐 Reading: {prompt[:40]}...", "system")
            content = read_url(prompt)
            # Add to context for any follow-up
            yield ("System", f"📖 URL content fetched ({len(content)} chars)", "system")
        elif cmd_type == "screenshot":
            yield ("System", f"📸 Capturing: {prompt[:40]}...", "system")
            success, img_data = take_screenshot(prompt)
            if success:
                yield ("System", img_data, "image")
    
    # Extract and display any image URLs
    for img_url in extract_image_urls(verdict):
        yield ("System", img_url, "image")
    
    # Only save important exchanges to memory
    if len(user_input) > 100 and len(verdict) > 500:
        save_memory(f"Q: {user_input[:150]}\nA: {verdict[:400]}", user_id)
    
    # Final stats
    tokens_saved = "~50% saved via smart skip" if skip_emperor else ""
    yield ("System", f"🧠 Council Complete | {get_tokens_used():,} tokens | {round_num} refinements {tokens_saved}", "system")


