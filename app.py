import streamlit as st
from rag_engine_simple import PhysicsChatbot
import os

# Page config
st.set_page_config(
    page_title="PhysicsGPT - Research Paper Chat",
    page_icon="🔬",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main {max-width: 800px; margin: 0 auto;}
    .stChatMessage {padding: 1rem; border-radius: 8px;}
    .source-box {
        background: #f0f2f6;
        padding: 8px 12px;
        border-radius: 4px;
        margin: 4px 0;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = PhysicsChatbot()

# Sidebar
with st.sidebar:
    st.title("🔬 PhysicsGPT")
    st.markdown("**Ask questions about physics research papers**")
    st.markdown("---")
    st.markdown(f"📊 Papers indexed: **1,247**")
    st.markdown(f"💬 Queries today: **{st.session_state.query_count}/10**")
    
    if st.session_state.query_count >= 10:
        st.warning("⚠️ Daily limit reached")
        st.markdown("[Upgrade for unlimited →](https://yoursite.com/pricing)")
    
    st.markdown("---")
    st.markdown("### Example questions")
    if st.button("What is quantum entanglement?"):
        st.session_state.example_query = "What is quantum entanglement?"
    if st.button("Explain the EPR paradox"):
        st.session_state.example_query = "Explain the EPR paradox"
    if st.button("How does QFT work?"):
        st.session_state.example_query = "How does quantum field theory work?"

# Main chat interface
st.title("Chat with Physics Papers")
st.caption("Ask questions and get answers from 1,247 research papers")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📚 View sources"):
                for source in message["sources"]:
                    st.markdown(
                        f'<div class="source-box">📄 <b>{source["title"]}</b><br/>'
                        f'<small>{source["authors"]} · arXiv:{source["paper_id"]}</small></div>',
                        unsafe_allow_html=True
                    )

# Handle example queries
if hasattr(st.session_state, 'example_query'):
    user_input = st.session_state.example_query
    delattr(st.session_state, 'example_query')
else:
    user_input = st.chat_input("Ask a question about physics...")

# Process user input
if user_input:
    # Check query limit (freemium gate)
    if st.session_state.query_count >= 10:
        st.error("You've reached your daily limit. [Upgrade to Pro](https://yoursite.com/pricing) for unlimited queries.")
        st.stop()
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Searching papers..."):
            result = st.session_state.chatbot.query(user_input)
            st.markdown(result['answer'])
            
            # Show sources
            with st.expander("📚 View sources"):
                for source in result['sources']:
                    st.markdown(
                        f'<div class="source-box">📄 <b>{source["title"]}</b><br/>'
                        f'<small>{source["authors"]} · arXiv:{source["paper_id"]}</small></div>',
                        unsafe_allow_html=True
                    )
    
    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": result['answer'],
        "sources": result['sources']
    })
    
    # Increment query count
    st.session_state.query_count += 1
    st.rerun()
