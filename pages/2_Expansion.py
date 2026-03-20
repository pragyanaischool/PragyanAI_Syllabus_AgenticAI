#This page serves three purposes:

#1. Granular Breakdown: Breaking Modules into Sub-topics and Key Concepts.

#2. Weightage Assignment: Assigning importance/marks to specific topics.

#3. Interactive Editing: Allowing the user to add "Industry-relevant" concepts that might be missing from the original PDF.

import streamlit as st
from groq import Groq
import pandas as pd

st.set_page_config(page_title="Syllabus Expansion & Editor", layout="wide")
st.header("🔍 Syllabus Expansion & Concept Editor")

# Initialize Groq Client
groq_key = ''
def get_groq_client():
    """
    Initializes the Groq client using Streamlit Secrets.
    """
    # Check if the key exists in secrets
    if "PRAGYANAI_GROQ_API_KEY" not in st.secrets:
        groq_key = st.sidebar.text_input("Groq API Key", type="password")
        #st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
        #st.stop()
    else:
        groq_key = st.secrets["PRAGYANAI_GROQ_API_KEY"]
    # Initialize client
    client = Groq(
        api_key=groq_key,
    )
    return client

# Usage in your app:
client = get_groq_client()

st.info("On this page, we break down the extracted syllabus into granular sub-topics and assign weights.")

# Check if data exists from Page 1
if 'master_curriculum' not in st.session_state or not st.session_state.master_curriculum:
    st.warning("No syllabus found. Please go to '1_Extraction' and upload a document first.")
    st.stop()

# Selection of which document to expand
doc_names = list(st.session_state.master_curriculum.keys())
selected_doc = st.selectbox("Select Syllabus to Expand", doc_names)

def expand_syllabus_logic(raw_content):
    """Uses LLM to create a structured table of topics, subtopics, and weights."""
    prompt = f"""
    Based on the following syllabus content, create a detailed expansion.
    Break it down into a structured list with:
    - Module Number
    - Main Topic
    - Sub-Topics (Comma separated)
    - Key Concepts (The core theories or algorithms)
    - Estimated Weightage (%) (Total should sum to 100)

    Syllabus Content:
    {raw_content}

    Return ONLY a valid JSON list of objects. Example:
    [
      {{"Module": 1, "Main Topic": "Search", "Sub-Topics": "State Space, Heuristics", "Key Concepts": "A* Algorithm, Hill Climbing", "Weight": 20}}
    ]
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" } # Using Llama 3 JSON mode
    )
    return response.choices[0].message.content

# State management for the editable table
if f"expanded_{selected_doc}" not in st.session_state:
    with st.spinner("Expanding syllabus into sub-topics..."):
        # Simulated LLM call or processing
        raw_data = st.session_state.master_curriculum[selected_doc]['data']
        # In a real app, you'd parse the JSON from expand_syllabus_logic(raw_data)
        # For this example, we initialize a default structure if the LLM isn't called yet
        initial_data = [
            {"Module": "1", "Topic": "AI Primitives", "Sub-Topics": "State Space, Search", "Concepts": "Heuristics, BFS/DFS", "Weight": 20},
            {"Module": "2", "Topic": "Knowledge Representation", "Sub-Topics": "Predicate Logic", "Concepts": "Resolution, Unification", "Weight": 20},
            {"Module": "3", "Topic": "Statistical Reasoning", "Sub-Topics": "Bayesian Networks", "Concepts": "Bayes Theorem, Fuzzy Logic", "Weight": 20},
            {"Module": "4", "Topic": "Learning", "Sub-Topics": "Inductive Learning", "Concepts": "Decision Trees, Neural Nets", "Weight": 20},
            {"Module": "5", "Topic": "NLP & Expert Systems", "Sub-Topics": "Syntactic Analysis", "Concepts": "Parsing, Shells", "Weight": 20},
        ]
        st.session_state[f"expanded_{selected_doc}"] = pd.DataFrame(initial_data)

# --- UI DISPLAY ---

st.subheader(f"Detailed Breakdown: {selected_doc}")

# Editable Data Frame
edited_df = st.data_editor(
    st.session_state[f"expanded_{selected_doc}"],
    num_rows="dynamic", # Allows adding/deleting rows (Concepts)
    use_container_width=True,
    column_config={
        "Weight": st.column_config.NumberColumn(
            "Weight (%)",
            help="Importance of this module in the curriculum",
            min_value=0,
            max_value=100,
            format="%d%%",
        )
    }
)

# Save changes to session state
if st.button("Save Changes & Update Master Syllabus"):
    st.session_state[f"expanded_{selected_doc}"] = edited_df
    st.success("Syllabus updated with new concepts and weights!")

# Visualizing the Weights
st.divider()
st.subheader("Curriculum Weightage Distribution")
st.bar_chart(edited_df, x="Topic", y="Weight")

# Practical Expansion Suggestion
with st.expander("💡 AI Suggestions to Enhance this Syllabus"):
    if st.button("Suggest Industry Add-ons"):
        current_topics = ", ".join(edited_df['Topic'].tolist())
        suggestion_prompt = f"Given these AI topics: {current_topics}, suggest 3 cutting-edge Industry sub-topics to add (e.g. LLMs, MLOps)."
        
        # Call Groq
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": suggestion_prompt}],
            model="llama3-8b-8192",
        )
        st.write(chat_completion.choices[0].message.content)
