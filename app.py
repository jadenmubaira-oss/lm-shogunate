"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    NEURAL COUNCIL - THE ABSOLUTE PINNACLE                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

The most beautiful AI interface. 4 models working as one.
Neon pink/sunset aesthetic. Glassmorphism. Premium animations.
"""

import streamlit as st
import os
import re
import base64
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Neural Council",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

import council


def render_message_with_images(content: str):
    """Render message and display any embedded images."""
    st.markdown(content)
    
    # Extract and display images
    patterns = [
        r'!\[[^\]]*\]\(([^\)]+)\)',
        r'(https://[^\s<>"]+\.(?:png|jpg|jpeg|gif|webp))',
        r'(https://oaidalleapiprodscus[^\s<>"]+)',
    ]
    
    displayed = set()
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            url = match.group(1) if match.lastindex else match.group(0)
            if url and url not in displayed:
                try:
                    st.image(url, width=450)
                    displayed.add(url)
                except:
                    pass


# ═══════════════════════════════════════════════════════════════════════════════
# STUNNING CSS - NEON PINK/SUNSET AESTHETIC
# ═══════════════════════════════════════════════════════════════════════════════

NEON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg-dark: #0a0a0f;
    --bg-card: rgba(20, 15, 30, 0.8);
    --neon-pink: #ff1493;
    --neon-magenta: #ff00ff;
    --sunset-orange: #ff6b35;
    --sunset-pink: #ff8577;
    --soft-pink: #ffb6c1;
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.7);
    --glass-border: rgba(255, 20, 147, 0.3);
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: linear-gradient(135deg, 
        #0a0a0f 0%, 
        #1a0a1f 25%,
        #150520 50%,
        #0f0515 75%,
        #0a0a0f 100%);
    background-attachment: fixed;
}

/* Animated background glow */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(ellipse at 20% 20%, rgba(255, 20, 147, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(255, 107, 53, 0.1) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(255, 0, 255, 0.05) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* Sidebar - Glassmorphism */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, 
        rgba(20, 10, 35, 0.95) 0%, 
        rgba(15, 5, 25, 0.98) 100%);
    border-right: 1px solid var(--glass-border);
    backdrop-filter: blur(20px);
}

[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--neon-pink), var(--neon-magenta), var(--sunset-orange));
}

/* Buttons - Neon glow effect */
.stButton > button {
    background: linear-gradient(135deg, 
        rgba(255, 20, 147, 0.2) 0%, 
        rgba(255, 0, 255, 0.15) 100%);
    color: var(--text-primary);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    font-weight: 600;
    padding: 12px 24px;
    min-height: 48px;
    backdrop-filter: blur(10px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-shadow: 0 0 10px rgba(255, 20, 147, 0.5);
}

.stButton > button:hover {
    background: linear-gradient(135deg, 
        rgba(255, 20, 147, 0.4) 0%, 
        rgba(255, 0, 255, 0.3) 100%);
    border-color: var(--neon-pink);
    transform: translateY(-2px);
    box-shadow: 
        0 0 20px rgba(255, 20, 147, 0.4),
        0 0 40px rgba(255, 20, 147, 0.2),
        0 10px 30px rgba(0, 0, 0, 0.3);
}

/* Input fields - Glass effect */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
[data-testid="stChatInput"] textarea {
    background: rgba(20, 10, 35, 0.6) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--neon-pink) !important;
    box-shadow: 0 0 20px rgba(255, 20, 147, 0.3) !important;
}

/* Chat messages - Premium glass cards */
[data-testid="stChatMessage"] {
    background: linear-gradient(135deg, 
        rgba(25, 15, 40, 0.7) 0%, 
        rgba(20, 10, 30, 0.8) 100%) !important;
    border: 1px solid rgba(255, 20, 147, 0.2);
    border-radius: 20px;
    padding: 20px;
    margin: 12px 0;
    backdrop-filter: blur(15px);
    transition: all 0.3s ease;
}

[data-testid="stChatMessage"]:hover {
    border-color: rgba(255, 20, 147, 0.4);
    box-shadow: 0 0 30px rgba(255, 20, 147, 0.15);
}

/* Agent badges - Glowing pills */
.agent-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 30px;
    font-size: 0.85em;
    font-weight: 600;
    margin-bottom: 10px;
    letter-spacing: 0.5px;
}

.agent-emperor {
    background: linear-gradient(90deg, #ffd700, #ff8c00);
    color: #000;
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
}

.agent-strategist {
    background: linear-gradient(90deg, #00bfff, #1e90ff);
    color: #fff;
    box-shadow: 0 0 20px rgba(0, 191, 255, 0.5);
}

.agent-executor {
    background: linear-gradient(90deg, #00ff88, #00cc66);
    color: #000;
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
}

.agent-sage {
    background: linear-gradient(90deg, #bf00ff, #8000ff);
    color: #fff;
    box-shadow: 0 0 20px rgba(191, 0, 255, 0.5);
}

/* Headers - Gradient text */
h1, h2, h3 {
    background: linear-gradient(90deg, var(--neon-pink), var(--sunset-orange));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
}

/* Code blocks - Dark glass */
pre, code {
    background: rgba(10, 5, 20, 0.8) !important;
    border: 1px solid rgba(255, 20, 147, 0.2) !important;
    border-radius: 12px !important;
}

/* Expander - Glass style */
.streamlit-expanderHeader {
    background: rgba(20, 10, 35, 0.6) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
}

/* Selectbox - Glass */
.stSelectbox > div > div {
    background: rgba(20, 10, 35, 0.6) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(20, 10, 35, 0.5);
    border: 2px dashed var(--glass-border);
    border-radius: 16px;
    padding: 20px;
}

/* Divider - Gradient */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, 
        transparent 0%, 
        var(--neon-pink) 50%, 
        transparent 100%);
    margin: 20px 0;
}

/* Status indicator - Pulsing */
.stStatus {
    background: rgba(20, 10, 35, 0.8) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 16px !important;
}

/* Scrollbar - Neon */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(10, 5, 20, 0.5);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--neon-pink), var(--neon-magenta));
    border-radius: 10px;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .stApp { padding: 0.5rem !important; }
    h1 { font-size: 1.8em !important; }
    h2 { font-size: 1.4em !important; }
    .stButton > button { width: 100% !important; }
    [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
}

/* Animations */
@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(255, 20, 147, 0.3); }
    50% { box-shadow: 0 0 40px rgba(255, 20, 147, 0.5); }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

/* Logo animation */
.logo-container {
    animation: float 3s ease-in-out infinite;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(20, 10, 35, 0.5);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    color: var(--text-secondary);
    padding: 10px 20px;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(255, 20, 147, 0.3), rgba(255, 0, 255, 0.2));
    border-color: var(--neon-pink);
    color: var(--text-primary);
}

/* Success/Error messages */
.stSuccess, .stError, .stWarning, .stInfo {
    background: rgba(20, 10, 35, 0.8) !important;
    border-radius: 12px !important;
    border: 1px solid var(--glass-border) !important;
}
</style>
"""

st.markdown(NEON_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN CAPTURE
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
        
        window.parent.postMessage({type: 'screenshot', data: dataUrl}, '*');
        document.getElementById('screenshot-status').innerText = '✅ Captured!';
        document.getElementById('screenshot-data').value = dataUrl;
    } catch (e) {
        document.getElementById('screenshot-status').innerText = '❌ ' + e.message;
    }
}
</script>
<div style="margin: 10px 0;">
    <button onclick="captureScreen()" style="
        background: linear-gradient(135deg, #ff1493, #ff00ff);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        cursor: pointer;
        font-weight: 600;
        font-size: 14px;
        box-shadow: 0 0 20px rgba(255, 20, 147, 0.4);
        transition: all 0.3s ease;
    ">
        📸 Capture Screen
    </button>
    <span id="screenshot-status" style="margin-left: 12px; color: rgba(255,255,255,0.7);"></span>
    <input type="hidden" id="screenshot-data" name="screenshot">
</div>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════════

params = st.query_params

def get_current_user():
    """Get current user from session_state only (not URL - security fix)."""
    if "user" in st.session_state:
        return st.session_state.user
    return None

def logout():
    if "user" in st.session_state:
        del st.session_state.user
    if "session_id" in st.session_state:
        del st.session_state.session_id
    st.rerun()

user = get_current_user()

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE - STUNNING
# ═══════════════════════════════════════════════════════════════════════════════

if not user:
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <div class="logo-container" style="font-size: 5em; margin-bottom: 20px;">🧠</div>
        <h1 style="
            font-size: 3.5em;
            margin: 0;
            background: linear-gradient(90deg, #ff1493, #ff00ff, #ff6b35);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            letter-spacing: -2px;
        ">NEURAL COUNCIL</h1>
        <p style="
            color: rgba(255,255,255,0.6);
            font-size: 1.3em;
            margin-top: 15px;
            font-weight: 300;
        ">4 AI Models. One Unified Intelligence.</p>
        <p style="
            color: rgba(255,255,255,0.4);
            font-size: 0.95em;
            margin-top: 8px;
        ">Claude Opus • Claude Sonnet • GPT-5.2 • DeepSeek V3</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Sign In", "✨ Create Account"])
        
        with tab1:
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("⚡ Enter", use_container_width=True, key="login_btn"):
                if email and password:
                    user_data, error = council.login_user(email, password)
                    if user_data:
                        st.session_state.user = user_data
                        # SECURITY FIX: Don't store token in URL - it's shareable!
                        # Token stays in session_state only (server-side)
                        st.success("✅ Welcome back!")
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
                else:
                    st.warning("Enter email and password")
        
        with tab2:
            reg_email = st.text_input("Email", key="reg_email", placeholder="you@example.com")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            reg_pass2 = st.text_input("Confirm", type="password", key="reg_pass2")
            
            if st.button("🚀 Create Account", use_container_width=True, key="reg_btn"):
                if reg_email and reg_pass:
                    if reg_pass != reg_pass2:
                        st.error("❌ Passwords don't match")
                    elif len(reg_pass) < 6:
                        st.error("❌ Min 6 characters")
                    else:
                        user_id, error = council.register_user(reg_email, reg_pass)
                        if user_id:
                            st.success("✅ Account created! Sign in now.")
                        else:
                            st.error(f"❌ {error}")
                else:
                    st.warning("Fill all fields")
    
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

user_id = user["id"]

if "session_id" not in st.session_state:
    saved = params.get("session")
    if saved:
        st.session_state.session_id = saved
    else:
        st.session_state.session_id = council.create_session("New Chat", "Neon", user_id)
        st.query_params["session"] = st.session_state.session_id

if "artifact" not in st.session_state:
    st.session_state.artifact = "# 🧠 Ready to assist..."

if "screenshot" not in st.session_state:
    st.session_state.screenshot = None

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 25px 0;">
        <div style="font-size: 2.5em; margin-bottom: 10px;">🧠</div>
        <div style="
            font-size: 1.3em;
            background: linear-gradient(90deg, #ff1493, #ff6b35);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            letter-spacing: 1px;
        ">NEURAL COUNCIL</div>
        <div style="font-size: 0.8em; color: rgba(255,255,255,0.5); margin-top: 5px;">
            {user.get('email', 'User')[:25]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Sign Out", use_container_width=True):
        logout()
    
    st.divider()
    
    if st.button("✨ New Chat", use_container_width=True):
        new_id = council.create_session("New Chat", "Neon", user_id)
        st.session_state.session_id = new_id
        st.query_params["session"] = new_id
        st.session_state.artifact = "# New chat..."
        council.reset_tokens()
        st.rerun()
    
    st.divider()
    
    st.markdown("### 🧠 The Council")
    for key, a in council.AGENTS.items():
        st.markdown(f"{a['avatar']} **{a['name']}**")
    
    st.divider()
    
    st.markdown("### 📂 Recent")
    try:
        for sess in council.get_sessions(user_id)[:8]:
            if sess['id'] == st.session_state.session_id:
                continue
            title = sess.get('title', 'Untitled')[:20]
            c1, c2 = st.columns([4, 1])
            with c1:
                if st.button(f"💬 {title}", key=f"s_{sess['id']}", use_container_width=True):
                    st.session_state.session_id = sess['id']
                    st.query_params["session"] = sess['id']
                    st.rerun()
            with c2:
                if st.button("×", key=f"d_{sess['id']}"):
                    council.delete_session(sess['id'])
                    st.rerun()
    except:
        st.caption("No history")
    
    st.divider()
    st.caption(f"⚡ {council.get_tokens_used():,} tokens")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("## 💬 Chat")
    
    with st.expander("📸 Screen Capture"):
        st.markdown(SCREEN_CAPTURE_JS, unsafe_allow_html=True)
        screenshot_b64 = st.text_area("Paste data:", key="ss_input", height=60, placeholder="Screenshot data...")
        if screenshot_b64 and screenshot_b64.startswith("data:"):
            st.session_state.screenshot = screenshot_b64
            st.success("✅ Ready!")
    
    uploaded = st.file_uploader("📎 Attach", type=['pdf', 'txt', 'py', 'js', 'json', 'md', 'html', 'css', 'png', 'jpg'])
    
    # History
    try:
        history = council.get_history(st.session_state.session_id)
        if history:
            for msg in history:
                agent_name = msg.get("agent_name", "")
                role = msg["role"]
                avatar = "👤" if role == "user" else next((a["avatar"] for a in council.AGENTS.values() if a["name"] in str(agent_name)), "🤖")
                with st.chat_message(role, avatar=avatar):
                    if agent_name:
                        cls = "emperor" if "Emperor" in agent_name else "strategist" if "Strategist" in agent_name else "executor" if "Executor" in agent_name else "sage" if "Sage" in agent_name else ""
                        st.markdown(f'<span class="agent-badge agent-{cls}">{agent_name}</span>', unsafe_allow_html=True)
                    render_message_with_images(msg["content"])
                    if "```" in str(msg["content"]):
                        try:
                            st.session_state.artifact = msg["content"].split("```")[1].split("\n", 1)[-1].strip()
                        except:
                            pass
        else:
            st.info("✨ Start a conversation...")
    except Exception as e:
        st.error(f"⚠️ Error loading chat history: {str(e)}")
    
    # Input
    user_input = st.chat_input("Ask anything... (image: prompt, video: prompt, search: query)")
    
    if user_input:
        # Handle uploaded file
        uploaded_image_b64 = None
        if uploaded:
            try:
                if uploaded.type == "application/pdf":
                    from PyPDF2 import PdfReader
                    file_text = "\n".join([p.extract_text() or "" for p in PdfReader(uploaded).pages])
                    user_input += f"\n\n[FILE: {uploaded.name}]\n```\n{file_text[:8000]}\n```"
                elif uploaded.type.startswith("image/"):
                    # FIXED: Encode image as base64 so AI can SEE it!
                    import base64
                    uploaded.seek(0)
                    image_bytes = uploaded.read()
                    uploaded_image_b64 = f"data:{uploaded.type};base64,{base64.b64encode(image_bytes).decode()}"
                    user_input += f"\n\n[IMAGE ATTACHED: {uploaded.name}]"
                else:
                    file_text = uploaded.read().decode('utf-8', errors='ignore')
                    user_input += f"\n\n[FILE: {uploaded.name}]\n```\n{file_text[:8000]}\n```"
            except Exception as e:
                user_input += f"\n\n[FILE ERROR: {str(e)}]"
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # Use uploaded image OR screenshot (prefer uploaded image)
        screenshot = uploaded_image_b64 or st.session_state.get("screenshot")
        st.session_state.screenshot = None
        
        with st.status("⚡ Council processing...", expanded=True) as status:
            try:
                final_answer = None
                final_agent = None
                intermediate_responses = []
                
                for agent, content, msg_type in council.run_council("Neon", user_input, st.session_state.session_id, user_id, screenshot):
                    if msg_type == "system":
                        st.markdown(f"🔔 {content}")
                    elif msg_type == "image":
                        st.image(content, width=500)
                    elif msg_type == "video":
                        st.video(content)
                    else:
                        # Check if this is the final answer (Emperor or Sage-Approved)
                        is_final = "Emperor" in agent or "Sage-Approved" in agent or "(Final)" in agent
                        
                        if is_final:
                            final_answer = content
                            final_agent = agent
                        else:
                            # Store intermediate response for expander
                            avatar = next((a["avatar"] for a in council.AGENTS.values() if a["name"] in str(agent)), "🤖")
                            intermediate_responses.append((agent, content, avatar))
                        
                        if "```" in str(content):
                            try:
                                st.session_state.artifact = content.split("```")[1].split("\n", 1)[-1].strip()
                            except:
                                pass
                
                status.update(label="✅ Complete!", state="complete")
            except Exception as e:
                status.update(label=f"❌ {str(e)}", state="error")
        
        # Display intermediate responses in expanders
        if intermediate_responses:
            with st.expander("🔍 View Council Deliberation", expanded=False):
                for agent, content, avatar in intermediate_responses:
                    cls = "strategist" if "Strategist" in agent else "executor" if "Executor" in agent else "sage" if "Sage" in agent else ""
                    st.markdown(f'<span class="agent-badge agent-{cls}">{agent}</span>', unsafe_allow_html=True)
                    st.markdown(content[:2000] + ("..." if len(content) > 2000 else ""))
                    st.divider()
        
        # Display final answer prominently
        if final_answer:
            avatar = "👑" if "Emperor" in str(final_agent) else "⚔️"
            with st.chat_message("assistant", avatar=avatar):
                st.markdown(f'<span class="agent-badge agent-emperor">✨ {final_agent}</span>', unsafe_allow_html=True)
                render_message_with_images(final_answer)
        
        st.rerun()

with col2:
    st.markdown("## 📄 Artifacts")
    
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
    
    st.markdown("### 🧠 The Models")
    st.markdown("""
    | Tier | Agent | Model |
    |------|-------|-------|
    | 👑 | Emperor | Claude Opus 4.5 |
    | 🎯 | Strategist | Claude Sonnet 4.5 |
    | ⚔️ | Executor | GPT-5.2 |
    | 📿 | Sage | DeepSeek V3.2 |
    """)
    
    with st.expander("💡 Commands"):
        st.markdown("""
        - `image: [prompt]` → Generate image
        - `video: [prompt]` → Generate video
        - `search: [query]` → Web search
        - Natural: "create an image of..."
        - Natural: "make a video of..."
        """)
