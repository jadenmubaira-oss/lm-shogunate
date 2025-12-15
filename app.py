import streamlit as st
import council
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="LM Shogunate",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== AUTHENTICATION =====
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🏯 LM SHOGUNATE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Enter the passcode to summon the council</p>", unsafe_allow_html=True)
    
    password = st.text_input("Passcode", type="password", key="login_pass")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔓 Enter", use_container_width=True):
            if password == os.getenv("APP_PASSWORD"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid passcode")
    st.stop()

# ===== INITIALIZE SESSION STATE =====
if "current_session" not in st.session_state:
    st.session_state.current_session = council.create_session("New Quest", "Shogunate")

if "current_theme" not in st.session_state:
    st.session_state.current_theme = "Shogunate"

if "code_artifact" not in st.session_state:
    st.session_state.code_artifact = "# Awaiting the council's wisdom..."

# ===== THEME INJECTION =====
theme_data = council.THEMES[st.session_state.current_theme]

st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {theme_data['bg']} 0%, {theme_data['accent']} 100%);
        color: {theme_data['text']};
    }}
    
    .stButton>button {{
        background-color: {theme_data['primary']};
        color: {theme_data['text']};
        border: 2px solid {theme_data['secondary']};
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }}
    
    .stButton>button:hover {{
        background-color: {theme_data['secondary']};
        transform: scale(1.05);
        box-shadow: 0 0 20px {theme_data['primary']};
    }}
    
    .stTextInput>div>div>input {{
        background-color: rgba(0,0,0,0.5);
        color: {theme_data['text']};
        border: 1px solid {theme_data['secondary']};
    }}
    
    .stTextArea>div>div>textarea {{
        background-color: rgba(0,0,0,0.5);
        color: {theme_data['text']};
        border: 1px solid {theme_data['secondary']};
    }}
    
    h1, h2, h3 {{
        color: {theme_data['primary']};
        text-shadow: 2px 2px 4px {theme_data['accent']};
    }}
    
    .chat-message {{
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid {theme_data['secondary']};
        background: rgba(0,0,0,0.3);
    }}
    
    /* Mobile Optimization */
    @media (max-width: 768px) {{
        .stButton>button {{
            width: 100%;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.title(f"{theme_data['personas']['Architect']['avatar']} LM SHOGUNATE")
    
    # Theme Selector
    new_theme = st.selectbox(
        "🎨 Select Era",
        ["Shogunate", "Bandit Camp", "Neon Tokyo"],
        index=["Shogunate", "Bandit Camp", "Neon Tokyo"].index(st.session_state.current_theme)
    )
    
    if new_theme != st.session_state.current_theme:
        st.session_state.current_theme = new_theme
        st.rerun()
    
    st.divider()
    
    # New Session
    if st.button("➕ New Quest", use_container_width=True):
        title = st.text_input("Quest Name", value="New Quest")
        if title:
            st.session_state.current_session = council.create_session(title, st.session_state.current_theme)
            st.session_state.code_artifact = "# Awaiting the council's wisdom..."
            st.rerun()
    
    st.divider()
    st.caption("📜 Previous Quests")
    
    # Session History
    sessions = council.get_sessions()
    for sess in sessions[:10]:  # Show last 10
        if st.button(
            f"{sess['theme'][:3]} | {sess['title'][:20]}...",
            key=sess['id'],
            use_container_width=True
        ):
            st.session_state.current_session = sess['id']
            st.session_state.current_theme = sess['theme']
            st.rerun()
    
    st.divider()
    st.caption(f"🔐 Logged in | Theme: {st.session_state.current_theme}")

# ===== MAIN LAYOUT =====
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader(f"{theme_data['personas']['Architect']['avatar']} Council Chamber")
    
    # Chat History
    history = council.get_history(st.session_state.current_session)
    
    for msg in history:
        with st.chat_message(msg["role"], avatar=msg.get("agent_name", "User")[:2]):
            if msg.get("agent_name"):
                st.markdown(f"**{msg['agent_name']}**")
            st.markdown(msg["content"])
            
            # Extract code blocks for artifact
            if "```" in msg["content"]:
                try:
                    code_block = msg["content"].split("```")[1]
                    if code_block.startswith("python"):
                        code_block = code_block[6:]
                    st.session_state.code_artifact = code_block.strip()
                except:
                    pass
    
    # User Input
    user_input = st.chat_input("Your command to the council...")
    
    if user_input:
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Run the council
        with st.status("⚙️ The council deliberates...", expanded=True) as status:
            for agent_name, content, msg_type in council.run_council(
                st.session_state.current_theme,
                user_input,
                st.session_state.current_session
            ):
                if msg_type == "system":
                    st.write(f"🔔 {content}")
                else:
                    with st.chat_message("assistant", avatar=agent_name[:2]):
                        st.markdown(f"**{agent_name}**")
                        st.markdown(content)
                    
                    # Update artifact if code is present
                    if "```" in content:
                        try:
                            code_block = content.split("```")[1]
                            if code_block.startswith("python"):
                                code_block = code_block[6:]
                            st.session_state.code_artifact = code_block.strip()
                        except:
                            pass
            
            status.update(label="✅ Council has spoken", state="complete")
        
        st.rerun()

with col2:
    st.subheader("📜 Artifacts")
    
    st.code(
        st.session_state.code_artifact,
        language="python",
        line_numbers=True
    )
    
    # Download button
    st.download_button(
        label="💾 Download Code",
        data=st.session_state.code_artifact,
        file_name="council_solution.py",
        mime="text/x-python"
    )
```

---

## **PHASE 6: DEPLOYMENT**

### Step 6.1: Create Requirements File
Create **`requirements.txt`**:
```
streamlit==1.31.0
litellm==1.30.0
python-dotenv==1.0.0
supabase==2.3.0
openai==1.12.0
tiktoken==0.6.0
tenacity==8.2.3
requests==2.31.0
beautifulsoup4==4.12.3
PyPDF2==3.0.1git push