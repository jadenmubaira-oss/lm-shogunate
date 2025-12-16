"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              LM SHOGUNATE: MULTI-USER PINNACLE UI                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Features:
• Multi-user authentication (email/password)
• Per-user sessions, themes, memories
• Screen capture (desktop browsers)
• 4-agent council with parallel execution
"""

import streamlit as st
import os
import base64
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="LM Shogunate", page_icon="🏯", layout="wide", initial_sidebar_state="expanded")

import council

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN CAPTURE JAVASCRIPT
# ═══════════════════════════════════════════════════════════════════════════════

SCREEN_CAPTURE_JS = """
<script>
async function captureScreen() {
    try {
        const stream = await navigator.mediaDevices.getDisplayMedia({video: {cursor: "always"}, audio: false});
        const track = stream.getVideoTracks()[0];
        const imageCapture = new ImageCapture(track);
        const bitmap = await imageCapture.grabFrame();
        
        const canvas = document.createElement('canvas');
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        canvas.getContext('2d').drawImage(bitmap, 0, 0);
        
        const dataUrl = canvas.toDataURL('image/png');
        track.stop();
        
        // Store in session storage for Streamlit to read
        window.parent.postMessage({type: 'screenshot', data: dataUrl}, '*');
        document.getElementById('screenshot-status').innerText = '✅ Screenshot captured!';
        document.getElementById('screenshot-data').value = dataUrl;
    } catch (e) {
        document.getElementById('screenshot-status').innerText = '❌ ' + e.message;
    }
}
</script>
<div style="margin: 10px 0;">
    <button onclick="captureScreen()" style="background: #c41e3a; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold;">
        📸 Capture Screen
    </button>
    <span id="screenshot-status" style="margin-left: 10px; color: #888;"></span>
    <input type="hidden" id="screenshot-data" name="screenshot">
</div>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION STATE
# ═══════════════════════════════════════════════════════════════════════════════

params = st.query_params

def get_current_user():
    """Get current user from session or token."""
    if "user" in st.session_state:
        return st.session_state.user
    token = params.get("token")
    if token:
        user = council.verify_token(token)
        if user:
            st.session_state.user = user
            return user
    return None

def logout():
    """Clear user session."""
    if "user" in st.session_state:
        del st.session_state.user
    if "token" in st.query_params:
        del st.query_params["token"]
    if "session_id" in st.session_state:
        del st.session_state.session_id
    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN/REGISTER PAGE
# ═══════════════════════════════════════════════════════════════════════════════

user = get_current_user()

if not user:
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 50%, #0a0a0a 100%); }
        @keyframes pulse { 
            0%, 100% { text-shadow: 0 0 20px #c41e3a, 0 0 40px #c41e3a40; }
            50% { text-shadow: 0 0 40px #ff6b6b, 0 0 80px #c41e3a60; }
        }
        .login-title { font-size: 5em; text-align: center; margin-bottom: 0; margin-top: 40px; }
        .login-subtitle { 
            font-size: 2.5em; text-align: center; color: #c41e3a;
            animation: pulse 2s ease-in-out infinite;
            font-family: 'Times New Roman', serif; letter-spacing: 8px;
        }
        .login-desc { text-align: center; color: #888; font-size: 1.2em; margin-top: 20px; }
    </style>
    <div class="login-title">🏯</div>
    <div class="login-subtitle">LM SHOGUNATE</div>
    <p class="login-desc">The Ultimate 4-Agent AI Council</p>
    <p class="login-desc" style="font-size: 0.9em; color: #666;">
        Claude Opus 4.5 • Claude Sonnet 4.5 • GPT-5.2 • DeepSeek V3.2
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Password...")
            
            if st.button("⚔️ ENTER THE SHOGUNATE", use_container_width=True, key="login_btn"):
                if email and password:
                    user_data, error = council.login_user(email, password)
                    if user_data:
                        st.session_state.user = user_data
                        st.query_params["token"] = user_data["token"]
                        st.success("✅ Welcome back!")
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
                else:
                    st.warning("Please enter email and password")
        
        with tab2:
            reg_email = st.text_input("Email", key="reg_email", placeholder="you@example.com")
            reg_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Choose a password...")
            reg_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="Confirm password...")
            
            if st.button("🎌 CREATE ACCOUNT", use_container_width=True, key="reg_btn"):
                if reg_email and reg_pass:
                    if reg_pass != reg_pass2:
                        st.error("❌ Passwords don't match")
                    elif len(reg_pass) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        user_id, error = council.register_user(reg_email, reg_pass)
                        if user_id:
                            st.success("✅ Account created! Please log in.")
                        else:
                            st.error(f"❌ {error}")
                else:
                    st.warning("Please fill all fields")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 40px; color: #444; font-size: 0.8em;">
            Powered by Azure AI Foundry • Supabase Auth
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP (Authenticated)
# ═══════════════════════════════════════════════════════════════════════════════

user_id = user["id"]

# Load user profile
profile = council.get_user_profile(user_id)

# Theme
if "theme" not in st.session_state:
    st.session_state.theme = profile.get("theme", "Shogunate")

# Session
if "session_id" not in st.session_state:
    saved = params.get("session")
    if saved:
        st.session_state.session_id = saved
    else:
        st.session_state.session_id = council.create_session("New Quest", st.session_state.theme, user_id)
        st.query_params["session"] = st.session_state.session_id

if "artifact" not in st.session_state:
    st.session_state.artifact = "# 🏯 The Council awaits..."

if "screenshot" not in st.session_state:
    st.session_state.screenshot = None

theme = council.THEMES[st.session_state.theme]

# CSS
st.markdown(f"""
<style>
    .stApp {{ background: linear-gradient(135deg, {theme['bg']} 0%, {theme['accent']} 100%); color: {theme['text']}; }}
    [data-testid="stSidebar"] {{ background: linear-gradient(180deg, {theme['bg']} 0%, {theme['accent']} 100%); border-right: 3px solid {theme['secondary']}; }}
    .stButton > button {{ background: linear-gradient(135deg, {theme['primary']} 0%, {theme['accent']} 100%); color: {theme['text']}; border: 2px solid {theme['secondary']}; border-radius: 12px; font-weight: bold; padding: 12px 24px; min-height: 44px; }}
    .stButton > button:hover {{ background: linear-gradient(135deg, {theme['secondary']} 0%, {theme['primary']} 100%); transform: translateY(-2px); }}
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{ background: rgba(0,0,0,0.7) !important; color: {theme['text']} !important; border: 2px solid {theme['secondary']}80 !important; border-radius: 10px !important; min-height: 44px; }}
    h1, h2, h3 {{ color: {theme['primary']} !important; }}
    [data-testid="stChatMessage"] {{ background: rgba(0,0,0,0.4) !important; border-radius: 15px; border-left: 5px solid {theme['secondary']}; padding: 15px; margin: 10px 0; }}
    .agent-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; margin-bottom: 8px; }}
    .agent-emperor {{ background: linear-gradient(90deg, #ffd700, #ffaa00); color: #000; }}
    .agent-strategist {{ background: linear-gradient(90deg, #4a90d9, #2e5a8b); color: #fff; }}
    .agent-executor {{ background: linear-gradient(90deg, #50c878, #228b22); color: #fff; }}
    .agent-sage {{ background: linear-gradient(90deg, #9370db, #4b0082); color: #fff; }}
    @media (max-width: 768px) {{
        .stApp {{ padding: 0.5rem !important; }}
        h1 {{ font-size: 1.5em !important; }}
        .stButton > button {{ width: 100% !important; }}
        [data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; }}
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
        <div style="font-size: 1.2em; color: {theme['primary']}; font-weight: bold;">LM SHOGUNATE</div>
        <div style="font-size: 0.8em; color: {theme['text']}80;">👤 {user.get('email', 'User')[:20]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.divider()
    
    # Theme
    st.markdown("### 🎨 Theme")
    new_theme = st.selectbox("Theme", list(council.THEMES.keys()), index=list(council.THEMES.keys()).index(st.session_state.theme), label_visibility="collapsed")
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        council.update_user_profile(user_id, new_theme)
        st.rerun()
    
    st.divider()
    
    if st.button("➕ New Quest", use_container_width=True):
        new_id = council.create_session("New Quest", st.session_state.theme, user_id)
        st.session_state.session_id = new_id
        st.query_params["session"] = new_id
        st.session_state.artifact = "# New quest..."
        council.reset_tokens()
        st.rerun()
    
    st.divider()
    
    # Council
    st.markdown("### 👑 Council")
    for key, a in council.AGENTS.items():
        st.markdown(f"{a['avatar']} **{a['name']}**")
    
    st.divider()
    
    # Sessions
    st.markdown("### 📜 Archives")
    try:
        for sess in council.get_sessions(user_id)[:10]:
            if sess['id'] == st.session_state.session_id:
                continue
            title = sess.get('title', 'Untitled')[:18]
            c1, c2 = st.columns([4, 1])
            with c1:
                if st.button(f"📜 {title}", key=f"s_{sess['id']}", use_container_width=True):
                    st.session_state.session_id = sess['id']
                    st.query_params["session"] = sess['id']
                    st.rerun()
            with c2:
                if st.button("🗑️", key=f"d_{sess['id']}"):
                    council.delete_session(sess['id'])
                    st.rerun()
    except:
        st.caption("📭 No archives")
    
    st.divider()
    st.caption(f"💰 Tokens: {council.get_tokens_used():,}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

col1, col2 = st.columns([1.4, 1])

with col1:
    st.markdown("## 👑 Council Chamber")
    
    # Screen capture
    with st.expander("📸 Screen Capture (Desktop Only)"):
        st.markdown(SCREEN_CAPTURE_JS, unsafe_allow_html=True)
        st.info("Click the button to share your screen. A screenshot will be attached to your next message.")
        screenshot_b64 = st.text_area("Paste screenshot data (base64):", key="screenshot_input", height=68, placeholder="After capturing, the data appears here...")
        if screenshot_b64 and screenshot_b64.startswith("data:"):
            st.session_state.screenshot = screenshot_b64
            st.success("✅ Screenshot ready!")
    
    # File upload
    uploaded = st.file_uploader("📎 Attach Files", type=['pdf', 'txt', 'py', 'js', 'json', 'md', 'html', 'css', 'png', 'jpg'])
    
    # History
    try:
        for msg in council.get_history(st.session_state.session_id):
            agent_name = msg.get("agent_name", "")
            role = msg["role"]
            avatar = "👤" if role == "user" else next((a["avatar"] for a in council.AGENTS.values() if a["name"] in str(agent_name)), "🤖")
            with st.chat_message(role, avatar=avatar):
                if agent_name:
                    cls = "emperor" if "Emperor" in agent_name else "strategist" if "Strategist" in agent_name else "executor" if "Executor" in agent_name else "sage" if "Sage" in agent_name else ""
                    st.markdown(f'<span class="agent-badge agent-{cls}">{agent_name}</span>', unsafe_allow_html=True)
                st.markdown(msg["content"])
                if "```" in str(msg["content"]):
                    try:
                        st.session_state.artifact = msg["content"].split("```")[1].split("\n", 1)[-1].strip()
                    except:
                        pass
    except:
        st.info("📜 No messages yet.")
    
    # Input
    user_input = st.chat_input("Command the council... (search: query, image: prompt)")
    
    if user_input:
        # Handle file
        if uploaded:
            try:
                if uploaded.type == "application/pdf":
                    from PyPDF2 import PdfReader
                    file_text = "\n".join([p.extract_text() or "" for p in PdfReader(uploaded).pages])
                elif uploaded.type.startswith("image/"):
                    img_b64 = base64.b64encode(uploaded.read()).decode()
                    file_text = f"[IMAGE ATTACHED: {uploaded.name}]"
                else:
                    file_text = uploaded.read().decode('utf-8', errors='ignore')
                user_input += f"\n\n[FILE: {uploaded.name}]\n```\n{file_text[:8000]}\n```"
            except Exception as e:
                user_input += f"\n\n[FILE ERROR: {str(e)}]"
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # Get screenshot
        screenshot = st.session_state.get("screenshot")
        st.session_state.screenshot = None  # Clear after use
        
        with st.status("⚡ Council deliberating...", expanded=True) as status:
            try:
                for agent, content, msg_type in council.run_council(st.session_state.theme, user_input, st.session_state.session_id, user_id, screenshot):
                    if msg_type == "system":
                        st.markdown(f"🔔 {content}")
                    elif msg_type == "image":
                        st.image(content, width=512)
                    elif msg_type == "video":
                        st.video(content)
                    else:
                        avatar = next((a["avatar"] for a in council.AGENTS.values() if a["name"] in str(agent)), "🤖")
                        with st.chat_message("assistant", avatar=avatar):
                            cls = "emperor" if "Emperor" in agent else "strategist" if "Strategist" in agent else "executor" if "Executor" in agent else "sage" if "Sage" in agent else ""
                            st.markdown(f'<span class="agent-badge agent-{cls}">{agent}</span>', unsafe_allow_html=True)
                            st.markdown(content)
                        if "```" in str(content):
                            try:
                                st.session_state.artifact = content.split("```")[1].split("\n", 1)[-1].strip()
                            except:
                                pass
                status.update(label="✅ Done!", state="complete")
            except Exception as e:
                status.update(label=f"❌ {str(e)}", state="error")
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
    
    st.code(code, language=lang, line_numbers=True)
    
    c1, c2 = st.columns(2)
    with c1:
        ext = {"python": "py", "javascript": "js", "json": "json", "html": "html"}.get(lang, "txt")
        st.download_button("💾 Download", code, f"code.{ext}", use_container_width=True)
    with c2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.artifact = "# Cleared"
            st.rerun()
    
    st.divider()
    
    st.markdown("### 🏯 Council")
    st.markdown("""
    | Tier | Agent | Model |
    |------|-------|-------|
    | 👑 | Emperor | Claude Opus 4.5 |
    | ⭐ | Strategist | Claude Sonnet 4.5 |
    | ⭐ | Executor | GPT-5.2 |
    | 📿 | Sage | DeepSeek V3.2 |
    """)
    
    with st.expander("💡 Tips"):
        st.markdown("""
        - `search: query` - Web search
        - `image: prompt` - Generate image
        - `video: prompt` - Generate video
        - Upload files for analysis
        - Use screen capture (desktop)
        """)
