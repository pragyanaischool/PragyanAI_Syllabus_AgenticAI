import streamlit as st
from groq import Groq
import pandas as pd

# Initialize Groq Client from Secrets
client = Groq(api_key=st.secrets["PRAGYANAI_GROQ_API_KEY"])

st.set_page_config(page_title="Industry Interview Prep", layout="wide")

st.header("🎯 Industry Interview Intelligence")
st.markdown("Generate high-frequency interview questions based on your specific curriculum modules.")

# --- DATA CHECK ---
if 'master_curriculum' not in st.session_state or not st.session_state.master_curriculum:
    st.warning("Please process a syllabus in '1_Extraction' first.")
    st.stop()

# --- SIDEBAR: INTERVIEW FILTERS ---
with st.sidebar:
    st.subheader("Candidate Persona")
    target_role = st.selectbox("Target Role", 
                               ["AI Engineer", "ML Researcher", "Data Scientist", "Full Stack AI Developer"])
    
    difficulty = st.select_slider("Complexity Level", 
                                  options=["Intern", "Junior", "Mid-Level", "Senior"])
    
    num_questions = st.number_input("Questions per Module", min_value=1, max_value=10, value=3)

# --- CONTEXT SELECTION ---
doc_names = list(st.session_state.master_curriculum.keys())
selected_doc = st.selectbox("Select Syllabus Source", doc_names)

# --- GENERATION LOGIC ---
def generate_interview_bank(syllabus_df, role, level, count):
    # Flatten the syllabus into a list of topics/concepts
    topics = syllabus_df[['Module', 'Topic', 'Concepts']].to_dict('records')
    
    prompt = f"""
    You are a Technical Hiring Manager at a top-tier AI company (like Google or OpenAI).
    Based on the following syllabus modules, generate a professional interview question bank.
    
    TARGET ROLE: {role}
    EXPERIENCE LEVEL: {level}
    QUESTIONS PER MODULE: {count}
    
    SYLLABUS DATA:
    {topics}
    
    FOR EACH MODULE, PROVIDE:
    1. 'Conceptual Question': Testing the core theory.
    2. 'Scenario-Based Question': A real-world engineering problem related to the module.
    3. 'Ideal Answer': A concise, high-scoring technical response.
    4. 'Key Terminology': Buzzwords the candidate should mention.
    
    Format the output in a clean, expandable Markdown structure.
    """
    
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6 # Moderate creativity for varied questions
    )
    return response.choices[0].message.content

# --- UI DISPLAY ---
if f"expanded_{selected_doc}" in st.session_state:
    syllabus_df = st.session_state[f"expanded_{selected_doc}"]
    
    if st.button(f"Generate Interview Bank for {selected_doc}"):
        with st.spinner(f"Simulating {target_role} Interview..."):
            interview_content = generate_interview_bank(syllabus_df, target_role, difficulty, num_questions)
            
            st.divider()
            st.markdown(interview_content)
            
            # Allow user to download for offline prep
            st.download_button(
                label="Download Interview Guide (PDF/MD)",
                data=interview_content,
                file_name=f"{selected_doc}_Interview_Prep.md",
                mime="text/markdown"
            )
else:
    st.info("Please expand the syllabus on Page 2 to generate module-specific questions.")

# --- MOCK INTERVIEW COMPONENT ---
st.divider()
st.subheader("🤖 Quick Mock Drill")
with st.expander("Click to start a 1-question rapid fire"):
    if st.button("Get Random Question"):
        # Select a random concept from the session state
        if f"expanded_{selected_doc}" in st.session_state:
            all_concepts = st.session_state[f"expanded_{selected_doc}"]['Concepts'].str.split(',').explode().unique()
            import random
            random_concept = random.choice(all_concepts).strip()
            
            st.write(f"**Interviewer:** 'Explain the importance of **{random_concept}** in modern {target_role} workflows.'")
            st.text_area("Your Answer (Mental or Typed):", placeholder="Start typing here...")
