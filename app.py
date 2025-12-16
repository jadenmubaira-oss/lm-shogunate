"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LM SHOGUNATE: THE FINAL PINNACLE UI                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Features:
• Persistent login (remembers device)
• Session persistence (no duplicate chats)
• Theme persistence
• Token tracking
• Image display
• Streamlined 3-agent council
"""

import streamlit as st
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="LM Shogunate | AI Council",
    page_icon="🏯",
    layout="wide",
    initial_sidebar_state="expanded"
)

import council

# ═══════════════════════════════════════════════════════════════════════════════
# PERSISTENT LOGIN - Uses query params (survives refresh)
# ═══════════════════════════════════════════════════════════════════════════════

def check_auth():
    """Check if user is authenticated via query param token."""
    params = st.query_params
    return params.get("auth") == hashlib.md5(os.getenv("APP_PASSWORD", "shogun2024").encode()).hexdigest()[:16]

def set_auth():
    """Set auth token in query params."""
    import hashlib
    token = hashlib.md5(os.getenv("APP_PASSWORD", "shogun2024").encode()).hexdigest()[:16]
    st.query_params["auth"] = token

import hashlib

# Check auth
if not check_auth():
    # Login screen
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 50%, #0a0a0a 100%); }
        @keyframes pulse { 
            0%, 100% { text-shadow: 0 0 20px #c41e3a, 0 0 40px #c41e3a40; }
            50% { text-shadow: 0 0 40px #ff6b6b, 0 0 80px #c41e3a60; }
        }
        .login-title { font-size: 5em; text-align: center; margin-bottom: 0; }
        .login-subtitle { 
            font-size: 2.5em; text-align: center; color: #c41e3a;
            animation: pulse 2s ease-in-out infinite;
            font-family: 'Times New Roman', serif; letter-spacing: 8px;
        }
        .login-desc { text-align: center; color: #888; font-size: 1.2em; margin-top: 20px; }
    </style>
    <div class="login-title">🏯</div>
    <div class="login-subtitle">LM SHOGUNATE</div>
    <p class="login-desc">The Ultimate Multi-Agent AI Council</p>
    <p class="login-desc" style="font-size: 0.9em; color: #666;">
        Claude Opus 4.5 • Claude Sonnet 4.5 • GPT-5.2
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        password = st.text_input("🔐 Enter Passcode", type="password", placeholder="Passcode...")
        
        if st.button("⚔️ ENTER THE SHOGUNATE", use_container_width=True):
            if password == os.getenv("APP_PASSWORD", "shogun2024"):
                set_auth()
                st.rerun()
            else:
                st.error("❌ Invalid passcode.")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 40px; color: #444; font-size: 0.8em;">
            Powered by Azure AI Foundry • Unrestricted Intelligence
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE - Persisted via query params
# ═══════════════════════════════════════════════════════════════════════════════

# Get session from query params or create new
params = st.query_params

# Theme
if "theme" not in st.session_state:
    st.session_state.theme = params.get("theme", "Shogunate")

# Session - DON'T create new on every refresh
if "session_id" not in st.session_state:
    saved_session = params.get("session")
    if saved_session:
        st.session_state.session_id = saved_session
    else:
        # Only create if no saved session
        st.session_state.session_id = council.create_session("New Quest", st.session_state.theme)
        st.query_params["session"] = st.session_state.session_id

if "artifact" not in st.session_state:
    st.session_state.artifact = "# 🏯 The Council awaits...\n\n# Type a command to summon the AI Lords."

# ═══════════════════════════════════════════════════════════════════════════════
# THEME SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

theme = council.THEMES[st.session_state.theme]

st.markdown(f"""
<style>
    /* === BASE === */
    .stApp {{
        background: linear-gradient(135deg, {theme['bg']} 0%, {theme['accent']} 100%);
        color: {theme['text']};
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {theme['bg']} 0%, {theme['accent']} 100%);
        border-right: 3px solid {theme['secondary']};
    }}
    .stButton > button {{
        background: linear-gradient(135deg, {theme['primary']} 0%, {theme['accent']} 100%);
        color: {theme['text']};
        border: 2px solid {theme['secondary']};
        border-radius: 12px;
        font-weight: bold;
        padding: 12px 24px;
        transition: all 0.3s ease;
        min-height: 44px; /* Touch-friendly */
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, {theme['secondary']} 0%, {theme['primary']} 100%);
        transform: translateY(-2px);
    }}
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background: rgba(0,0,0,0.7) !important;
        color: {theme['text']} !important;
        border: 2px solid {theme['secondary']}80 !important;
        border-radius: 10px !important;
        min-height: 44px; /* Touch-friendly */
    }}
    h1, h2, h3 {{ color: {theme['primary']} !important; }}
    [data-testid="stChatMessage"] {{
        background: rgba(0,0,0,0.4) !important;
        border-radius: 15px;
        border-left: 5px solid {theme['secondary']};
        padding: 15px;
        margin: 10px 0;
    }}
    .agent-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        margin-bottom: 8px;
    }}
    .agent-emperor {{ background: linear-gradient(90deg, #ffd700, #ffaa00); color: #000; }}
    .agent-strategist {{ background: linear-gradient(90deg, #4a90d9, #2e5a8b); color: #fff; }}
    .agent-executor {{ background: linear-gradient(90deg, #50c878, #228b22); color: #fff; }}
    .agent-sage {{ background: linear-gradient(90deg, #9370db, #4b0082); color: #fff; }}
    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-track {{ background: {theme['bg']}; }}
    ::-webkit-scrollbar-thumb {{ background: {theme['secondary']}; border-radius: 4px; }}
    
    /* === MOBILE RESPONSIVENESS === */
    @media (max-width: 768px) {{
        .stApp {{ padding: 0.5rem !important; }}
        h1 {{ font-size: 1.5em !important; }}
        h2 {{ font-size: 1.2em !important; }}
        .stButton > button {{ 
            width: 100% !important; 
            padding: 14px !important;
            font-size: 1em !important;
        }}
        [data-testid="stSidebar"] {{
            width: 100% !important;
            max-width: 100% !important;
        }}
        [data-testid="stChatMessage"] {{
            padding: 10px;
            margin: 5px 0;
        }}
        .agent-badge {{
            font-size: 0.75em;
            padding: 3px 8px;
        }}
        /* Stack columns on mobile */
        [data-testid="column"] {{
            width: 100% !important;
            flex: 1 1 100% !important;
        }}
    }}
    
    /* === TABLET === */
    @media (min-width: 769px) and (max-width: 1024px) {{
        h1 {{ font-size: 1.8em !important; }}
        .stButton > button {{ padding: 12px 20px !important; }}
    }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 3em;">🏯</div>
        <div style="font-size: 1.5em; color: {theme['primary']}; font-weight: bold;">LM SHOGUNATE</div>
        <div style="font-size: 0.8em; color: {theme['text']}80;">{theme['description']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Theme selector
    st.markdown("### 🎨 Choose Your Era")
    new_theme = st.selectbox(
        "Theme", list(council.THEMES.keys()),
        index=list(council.THEMES.keys()).index(st.session_state.theme),
        label_visibility="collapsed"
    )
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.query_params["theme"] = new_theme
        st.rerun()
    
    st.divider()
    
    # New session
    if st.button("➕ Begin New Quest", use_container_width=True):
        new_id = council.create_session("New Quest", st.session_state.theme)
        st.session_state.session_id = new_id
        st.query_params["session"] = new_id
        st.session_state.artifact = "# New quest initiated..."
        council.reset_tokens()
        st.rerun()
    
    st.divider()
    
    # Council hierarchy
    st.markdown("### 👑 The Council")
    for key, agent in council.AGENTS.items():
        st.markdown(f"{agent['avatar']} **{agent['name']}**")
        st.caption(f"  ↳ {agent['role']}")
    
    st.divider()
    
    # Session history
    st.markdown("### 📜 Quest Archives")
    try:
        sessions = council.get_sessions()
        displayed = 0
        for sess in sessions:
            if displayed >= 10:
                break
            if sess['id'] == st.session_state.session_id:
                continue  # Skip current
            
            title = sess.get('title', 'Untitled')[:20]
            theme_icon = {"Shogunate": "⚔️", "Bandit Camp": "🪓", "Neon Tokyo": "🌃"}.get(sess.get('theme', ''), "📜")
            
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"{theme_icon} {title}", key=f"sess_{sess['id']}", use_container_width=True):
                    st.session_state.session_id = sess['id']
                    st.session_state.theme = sess.get('theme', 'Shogunate')
                    st.query_params["session"] = sess['id']
                    st.query_params["theme"] = sess.get('theme', 'Shogunate')
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{sess['id']}"):
                    council.delete_session(sess['id'])
                    st.rerun()
            
            displayed += 1
    except Exception as e:
        st.caption(f"📭 No archives")
    
    st.divider()
    st.caption(f"💰 Tokens Used: {council.get_tokens_used():,}")
    st.caption(f"🔐 Session: {st.session_state.session_id[:12]}...")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

col1, col2 = st.columns([1.4, 1])

with col1:
    st.markdown("## 👑 Council Chamber")
    st.markdown(f"*{theme['description']}*")
    
    # File upload
    uploaded = st.file_uploader(
        "📎 Attach Files",
        type=['pdf', 'txt', 'py', 'js', 'ts', 'json', 'md', 'html', 'css', 'sql'],
        help="Upload files for analysis"
    )
    
    # Chat history
    try:
        history = council.get_history(st.session_state.session_id)
        for msg in history:
            agent_name = msg.get("agent_name", "")
            role = msg["role"]
            
            if role == "user":
                avatar = "👤"
            else:
                agent_info = None
                for key, agent in council.AGENTS.items():
                    if agent["name"] in str(agent_name):
                        agent_info = agent
                        break
                avatar = agent_info["avatar"] if agent_info else "🤖"
            
            with st.chat_message(role, avatar=avatar):
                if agent_name:
                    agent_class = "emperor" if "Emperor" in agent_name else \
                                 "strategist" if "Strategist" in agent_name else \
                                 "executor" if "Executor" in agent_name else ""
                    st.markdown(f'<span class="agent-badge agent-{agent_class}">{agent_name}</span>', unsafe_allow_html=True)
                
                st.markdown(msg["content"])
                
                # Extract code for artifact
                if "```" in str(msg["content"]):
                    try:
                        parts = msg["content"].split("```")
                        if len(parts) >= 2:
                            block = parts[1]
                            if "\n" in block:
                                first_line, rest = block.split("\n", 1)
                                if first_line.strip() in ["python", "javascript", "js", "typescript", "ts", "html", "css", "json", "sql"]:
                                    block = rest
                            st.session_state.artifact = block.strip()
                    except:
                        pass
    except:
        st.info("📜 No messages yet. Command the council to begin.")
    
    # User input
    user_input = st.chat_input("Command the council... (search: query, image: prompt)")
    
    if user_input:
        # Handle file
        if uploaded:
            try:
                if uploaded.type == "application/pdf":
                    from PyPDF2 import PdfReader
                    reader = PdfReader(uploaded)
                    file_text = "\n".join([p.extract_text() or "" for p in reader.pages])
                else:
                    file_text = uploaded.read().decode('utf-8', errors='ignore')
                user_input += f"\n\n[FILE: {uploaded.name}]\n```\n{file_text[:8000]}\n```"
            except Exception as e:
                user_input += f"\n\n[FILE ERROR: {str(e)}]"
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # Run council
        with st.status("⚡ The Council deliberates...", expanded=True) as status:
            try:
                for agent, content, msg_type in council.run_council(
                    st.session_state.theme,
                    user_input,
                    st.session_state.session_id
                ):
                    if msg_type == "system":
                        st.markdown(f"🔔 {content}")
                    elif msg_type == "image":
                        st.image(content, width=512, caption="Generated Image")
                    elif msg_type == "video":
                        st.video(content)
                        st.caption("🎬 Generated Video (Kling v2.5)")
                    else:
                        agent_info = None
                        for key, a in council.AGENTS.items():
                            if a["name"] in str(agent):
                                agent_info = a
                                break
                        
                        avatar = agent_info["avatar"] if agent_info else "🤖"
                        
                        with st.chat_message("assistant", avatar=avatar):
                            agent_class = "emperor" if "Emperor" in agent else \
                                         "strategist" if "Strategist" in agent else \
                                         "executor" if "Executor" in agent else \
                                         "sage" if "Sage" in agent else ""
                            st.markdown(f'<span class="agent-badge agent-{agent_class}">{agent}</span>', unsafe_allow_html=True)
                            st.markdown(content)
                        
                        # Update artifact
                        if "```" in str(content):
                            try:
                                parts = content.split("```")
                                if len(parts) >= 2:
                                    block = parts[1]
                                    if "\n" in block:
                                        first_line, rest = block.split("\n", 1)
                                        if first_line.strip() in ["python", "javascript", "js", "typescript", "ts", "html", "css", "json", "sql"]:
                                            block = rest
                                    st.session_state.artifact = block.strip()
                            except:
                                pass
                
                status.update(label="✅ Council has spoken!", state="complete")
            except Exception as e:
                status.update(label=f"❌ Error: {str(e)}", state="error")
        
        st.rerun()

with col2:
    st.markdown("## 📜 Artifacts")
    
    code = st.session_state.artifact
    lang = "python"
    if code.strip().startswith(("{", "[")):
        lang = "json"
    elif "<html" in code.lower():
        lang = "html"
    elif "function" in code or "const " in code:
        lang = "javascript"
    elif "SELECT" in code.upper():
        lang = "sql"
    
    st.code(code, language=lang, line_numbers=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        ext = {"python": "py", "javascript": "js", "json": "json", "html": "html", "sql": "sql"}.get(lang, "txt")
        st.download_button("💾 Download", st.session_state.artifact, f"solution.{ext}", use_container_width=True)
    with col_b:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.artifact = "# Cleared."
            st.rerun()
    
    st.divider()
    
    st.markdown("### 🏯 Council Hierarchy")
    st.markdown("""
    | Tier | Agent | Model |
    |------|-------|-------|
    | 👑 | **Emperor** | Claude Opus 4.5 |
    | ⭐ | **Strategist** | Claude Sonnet 4.5 |
    | ⭐ | **Executor** | GPT-5.2 |
    | 📿 | **Sage** | DeepSeek V3.2 |
    """)
    
    st.divider()
    
    with st.expander("💡 Power Tips"):
        st.markdown("""
        - `search: query` - Web search
        - `image: prompt` - Generate images
        - `video: prompt` - Generate videos
        - Paste URLs - Auto-read content
        - Upload files - PDF, code, etc.
        - Sessions persist on refresh
        """)

