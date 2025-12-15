"""
LM SHOGUNATE: The Pinnacle UI
==============================
A stunning, immersive interface for the multi-agent AI council.
"""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="LM Shogunate | AI Council",
    page_icon="🏯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import after load_dotenv
import council

# ===== AUTHENTICATION =====
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Epic login screen
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 50%, #0a0a0a 100%);
        }
        @keyframes pulse {
            0%, 100% { text-shadow: 0 0 20px #c41e3a, 0 0 40px #c41e3a40; }
            50% { text-shadow: 0 0 40px #ff6b6b, 0 0 80px #c41e3a60; }
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .login-title {
            font-size: 5em;
            text-align: center;
            animation: float 3s ease-in-out infinite;
            margin-bottom: 0;
        }
        .login-subtitle {
            font-size: 2.5em;
            text-align: center;
            color: #c41e3a;
            animation: pulse 2s ease-in-out infinite;
            font-family: 'Times New Roman', serif;
            letter-spacing: 8px;
        }
        .login-desc {
            text-align: center;
            color: #888;
            font-size: 1.2em;
            margin-top: 20px;
        }
    </style>
    <div class="login-title">🏯</div>
    <div class="login-subtitle">LM SHOGUNATE</div>
    <p class="login-desc">The Pinnacle Multi-Agent AI Council</p>
    <p class="login-desc" style="font-size: 0.9em; color: #666;">
        6 AI Lords • Opus 4.5 Emperor • Unified Intelligence
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        password = st.text_input("🔐 Enter the Sacred Code", type="password", placeholder="Passcode...")
        
        if st.button("⚔️ ENTER THE SHOGUNATE", use_container_width=True):
            if password == os.getenv("APP_PASSWORD", "shogun2024"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ The gates remain sealed.")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 40px; color: #444; font-size: 0.8em;">
            Powered by Claude Opus 4.5 • GPT-5.2 • Grok 4 • Gemini 2.0 • Kimi K2
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ===== SESSION STATE =====
if "current_theme" not in st.session_state:
    st.session_state.current_theme = "Shogunate"
if "current_session" not in st.session_state:
    st.session_state.current_session = council.create_session("New Quest", st.session_state.current_theme)
if "code_artifact" not in st.session_state:
    st.session_state.code_artifact = "# 🏯 The Council awaits your command...\n\n# Type a request to summon the AI Lords.\n# Use 'search: query' for web search.\n# Paste URLs to analyze web content."
if "last_agent" not in st.session_state:
    st.session_state.last_agent = None

# ===== THEME SYSTEM =====
theme = council.THEMES[st.session_state.current_theme]

# Base styles
st.markdown(f"""
<style>
    /* === BASE THEME === */
    .stApp {{
        background: linear-gradient(135deg, {theme['bg']} 0%, {theme['accent']} 100%);
        color: {theme['text']};
    }}
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {theme['bg']} 0%, {theme['accent']} 100%);
        border-right: 3px solid {theme['secondary']};
    }}
    
    /* === BUTTONS === */
    .stButton > button {{
        background: linear-gradient(135deg, {theme['primary']} 0%, {theme['accent']} 100%);
        color: {theme['text']};
        border: 2px solid {theme['secondary']};
        border-radius: 12px;
        font-weight: bold;
        padding: 10px 20px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px {theme['primary']}40;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, {theme['secondary']} 0%, {theme['primary']} 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px {theme['glow']}60;
    }}
    
    /* === INPUTS === */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background: rgba(0,0,0,0.7) !important;
        color: {theme['text']} !important;
        border: 2px solid {theme['secondary']}80 !important;
        border-radius: 10px !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {theme['primary']} !important;
        box-shadow: 0 0 15px {theme['primary']}40 !important;
    }}
    
    /* === HEADERS === */
    h1, h2, h3 {{
        color: {theme['primary']} !important;
        text-shadow: 2px 2px 10px {theme['accent']};
    }}
    
    /* === CHAT MESSAGES === */
    [data-testid="stChatMessage"] {{
        background: rgba(0,0,0,0.4) !important;
        border-radius: 15px;
        border-left: 5px solid {theme['secondary']};
        padding: 15px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }}
    
    /* === CODE BLOCKS === */
    .stCodeBlock {{
        border: 2px solid {theme['secondary']};
        border-radius: 10px;
        box-shadow: 0 4px 20px {theme['primary']}30;
    }}
    
    /* === AGENT BADGES === */
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
    .agent-inquisitor {{ background: linear-gradient(90deg, #dc143c, #8b0000); color: #fff; }}
    .agent-sage {{ background: linear-gradient(90deg, #9370db, #4b0082); color: #fff; }}
    .agent-innovator {{ background: linear-gradient(90deg, #ff69b4, #ff1493); color: #fff; }}
    
    /* === PHASE INDICATORS === */
    .phase-indicator {{
        background: linear-gradient(90deg, {theme['primary']}, {theme['secondary']});
        padding: 8px 20px;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        margin: 10px 0;
    }}
    
    /* === MOBILE === */
    @media (max-width: 768px) {{
        .stButton > button {{ width: 100%; }}
        h1 {{ font-size: 1.5em !important; }}
    }}
    
    /* === SCROLLBAR === */
    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-track {{ background: {theme['bg']}; }}
    ::-webkit-scrollbar-thumb {{ background: {theme['secondary']}; border-radius: 4px; }}
</style>
""", unsafe_allow_html=True)

# Theme-specific enhancements
if st.session_state.current_theme == "Neon Tokyo":
    st.markdown("""
    <style>
        .stApp {
            background-image: 
                radial-gradient(circle at 10% 10%, rgba(255,154,217,0.15) 0 3px, transparent 4px),
                radial-gradient(circle at 90% 20%, rgba(255,77,166,0.12) 0 4px, transparent 5px),
                radial-gradient(circle at 50% 80%, rgba(255,102,178,0.1) 0 5px, transparent 6px),
                radial-gradient(circle at 30% 60%, rgba(255,200,240,0.08) 0 2px, transparent 3px),
                radial-gradient(circle at 70% 40%, rgba(255,0,255,0.05) 0 6px, transparent 7px);
        }
        
        @keyframes neon-pulse {
            0%, 100% { 
                box-shadow: 0 0 20px #ff1493, 0 0 40px #ff149380, 0 0 60px #ff149340;
            }
            50% { 
                box-shadow: 0 0 30px #ff69b4, 0 0 60px #ff69b480, 0 0 90px #ff69b440;
            }
        }
        
        @keyframes float-rotate {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            25% { transform: translateY(-5px) rotate(1deg); }
            75% { transform: translateY(-5px) rotate(-1deg); }
        }
        
        h1 { animation: float-rotate 4s ease-in-out infinite; }
        .stButton > button { animation: neon-pulse 2s ease-in-out infinite; }
        
        [data-testid="stChatMessage"] {
            border: 1px solid #ff149380;
            box-shadow: 0 0 20px #ff149330;
        }
    </style>
    """, unsafe_allow_html=True)

elif st.session_state.current_theme == "Shogunate":
    st.markdown("""
    <style>
        .stApp {
            background-image: 
                linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)),
                repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 100px,
                    rgba(212,175,55,0.03) 100px,
                    rgba(212,175,55,0.03) 101px
                ),
                repeating-linear-gradient(
                    90deg,
                    transparent,
                    transparent 100px,
                    rgba(196,30,58,0.02) 100px,
                    rgba(196,30,58,0.02) 101px
                );
        }
        
        @keyframes samurai-glow {
            0%, 100% { text-shadow: 0 0 10px #c41e3a, 0 0 20px #d4af37; }
            50% { text-shadow: 0 0 20px #ff6b6b, 0 0 40px #ffd700; }
        }
        
        h1 { animation: samurai-glow 3s ease-in-out infinite; }
    </style>
    """, unsafe_allow_html=True)

elif st.session_state.current_theme == "Bandit Camp":
    st.markdown("""
    <style>
        .stApp {
            background-image: 
                radial-gradient(circle at 20% 30%, rgba(139,115,85,0.15) 0 2px, transparent 3px),
                radial-gradient(circle at 80% 70%, rgba(101,67,33,0.12) 0 3px, transparent 4px),
                radial-gradient(circle at 50% 50%, rgba(160,82,45,0.08) 0 4px, transparent 5px);
        }
    </style>
    """, unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    # Header
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 3em;">🏯</div>
        <div style="font-size: 1.5em; color: {theme['primary']}; font-weight: bold;">LM SHOGUNATE</div>
        <div style="font-size: 0.8em; color: {theme['text']}80;">{council.THEMES[st.session_state.current_theme]['description']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Theme selector
    st.markdown("### 🎨 Choose Your Era")
    new_theme = st.selectbox(
        "Theme",
        list(council.THEMES.keys()),
        index=list(council.THEMES.keys()).index(st.session_state.current_theme),
        label_visibility="collapsed"
    )
    if new_theme != st.session_state.current_theme:
        st.session_state.current_theme = new_theme
        st.rerun()
    
    st.divider()
    
    # New session
    if st.button("➕ Begin New Quest", use_container_width=True):
        st.session_state.current_session = council.create_session("New Quest", st.session_state.current_theme)
        st.session_state.code_artifact = "# New quest initiated...\n# The Council awaits."
        st.rerun()
    
    st.divider()
    
    # Council members
    st.markdown("### 👑 The Council")
    for key, agent in council.AGENTS.items():
        if agent["tier"] <= 2:  # Show main council
            st.markdown(f"{agent['avatar']} **{agent['name']}**")
    
    st.divider()
    
    # Session history
    st.markdown("### 📜 Quest Archives")
    try:
        sessions = council.get_sessions()
        for sess in sessions[:8]:
            theme_icon = {"Shogunate": "⚔️", "Bandit Camp": "🪓", "Neon Tokyo": "🌃"}.get(sess.get('theme', ''), "📜")
            title = sess.get('title', 'Untitled')[:15]
            if st.button(f"{theme_icon} {title}...", key=sess['id'], use_container_width=True):
                st.session_state.current_session = sess['id']
                st.session_state.current_theme = sess.get('theme', 'Shogunate')
                st.rerun()
    except:
        st.caption("📭 No archives yet")
    
    st.divider()
    st.caption(f"💰 Token Budget: {council.SESSION_BUDGET}")
    st.caption(f"🔐 Era: {st.session_state.current_theme}")

# ===== MAIN CONTENT =====
col1, col2 = st.columns([1.4, 1])

with col1:
    st.markdown(f"## 👑 Council Chamber")
    st.markdown(f"*{council.THEMES[st.session_state.current_theme]['description']}*")
    
    # File upload
    uploaded = st.file_uploader(
        "📎 Attach Scrolls",
        type=['pdf', 'txt', 'py', 'js', 'ts', 'jsx', 'tsx', 'json', 'md', 'html', 'css', 'sql'],
        help="Upload files for the council to analyze"
    )
    
    # Chat history
    try:
        history = council.get_history(st.session_state.current_session)
        for msg in history:
            agent_name = msg.get("agent_name", "")
            role = msg["role"]
            
            # Determine avatar and styling
            if role == "user":
                avatar = "👤"
            else:
                # Find agent info
                agent_info = None
                for key, agent in council.AGENTS.items():
                    if agent["name"] in agent_name:
                        agent_info = agent
                        break
                avatar = agent_info["avatar"] if agent_info else "🤖"
            
            with st.chat_message(role, avatar=avatar):
                if agent_name:
                    # Color-coded agent name
                    agent_class = "emperor" if "Emperor" in agent_name or "天皇" in agent_name else \
                                  "strategist" if "Strategist" in agent_name or "軍師" in agent_name else \
                                  "executor" if "Executor" in agent_name or "刀匠" in agent_name else \
                                  "inquisitor" if "Inquisitor" in agent_name or "審問官" in agent_name else \
                                  "sage" if "Sage" in agent_name or "賢者" in agent_name else \
                                  "innovator" if "Innovator" in agent_name or "発明家" in agent_name else ""
                    
                    st.markdown(f'<span class="agent-badge agent-{agent_class}">{agent_name}</span>', unsafe_allow_html=True)
                
                st.markdown(msg["content"])
                
                # Extract code for artifact
                if "```" in msg["content"]:
                    try:
                        parts = msg["content"].split("```")
                        if len(parts) >= 2:
                            block = parts[1]
                            if "\n" in block:
                                first_line, rest = block.split("\n", 1)
                                if first_line.strip() in ["python", "javascript", "js", "typescript", "ts", "html", "css", "json", "sql"]:
                                    block = rest
                            st.session_state.code_artifact = block.strip()
                    except:
                        pass
    except:
        st.info("📜 No messages yet. Command the council to begin your quest.")
    
    # User input
    user_input = st.chat_input("Command the council... (use 'search: query' for web search)")
    
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
                user_input += f"\n\n[ATTACHED FILE: {uploaded.name}]\n```\n{file_text[:10000]}\n```"
            except Exception as e:
                user_input += f"\n\n[FILE ERROR: {str(e)}]"
        
        # Show user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # Run the council
        with st.status("⚡ The Council deliberates...", expanded=True) as status:
            try:
                for agent, content, msg_type in council.run_council(
                    st.session_state.current_theme,
                    user_input,
                    st.session_state.current_session
                ):
                    if msg_type == "system":
                        st.markdown(f"🔔 {content}")
                    else:
                        # Find agent info for styling
                        agent_info = None
                        for key, a in council.AGENTS.items():
                            if a["name"] in agent:
                                agent_info = a
                                break
                        
                        avatar = agent_info["avatar"] if agent_info else "🤖"
                        
                        with st.chat_message("assistant", avatar=avatar):
                            agent_class = "emperor" if "Emperor" in agent or "天皇" in agent else \
                                          "strategist" if "Strategist" in agent or "軍師" in agent else \
                                          "executor" if "Executor" in agent or "刀匠" in agent else \
                                          "inquisitor" if "Inquisitor" in agent or "審問官" in agent else \
                                          "sage" if "Sage" in agent or "賢者" in agent else \
                                          "innovator" if "Innovator" in agent or "発明家" in agent else ""
                            
                            st.markdown(f'<span class="agent-badge agent-{agent_class}">{agent}</span>', unsafe_allow_html=True)
                            st.markdown(content)
                        
                        # Update artifact
                        if "```" in content:
                            try:
                                parts = content.split("```")
                                if len(parts) >= 2:
                                    block = parts[1]
                                    if "\n" in block:
                                        first_line, rest = block.split("\n", 1)
                                        if first_line.strip() in ["python", "javascript", "js", "typescript", "ts", "html", "css", "json", "sql"]:
                                            block = rest
                                    st.session_state.code_artifact = block.strip()
                            except:
                                pass
                        
                        st.session_state.last_agent = agent
                
                status.update(label="✅ The Council has spoken!", state="complete")
            except Exception as e:
                status.update(label=f"❌ Error: {str(e)}", state="error")
        
        st.rerun()

with col2:
    st.markdown("## 📜 Artifacts")
    
    # Language detection
    code = st.session_state.code_artifact
    lang = "python"
    if code.strip().startswith(("{", "[")):
        lang = "json"
    elif "<html" in code.lower() or "<!doctype" in code.lower():
        lang = "html"
    elif "<" in code and ">" in code and ("div" in code or "span" in code or "class=" in code):
        lang = "html"
    elif "function" in code or "const " in code or "let " in code or "=>" in code:
        lang = "javascript"
    elif "SELECT" in code.upper() or "INSERT" in code.upper():
        lang = "sql"
    
    # Code display
    st.code(code, language=lang, line_numbers=True)
    
    # Actions
    col_a, col_b = st.columns(2)
    with col_a:
        ext = {"python": "py", "javascript": "js", "json": "json", "html": "html", "sql": "sql"}.get(lang, "txt")
        st.download_button(
            "💾 Download",
            st.session_state.code_artifact,
            f"council_solution.{ext}",
            use_container_width=True
        )
    with col_b:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.code_artifact = "# Cleared."
            st.rerun()
    
    st.divider()
    
    # Council info
    st.markdown("### 🏯 Council Hierarchy")
    st.markdown("""
    | Tier | Agent | Role |
    |------|-------|------|
    | 👑 | **Emperor** (Opus 4.5) | Final Arbiter |
    | ⭐ | **Strategist** (Sonnet) | Planning |
    | ⭐ | **Executor** (GPT-5.2) | Coding |
    | ⭐ | **Inquisitor** (Grok) | Critique |
    | ⭐ | **Sage** (Kimi K2) | Reasoning |
    | ⭐ | **Innovator** (Gemini) | Creativity |
    """)
    
    st.divider()
    
    # Tips
    with st.expander("💡 Power Tips"):
        st.markdown("""
        - **Web Search**: Type `search: your query` to search the web
        - **Read URLs**: Paste any URL and the council will analyze its content
        - **Upload Files**: Attach PDFs, code, or text files for analysis
        - **Theme Switch**: Change eras in the sidebar for different vibes
        - **Memory**: The council remembers successful solutions
        """)
