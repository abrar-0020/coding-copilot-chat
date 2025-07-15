# 🤖 CodeStitch – AI Coding Copilot by Abrar Pasha

**CodeStitch** is a modern, interactive coding assistant built with **Streamlit** and **Together.ai (Mistral-7B)**. Ask coding questions or upload `.py` files to get plain-English explanations, bug fixes, or improvements — all via a sleek chat interface.

---

**## 🚀 Features**

- 💬 Chat with an AI coding assistant (powered by Mistral-7B)
- 📂 Upload `.py` files to get full-code breakdowns
- 🧠 Maintains conversation within session (stateless across reloads)
- 🎓 Built for students, educators, and beginner-to-intermediate devs
- ⚡ Hosted online — no install required

---

**## 🌐 Try the Live App**

▶️ [https://codestitch.streamlit.app/](https://codestitch.streamlit.app/)

---

** 🛠 Tech Stack**

- Python 3.x
- Streamlit
- Together.ai API (Mistral-7B-Instruct)
- RESTful HTTP

---

**## 💻 How to Run Locally

# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the Streamlit app
streamlit run app.py

---

**📂 Files Included**

-> app.py – Full Streamlit app with chat + file upload logic
-> requirements.txt – Python packages needed to run
-> README.md – Project overview and usage

---

**🔐 API Key Setup**
For local or cloud deployment, avoid hardcoding API keys:

import os
API_KEY = os.getenv("TOGETHER_API_KEY")

**Set your API key securely via:**
.env file (locally with python-dotenv)
Secrets Manager in Streamlit Cloud

---

**🙋 Author**
Abrar Pasha
🧪 Internship Project @ Planto.ai
🗓️ 2025

---

**📌 Note**
This tool is designed for educational and productivity use — not for generating full applications or advanced debugging. For large-scale use, consider integrating with stronger hosting or GPT-based APIs.



