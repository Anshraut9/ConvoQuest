# 🤖 ConvoQuest – Generative AI Web Application

ConvoQuest is a 3-in-1 interactive AI web application built using Python and Streamlit, powered by the Google Gemini API.

It features a conversational AI chatbot, an on-demand quiz generator, and a persistent chat history log — all integrated within a single, user-friendly interface.

# 🚀 Project Overview

This project demonstrates the integration of Large Language Models (LLMs) with modern web frameworks.

ConvoQuest includes:

💬 AI Chatbot – A conversational assistant powered by Google Gemini API.

🧠 Quiz Generator – Automatically creates and evaluates 20-question quizzes on any user-specified topic.

📜 History Log – Maintains past chat and quiz sessions with the ability to view or clear them.

The app leverages Streamlit’s Session State for dynamic state management and JSON schema validation for reliable AI response parsing.

# 🗂 Repository

GitHub Repository:
👉 https://github.com/Anshraut9/ConvoQuest.git

Clone the repository to your local system:

$ git clone https://github.com/Anshraut9/ConvoQuest.git
$ cd ConvoQuest

# ⚙️ Setup Instructions
## 1. Create and Activate a Virtual Environment
```bash
$ python3 -m venv venv
$ Windows: venv\Scripts\activate
```

## 2. Install Required Dependencies
```bash
(venv) $ pip install -r requirements.txt
```


# 🔑 API Configuration (Google Gemini)

To use the Google Gemini API, you must configure your API key securely.

Steps:
Inside your project directory, create a folder named .streamlit
Inside it, create a file named secrets.toml
Paste your API key as shown below:

```bash
GEMINI_API_KEY = "your api key"
```

# 💻 Running the Application

Once dependencies and the API key are configured, start the Streamlit app:
```bash
(venv) $ streamlit run app.py
```
Then open your browser and visit:
👉 ---website(local host)---


You’ll see the ConvoQuest dashboard with three tabs:

💬 Chatbot

🧠 Quiz Generator

🕒 History

# 🧠 Technologies Used

Python – Core programming language

Streamlit – Web framework for interactive UI

Google Gemini API – LLM for chatbot and quiz generation

JSON – Structured data exchange and validation

Session State Management – Persistent chat and quiz history
