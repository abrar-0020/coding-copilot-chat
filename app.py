import streamlit as st
import google.generativeai as genai

# 🔹 Configure Gemini API Key
API_KEY = "AIzaSyAG9aiAXuZ7ULYe3KeaMLvKXVrGyj3ji5A"
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-1.5-flash"  # you can also use "gemini-1.5-pro"

# ── Query Gemini API ──
def query_gemini(prompt: str) -> str:
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
    st.session_state.messages = []

# ── Chat History ──
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat Input ──
user_input = st.chat_input("Ask something about your code...")

# ── File Upload (.py files) ──
uploaded_file = st.file_uploader("Upload Python file", type="py", label_visibility="collapsed")
if uploaded_file:
    code = uploaded_file.read().decode("utf-8", errors="ignore")
    st.toast("✅ File uploaded. Generating explanation...")
    file_prompt = f"Explain this Python code:\n```python\n{code}\n```"
    st.session_state.messages.append({"role": "user", "content": "📄 Uploaded a Python file"})
    with st.chat_message("user"):
        st.markdown("📄 Uploaded a Python file")
    with st.spinner("💭 Thinking..."):
        reply = query_gemini(file_prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# ── Process User Input ──
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.spinner("💭 Thinking..."):
        reply = query_gemini(user_input)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
