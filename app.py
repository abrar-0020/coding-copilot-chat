import streamlit as st
from openai import OpenAI

# 🔹 Set your API key
API_KEY = "sk-abcd1234efgh5678abcd1234efgh5678abcd1234"

# 🔹 Initialize OpenAI Client
client = OpenAI(api_key=API_KEY)

MODEL_NAME = "gpt-4o-mini"  # or "gpt-3.5-turbo"

# ── Query OpenAI API ──
def query_openai(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a coding assistant. Explain code simply."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ OpenAI API Error: {e}"

# ── Streamlit UI ──
st.set_page_config(page_title="Coding Copilot (OpenAI)", page_icon="🤖")

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
uploaded_file = st.file_uploader("", type="py", label_visibility="collapsed")
if uploaded_file:
    code = uploaded_file.read().decode("utf-8", errors="ignore")
    st.toast("✅ File uploaded. Generating explanation...")
    file_prompt = f"Explain this Python code:\n```python\n{code}\n```"
    st.session_state.messages.append({"role": "user", "content": "Uploaded a Python file"})
    with st.chat_message("user"):
        st.markdown("📄 Uploaded a Python file")
    with st.spinner("💭 Thinking..."):
        reply = query_openai(file_prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# ── Process User Input ──
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.spinner("💭 Thinking..."):
        reply = query_openai(user_input)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
