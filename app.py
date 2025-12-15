import streamlit as st
import council
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader

load_dotenv()

st.set_page_config(
    page_title="LM Shogunate",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== AUTH =====
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🏯 LM SHOGUNATE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Enter passcode to summon the council</p>", unsafe_allow_html=True)
    password = st.text_input("Passcode", type="password")
    if st.button("🔓 Enter"):
        if password == os.getenv("APP_PASSWORD"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid")
    st.stop()

# ===== INIT =====
if "current_session" not in st.session_state:
    st.session_state.current_session = council.create_session("New Quest", "Shogunate")
if "current_theme" not in st.session_state:
    st.session_state.current_theme = "Shogunate"
if "code_artifact" not in st.session_state:
    st.session_state.code_artifact = "# Awaiting wisdom..."

# ===== THEME CSS =====
theme = council.THEMES[st.session_state.current_theme]

st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {theme['bg']} 0%, {theme['accent']} 100%);
        color: {theme['text']};
    }}
    .stButton>button {{
        background-color: {theme['primary']};
        color: {theme['text']};
        border: 2px solid {theme['secondary']};
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        background-color: {theme['secondary']};
        transform: scale(1.05);
        box-shadow: 0 0 20px {theme['primary']};
    }}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: rgba(0,0,0,0.5);
        color: {theme['text']};
        border: 1px solid {theme['secondary']};
    }}
    h1, h2, h3 {{
        color: {theme['primary']};
        text-shadow: 2px 2px 4px {theme['accent']};
    }}
    @media (max-width: 768px) {{
        .stButton>button {{width: 100%;}}
    }}
</style>
""", unsafe_allow_html=True)

# Neon Tokyo extras
if st.session_state.current_theme == "Neon Tokyo":
    st.markdown("""
    <style>
        .stApp {{
            background-image: 
                radial-gradient(circle at 10% 10%, rgba(255,154,217,0.08) 0 2px, transparent 3px),
                radial-gradient(circle at 80% 30%, rgba(255,77,166,0.06) 0 3px, transparent 4px),
                radial-gradient(circle at 50% 70%, rgba(255,102,178,0.05) 0 4px, transparent 5px);
        }}
        @keyframes float {{
            0%, 100% {{transform: translateY(0);}}
            50% {{transform: translateY(-10px);}}
        }}
        h1 {{animation: float 3s ease-in-out infinite;}}
    </style>
    """, unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.title(f"{theme['personas']['Architect']['avatar']} LM SHOGUNATE")
    
    new_theme = st.selectbox(
        "🎨 Era",
        ["Shogunate", "Bandit Camp", "Neon Tokyo"],
        index=["Shogunate", "Bandit Camp", "Neon Tokyo"].index(st.session_state.current_theme)
    )
    if new_theme != st.session_state.current_theme:
        st.session_state.current_theme = new_theme
        st.rerun()
    
    st.divider()
    
    if st.button("➕ New Quest", use_container_width=True):
        st.session_state.current_session = council.create_session("New Quest", st.session_state.current_theme)
        st.session_state.code_artifact = "# Awaiting wisdom..."
        st.rerun()
    
    st.divider()
    st.caption("📜 History")
    
    sessions = council.get_sessions()
    for sess in sessions[:10]:
        if st.button(f"{sess['theme'][:3]} | {sess['title'][:20]}...", key=sess['id'], use_container_width=True):
            st.session_state.current_session = sess['id']
            st.session_state.current_theme = sess['theme']
            st.rerun()
    
    st.divider()
    st.caption(f"🔐 {st.session_state.current_theme}")

# ===== MAIN =====
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader(f"{theme['personas']['Architect']['avatar']} Council Chamber")
    
    # File upload
    uploaded = st.file_uploader("📎 Attach File", type=['pdf', 'txt', 'py', 'js'])
    
    # History
    history = council.get_history(st.session_state.current_session)
    for msg in history:
        with st.chat_message(msg["role"], avatar=msg.get("agent_name", "User")[:2]):
            if msg.get("agent_name"):
                st.markdown(f"**{msg['agent_name']}**")
            st.markdown(msg["content"])
            if "```" in msg["content"]:
                try:
                    block = msg["content"].split("```")[1]
                    if block.startswith("python"):
                        block = block[6:]
                    st.session_state.code_artifact = block.strip()
                except:
                    pass
    
    # Input
    user_input = st.chat_input("Command the council...")
    
    if user_input:
        # Handle file
        if uploaded:
            if uploaded.type == "application/pdf":
                reader = PdfReader(uploaded)
                file_text = "\n".join([p.extract_text() for p in reader.pages])
            else:
                file_text = uploaded.read().decode()
            user_input += f"\n\n[FILE: {uploaded.name}]\n{file_text[:5000]}"
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.status("⚙️ Council deliberates...", expanded=True) as status:
            for agent, content, msg_type in council.run_council(st.session_state.current_theme, user_input, st.session_state.current_session):
                if msg_type == "system":
                    st.write(f"🔔 {content}")
                else:
                    with st.chat_message("assistant", avatar=agent[:2]):
                        st.markdown(f"**{agent}**")
                        st.markdown(content)
                    if "```" in content:
                        try:
                            block = content.split("```")[1]
                            if block.startswith("python"):
                                block = block[6:]
                            st.session_state.code_artifact = block.strip()
                        except:
                            pass
            status.update(label="✅ Council has spoken", state="complete")
        st.rerun()

with col2:
    st.subheader("📜 Artifacts")
    st.code(st.session_state.code_artifact, language="python", line_numbers=True)
    st.download_button("💾 Download", st.session_state.code_artifact, "council_solution.py", "text/x-python")
