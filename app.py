import os
from dotenv import load_dotenv

import streamlit as st
import requests

# ── App Configuration ──
st.set_page_config(page_title="Coding Copilot Chat", page_icon="🤖", layout="wide")
load_dotenv()
API_KEY = os.getenv("TOGETHER_API_KEY")
API_URL    = "https://api.together.xyz/v1/chat/completions"
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

SYSTEM_PROMPT = (
    "You are a helpful coding assistant. "
    "Answer questions about code, explain snippets, fix bugs, and suggest improvements."
)

# ── Helper: send message to model and show reply ──
def process_user_message(text: str) -> None:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(text)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":       MODEL_NAME,
        "messages":    st.session_state.messages,
        "temperature": 0.7,
        "max_tokens":  512,
    }
    with st.spinner("Copilot is thinking…"):
        r = requests.post(API_URL, headers=headers, json=payload)
        reply = (
            r.json()["choices"][0]["message"]["content"]
            if r.status_code == 200
            else f"❌ Error {r.status_code}: {r.text}"
        )

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(reply)

# ── Session State Initialization ──
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "last_file_name" not in st.session_state:
    st.session_state.last_file_name = None

# ── Sidebar: New Chat only (no history) ──
with st.sidebar:
    st.markdown("## 💬 Chat Menu")
    if st.button("🆕 New Chat"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.session_state.last_file_name = None
        st.success("Started a new chat!")
    st.markdown("---")

# ── Display current conversation ──
for m in st.session_state.messages[1:]:  # skip system prompt
    avatar = "🤖" if m["role"] == "assistant" else "🧑"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])

# ── Chat Input & File Upload ──
user_text = st.chat_input("Type your code question or paste code…")

uploaded_file = st.file_uploader("", type="py", label_visibility="collapsed")
if uploaded_file:
    if st.session_state.last_file_name != uploaded_file.name:
        code = uploaded_file.read().decode("utf-8", errors="ignore")
        st.toast("✅ File uploaded. Generating explanation…")
        prompt = f"Explain this Python code:\n```python\n{code}\n```"
        process_user_message(prompt)
        st.session_state.last_file_name = uploaded_file.name

if user_text:
    process_user_message(user_text)
