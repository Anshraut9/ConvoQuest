import streamlit as st
import google.generativeai as genai
import json

# --- 1. Configuration & Page Setup ---
st.set_page_config(
    page_title="ConvoQuest - GenAI Multi-Tool",
    page_icon="🤖",
    layout="wide",
)

# --- 2. Gemini API Setup ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("GEMINI_API_KEY not found or misconfigured in Streamlit Secrets.")
    st.stop()

# Using Gemini 1.5 Flash for speed and reliability
MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# --- 3. Helper Functions ---

def get_gemini_response(prompt, chat_history=None, force_json=False):
    try:
        if chat_history is not None:
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(prompt)
        else:
            if force_json:
                response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            else:
                response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def generate_scorecard(transcript):
    eval_prompt = f"""
    Analyze the following professional roleplay transcript: {transcript}
    Provide a performance scorecard in EXACT JSON format:
    {{
      "scores": {{"Tone": 0, "Logic": 0, "Persuasion": 0}},
      "feedback": "Overall summary",
      "winning_moment": "The best part of user's strategy",
      "mistake": "What they should improve"
    }}
    Scores must be integers 1-10.
    """
    response = model.generate_content(eval_prompt, generation_config={"response_mime_type": "application/json"})
    return json.loads(response.text)

def clean_json_response(raw_text):
    try:
        start = raw_text.find('[')
        end = raw_text.rfind(']')
        if start != -1 and end != -1:
            return json.loads(raw_text[start:end+1])
    except:
        return None

# --- 4. Session State Initialization ---
state_keys = {
    "chat_history": [],
    "quiz_questions": [],
    "user_answers": {},
    "quiz_score": None,
    "simulation_history": []
}

for key, default in state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- 5. Sidebar: Unified History ---
with st.sidebar:
    st.title("📚 Session History")
    if st.button("🗑️ Clear All History"):
        st.session_state.chat_history = []
        st.session_state.simulation_history = []
        st.rerun()
    
    st.subheader("Recent Chat Log")
    for msg in st.session_state.chat_history[-5:]: # Show last 5
        role = "👤" if msg["role"] == "user" else "🤖"
        st.caption(f"{role}: {msg['parts'][0][:50]}...")

# --- 6. Main UI ---
st.title("🚀 ConvoQuest")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["💬 AI Chatbot", "🧠 Quiz Master", "🥊 Shadow Boxer"])

# --- Tab 1: Standard Chatbot ---
with tab1:
    st.header("General Assistant")
    for message in st.session_state.chat_history:
        role = "assistant" if message["role"] == "model" else "user"
        with st.chat_message(role):
            st.markdown(message["parts"][0])

    user_input = st.chat_input("Ask me anything...", key="chat_input")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.spinner("Typing..."):
            response = get_gemini_response(user_input, st.session_state.chat_history)
            if response:
                st.session_state.chat_history.append({"role": "model", "parts": [response]})
                st.rerun()

# --- Tab 2: Quiz Generator ---
with tab2:
    st.header("Quiz Generator")
    topic = st.text_input("Enter Topic (e.g. Python, History, Space):")
    
    if st.button("Generate 20-Question Quiz"):
        quiz_prompt = f"Generate a 20-question MCQ quiz on {topic} as a JSON array of objects with 'question', 'options' (list of 4), and 'correct_answer'."
        with st.spinner("Crafting questions..."):
            raw_quiz = get_gemini_response(quiz_prompt, force_json=True)
            st.session_state.quiz_questions = clean_json_response(raw_quiz)
            st.session_state.quiz_score = None

    if st.session_state.quiz_questions:
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                st.session_state.user_answers[i] = st.radio("Select:", q['options'], key=f"quiz_{i}")
            
            if st.form_submit_button("Submit Quiz"):
                score = sum(1 for i, q in enumerate(st.session_state.quiz_questions) if st.session_state.user_answers[i] == q['correct_answer'])
                st.session_state.quiz_score = score
                st.rerun()

    if st.session_state.quiz_score is not None:
        st.balloons()
        st.success(f"### Final Score: {st.session_state.quiz_score} / 20")

# --- Tab 3: AI Shadow Boxer ---
with tab3:
    st.header("🥊 AI Shadow Boxer")
    st.info("Practice high-stakes conversations with a tough AI opponent.")
    
    # Message Container
    sim_container = st.container(height=400)
    with sim_container:
        for msg in st.session_state.simulation_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    sim_input = st.chat_input("Make your argument...", key="sim_box")
    
    if sim_input:
        st.session_state.simulation_history.append({"role": "user", "content": sim_input})
        with st.spinner("Opponent is countering..."):
            system_instruction = "Act as a very skeptical and tough HR Manager in a salary negotiation. Be firm but professional. Don't give in easily."
            opponent_msg = get_gemini_response(f"{system_instruction} User says: {sim_input}")
            if opponent_msg:
                st.session_state.simulation_history.append({"role": "assistant", "content": opponent_msg})
                st.rerun()

    if st.button("🏁 End Session & Get Scorecard"):
        if st.session_state.simulation_history:
            with st.spinner("Analyzing performance..."):
                report = generate_scorecard(str(st.session_state.simulation_history))
                st.markdown("---")
                st.subheader("📊 Your Performance Scorecard")
                c1, c2, c3 = st.columns(3)
                c1.metric("Tone", f"{report['scores']['Tone']}/10")
                c2.metric("Logic", f"{report['scores']['Logic']}/10")
                c3.metric("Persuasion", f"{report['scores']['Persuasion']}/10")
                st.write(f"**Feedback:** {report['feedback']}")
                st.success(f"✅ **Winning Moment:** {report['winning_moment']}")
                st.error(f"❌ **Area to Improve:** {report['mistake']}")
        else:
            st.warning("Start a conversation first!")