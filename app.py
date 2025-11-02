import streamlit as st
import google.generativeai as genai
import json # For parsing the quiz JSON

# --- Configuration ---

# Set page configuration
st.set_page_config(
    page_title="Gemini Multi-Tool",
    page_icon="🤖",
    layout="wide",
)

# --- Gemini API Setup ---

# Load API key from Streamlit secrets
try:
    # This line might fail if secrets.toml is misconfigured
    api_key = st.secrets["GEMINI_API_KEY"]
    if not api_key:
        st.error("GEMINI_API_KEY is empty. Please add it to your Streamlit secrets.", icon="🚨")
        st.stop()
    genai.configure(api_key=api_key)
except KeyError:
    # This catches if GEMINI_API_KEY doesn't exist at all
    st.error("GEMINI_API_KEY not found. Please create .streamlit/secrets.toml and add it.", icon="🚨")
    st.stop()
except Exception as e:
    # Catch any other potential errors during setup
    st.error(f"Error during API configuration: {e}", icon="🚨")
    st.stop()

# Define the model to use (Gemini 1.5 Flash is fast and capable)
MODEL = "gemini-2.5-pro"
model = genai.GenerativeModel(MODEL)

# Define the JSON schema for the quiz
# This tells the model exactly what format to return
# --- THIS SECTION IS FIXED ---
quiz_schema = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "question": {"type": "STRING"},
            "options": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
                # Removed 'minItems' and 'maxItems' which caused the error.
                # We will rely on the prompt to request 4 options.
            },
            "correct_answer": {"type": "STRING"}
        },
        "required": ["question", "options", "correct_answer"]
    }
}
# --- END OF FIX ---

# Generation config for forcing JSON output
json_generation_config = genai.GenerationConfig(
    response_mime_type="application/json",
    response_schema=quiz_schema
)

# --- Helper Functions ---

# --- THIS FUNCTION IS UPDATED ---
def get_gemini_response(prompt, chat_history=None, force_json=False):
    """
    Gets a response from the Gemini model.

    Args:
        prompt (str): The user's prompt.
        chat_history (list, optional): The chat history.
        force_json (bool): Whether to force JSON output.

    Returns:
        str: The model's response text.
    """
    try:
        # Start a chat session if history is provided
        if chat_history is not None:
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(prompt)
        else:
            # Otherwise, just generate content
            config = json_generation_config if force_json else None
            response = model.generate_content(prompt, generation_config=config)
        
        return response.text
    except Exception as e:
        # Print the full error to the terminal for debugging
        print(f"--- ERROR CALLING GEMINI API ---")
        print(f"Error: {e}")
        print(f"Prompt: {prompt}")
        print(f"JSON Mode: {force_json}")
        print(f"---------------------------------")
        
        # Show a user-friendly error in the Streamlit app
        st.error(f"An error occurred with the Gemini API. Details: {e}")
        return None
# --- END OF UPDATE ---

def clean_json_response(raw_text):
    """
    Cleans the raw text response to extract only the JSON part.
    Sometimes the model might add markdown backticks.
    """
    try:
        # Find the first '[' and the last ']'
        start = raw_text.find('[')
        end = raw_text.rfind(']')
        if start != -1 and end != -1:
            json_str = raw_text[start:end+1]
            return json.loads(json_str)
    except json.JSONDecodeError:
        st.error("Failed to parse the quiz data from the model. The model's response was not valid JSON.")
        print(f"--- JSON PARSE FAILED --- \nRaw text: {raw_text}\n-------------------------")
    except Exception as e:
        st.error(f"An unexpected error occurred while parsing JSON: {e}")
    
    return None

# --- Session State Initialization ---

# 1. Chatbot History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 2. Quiz Questions
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

# 3. User's answers for the quiz
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# 4. Quiz score
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = None

# --- Main Application UI ---

st.title("🤖 Gemini Multi-Tool Chatbot")
st.caption("A unique chatbot with a Q&A, Quiz Generator, and History section.")

# Create the three main tabs
tab1, tab2, tab3 = st.tabs(["💬 Chatbot", "🧠 Quiz Time", "📚 Chat History"])

# --- Tab 1: Chatbot ---
with tab1:
    st.header("Standard Chatbot")
    st.write("Ask me anything! I will try my best to answer.")

    # Display existing chat messages
    for message in st.session_state.chat_history:
        role = "assistant" if message["role"] == "model" else "user"
        with st.chat_message(role):
            st.markdown(message["parts"][0])

    # Chat input box at the bottom
    user_prompt = st.chat_input("What's on your mind?")

    if user_prompt:
        # Add user's message to UI and history
        st.chat_message("user").markdown(user_prompt)
        st.session_state.chat_history.append({"role": "user", "parts": [user_prompt]})

        # Get the chatbot's response
        with st.spinner("Thinking..."):
            response_text = get_gemini_response(user_prompt, st.session_state.chat_history)
        
        if response_text:
            # Add chatbot's response to UI and history
            st.chat_message("assistant").markdown(response_text)
            st.session_state.chat_history.append({"role": "model", "parts": [response_text]})
            st.rerun() # Rerun to update the UI immediately
        else:
            # Error is already shown by get_gemini_response
            pass

# --- Tab 2: Quiz Generator ---
with tab2:
    st.header("🧠 Quiz Time")
    st.write("Enter a topic, and I'll generate a 20-question quiz for you.")

    # Input for the quiz topic
    topic = st.text_input("Enter a topic for your quiz:", placeholder="e.g., 'The Solar System' or 'World War II'")

    if st.button("Generate Quiz"):
        if topic:
            # Clear any old quiz data
            st.session_state.quiz_questions = []
            st.session_state.user_answers = {}
            st.session_state.quiz_score = None

            with st.spinner(f"Generating a 20-question quiz on '{topic}'... This might take a moment."):
                # Create a very specific prompt for the model
                quiz_prompt = f"""
                Generate a 20-question multiple-choice quiz on the topic: '{topic}'.
                You MUST return the quiz as a valid JSON array of objects.
                Each object must have "question", "options" (an array of 4 strings), and "correct_answer".
                You must follow this exact schema:
                [
                    {{
                        "question": "The question text",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "The text of the correct option"
                    }}
                ]
                Do not include any text, notes, or markdown backticks outside of the main JSON array.
                The "options" array MUST contain exactly 4 string items.
                """
                
                raw_response = get_gemini_response(quiz_prompt, force_json=True)
                
                if raw_response:
                    st.session_state.quiz_questions = clean_json_response(raw_response)
                    
                    if not st.session_state.quiz_questions:
                        st.error("The model did not return valid quiz data. Please try a different topic or try again.")
        else:
            st.warning("Please enter a topic first.")

    # --- Display the Quiz ---
    if st.session_state.quiz_questions:
        st.subheader(f"Quiz on: {topic if topic else 'your topic'}")
        st.write("Answer all questions and click 'Submit' at the bottom.")
        
        # Use a form to collect all answers before submitting
        with st.form(key="quiz_form"):
            user_answers = {}
            for i, q in enumerate(st.session_state.quiz_questions):
                # Check if question format is valid
                if 'question' not in q or 'options' not in q or not isinstance(q['options'], list):
                    st.error(f"Skipping malformed question {i+1}. Data: {q}")
                    continue

                st.markdown(f"**Question {i+1}: {q['question']}**")
                user_answers[i] = st.radio(
                    "Select one:",
                    q['options'], # This should now be a valid list
                    key=f"q_{i}",
                    label_visibility="collapsed"
                )
                st.markdown("---") # Separator

            submit_button = st.form_submit_button(label="Submit Answers")

            if submit_button:
                # Store answers and calculate score
                st.session_state.user_answers = user_answers
                score = 0
                for i, q in enumerate(st.session_state.quiz_questions):
                    # Safety check
                    if i in st.session_state.user_answers and 'correct_answer' in q:
                        if st.session_state.user_answers[i] == q['correct_answer']:
                            score += 1
                st.session_state.quiz_score = score
                st.rerun() # Rerun to show the score

    # --- Display the Score ---
    if st.session_state.quiz_score is not None:
        st.header(f"Your Score: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}")
        
        # Show a detailed breakdown
        st.subheader("Your Answers:")
        for i, q in enumerate(st.session_state.quiz_questions):
            # Safety checks for displaying results
            if i not in st.session_state.user_answers or 'correct_answer' not in q or 'question' not in q:
                continue

            user_ans = st.session_state.user_answers[i]
            correct_ans = q['correct_answer']
            
            if user_ans == correct_ans:
                st.success(f"**Q{i+1}: {q['question']}**")
                st.write(f"Your answer: {user_ans} (Correct!)")
            else:
                st.error(f"**Q{i+1}: {q['question']}**")
                st.write(f"Your answer: {user_ans}")
                st.write(f"Correct answer: {correct_ans}")
            st.markdown("---")

        if st.button("Take Another Quiz?"):
            # Clear all quiz state to start over
            st.session_state.quiz_questions = []
            st.session_state.user_answers = {}
            st.session_state.quiz_score = None
            st.rerun()

# --- Tab 3: Chat History ---
with tab3:
    st.header("📚 Your Chat History")
    st.write("Here is a log of your conversation from the 'Chatbot' tab.")

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")
        st.rerun()

    if not st.session_state.chat_history:
        st.info("Your chat history is empty. Start a conversation in the 'Chatbot' tab!")
    else:
        # Display history just like in the chat tab (read-only)
        for message in st.session_state.chat_history:
            role = "assistant" if message["role"] == "model" else "user"
            with st.chat_message(role):
                st.markdown(message["parts"][0])

