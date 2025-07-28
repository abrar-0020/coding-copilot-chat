import streamlit as st
import requests

# ── Local Ollama API Endpoint ──
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"  # change to "llama3" or other model you installed

# ── Query Ollama Locally ──
def query_ollama(prompt: str) -> str:
    try:
        payload = {"model": MODEL_NAME, "prompt": prompt}
        response = requests.post(OLLAMA_API, json=payload, stream=False)
        if response.status_code == 200:
            return response.json().get("response", "⚠️ No response from Ollama.")
        return f"❌ Error {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"❌ Cannot connect to Ollama: {e}"

# ── Streamlit UI ──
st.set_page_config(page_title="Local Coding Copilot", page_icon="🤖")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat Input at Bottom ──
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
        reply = query_ollama(file_prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# ── Process User Input ──
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.spinner("💭 Thinking..."):
        reply = query_ollama(user_input)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
