import streamlit as st
import google.generativeai as genai
import pdfplumber
import mimetypes
from PIL import Image
import io

# 🔹 Configure Gemini API
API_KEY = "your_gemini_api_key_here"
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-1.5-flash"

# ── Query Gemini ──
def query_gemini_text(prompt: str) -> str:
    """Send text prompt to Gemini."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini API Error: {e}"

def query_gemini_image(image_bytes, prompt="Describe this image.") -> str:
    """Send an image with an optional prompt to Gemini."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        image = Image.open(io.BytesIO(image_bytes))
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"❌ Gemini Image Analysis Error: {e}"

# ── Extract Text from PDF ──
def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# ── Streamlit UI ──
st.set_page_config(page_title="AI File Analyzer (Gemini)", page_icon="🤖")

# ── Sidebar ──
st.sidebar.title("⚙️ Options")
if st.sidebar.button("🆕 New Chat"):
    st.session_state.clear()

# ── Session State ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── File Upload ──
uploaded_file = st.file_uploader("Upload any file (image, PDF, text, etc.)", type=None)

if uploaded_file and not st.session_state.file_processed:
    file_type, _ = mimetypes.guess_type(uploaded_file.name)
    file_bytes = uploaded_file.read()

    # ✅ Handle Images
    if file_type and file_type.startswith("image"):
        with st.chat_message("user"):
            st.markdown(f"📷 **Uploaded Image:** {uploaded_file.name}")
            st.image(file_bytes)

        st.session_state.messages.append({"role": "user", "content": f"📷 Uploaded Image: {uploaded_file.name}"})

        with st.spinner("💭 Analyzing image with Gemini..."):
            reply = query_gemini_image(file_bytes, "Explain this image in detail.")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ✅ Handle PDFs
    elif file_type == "application/pdf":
        text = extract_text_from_pdf(file_bytes)
        with st.chat_message("user"):
            st.markdown(f"📄 **Uploaded PDF:** {uploaded_file.name}")
            st.code(text[:1000] + "..." if len(text) > 1000 else text)
        st.session_state.messages.append({"role": "user", "content": f"📄 Uploaded PDF: {uploaded_file.name}"})

        with st.spinner("💭 Analyzing PDF with Gemini..."):
            reply = query_gemini_text(f"Explain this PDF content:\n{text[:4000]}")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ✅ Handle Text Files
    elif file_type and ("text" in file_type or file_type.endswith("json")):
        text = file_bytes.decode("utf-8", errors="ignore")
        with st.chat_message("user"):
            st.markdown(f"📄 **Uploaded File:** {uploaded_file.name}")
            st.code(text[:1000] + "..." if len(text) > 1000 else text)
        st.session_state.messages.append({"role": "user", "content": f"📄 Uploaded File: {uploaded_file.name}"})

        with st.spinner("💭 Analyzing file content with Gemini..."):
            reply = query_gemini_text(f"Explain this file content:\n{text[:4000]}")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ❌ Unsupported Files (video, audio, etc.)
    else:
        with st.chat_message("assistant"):
            st.warning("❌ This file type is not fully supported yet. Try uploading text, PDF, or images.")
        st.session_state.messages.append({"role": "assistant", "content": "❌ Unsupported file type."})

    st.session_state.file_processed = True

# ── Chat Input (Only Current Prompt → Response) ──
user_input = st.chat_input("Ask a question about your uploaded file or anything else...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("💭 Thinking..."):
        reply = query_gemini_text(user_input)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
