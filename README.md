# 🤖 ConvoQuest – Generative AI Web Application

ConvoQuest is a professional 3-in-1 interactive AI platform built using Python and Streamlit, powered by the Google Gemini API. 
This application bridges the gap between conversational AI, automated education, and real-time skill evaluation.

# 🚀 Project Overview

This project demonstrates advanced integration of Large Language Models (LLMs) with modern web frameworks, focusing on structured data and multi-turn reasoning.

# 💬 AI Chatbot
A conversational assistant powered by the Google Gemini API. It handles general queries with a focus on natural language understanding and now features a persistent sidebar for session-wide context.

# 🧠 Quiz Master
An automated assessment engine that generates 20-question MCQ quizzes on any user-specified topic.

Data Integrity: Employs JSON Schema enforcement to ensure 100% reliable parsing of AI responses.

Evaluation: Features an automated grading system with instant feedback on correct and incorrect answers.

# 🥊 AI Shadow Boxer (Scenario Simulator)
An innovative "Roleplay Arena" designed for skill-building through high-stakes simulations (e.g., Salary Negotiations or Interviews).

Interactive Challenge: The AI is programmed with a "Tough Opponent" persona to challenge user arguments.

Performance Scorecard: Generates a data-driven report evaluating Logic, Tone, and Persuasion via a comprehensive multi-turn transcript analysis.

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


You will find the dashboard organized into three functional modules:

💬 Chatbot: General AI assistance.

🧠 Quiz Master: Topic-based 20-question assessments.

🥊 Shadow Boxer: Simulation and performance scoring.

# 🧠 Technologies Used

Python – Core programming language

Streamlit – Web framework for interactive UI

Google Gemini API – LLM for chatbot and quiz generation

JSON – Structured data exchange and validation

Session State Management – Persistent chat and quiz history
