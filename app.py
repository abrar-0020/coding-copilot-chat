import streamlit as st
import google.generativeai as genai

# 🔹 Configure Gemini API
API_KEY = "AIzaSyAG9aiAXuZ7ULYe3KeaMLvKXVrGyj3ji5A"
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-1.5-flash"

# ── Query Gemini ──
def query_gemini(prompt: str) -> str:
    """Send only the current prompt to Gemini (no chat history)."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini API Error: {e}"

# ── Streamlit UI ──
st.set_page_config(page_title="Coding Copilot (Gemini)", page_icon="🤖")

# ── Sidebar ──
st.sidebar.title("⚙️ Options")
if st.sidebar.button("🆕 New Chat"):
    st.session_state.clear()

# ── Session State ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_explained" not in st.session_state:
    st.session_state.file_explained = False

# ── Display previous chat messages ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── File Upload (Explain Only Once) ──
uploaded_file = st.file_uploader("Upload Python file", type="py", label_visibility="collapsed")

if uploaded_file and not st.session_state.file_explained:
    code = uploaded_file.read().decode("utf-8", errors="ignore")

    # Show uploaded code
    with st.chat_message("user"):
        st.markdown("📄 **Uploaded Python file:**")
        st.code(code, language="python")
    st.session_state.messages.append({"role": "user", "content": f"📄 Uploaded Python file:\n```python\n{code}\n```"})

    # Query Gemini only once for explanation
    with st.spinner("💭 Analyzing uploaded code..."):
        explanation = query_gemini(f"Explain this Python code in detail:\n```python\n{code}\n```")

    # Show explanation
    st.session_state.messages.append({"role": "assistant", "content": explanation})
    with st.chat_message("assistant"):
        st.markdown(explanation)

    # ✅ Mark file as explained
    st.session_state.file_explained = True

# ── Chat Input (Each Prompt → Single Response) ──
user_input = st.chat_input("Ask something about your code...")

if user_input:
    # Show user message in chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ✅ Send only current prompt to Gemini (no history)
    with st.spinner("💭 Thinking..."):
        reply = query_gemini(user_input)

    # Show Gemini response
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
