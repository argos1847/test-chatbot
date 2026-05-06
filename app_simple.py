import streamlit as st
from simple_chatbot import SimpleChatbot
import os

st.set_page_config(
    page_title="PhysicsGPT",
    page_icon="🔬"
)

# Load chatbot (cached)
@st.cache_resource
def load_bot():
    try:
        return SimpleChatbot()
    except Exception as e:
        st.error(f"Error loading chatbot: {e}")
        return None

# Initialize
if 'messages' not in st.session_state:
    st.session_state.messages = []

bot = load_bot()

if bot is None:
    st.error("⚠️ Failed to load papers. Make sure papers_database.json exists.")
    st.stop()

# Sidebar
with st.sidebar:
    st.title("🔬 PhysicsGPT")
    st.markdown("Ask questions about physics papers")
    
    if os.environ.get("GROQ_API_KEY"):
        st.success("✅ Ready")
    else:
        st.error("❌ Set GROQ_API_KEY")

# Main chat
st.title("Physics Papers Chat")

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📚 Sources"):
                for src in msg["sources"]:
                    st.markdown(f"- {src['filename']}")

# Chat input
if prompt := st.chat_input("Ask a question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            result = bot.query(prompt)
            st.markdown(result['answer'])
            
            if result['sources']:
                with st.expander("📚 Sources"):
                    for src in result['sources']:
                        st.markdown(f"- {src['filename']}")
        
        # Save
        st.session_state.messages.append({
            "role": "assistant",
            "content": result['answer'],
            "sources": result['sources']
        })