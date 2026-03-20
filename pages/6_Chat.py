import streamlit as st
from groq import Groq
import pandas as pd

# Initialize Groq Client
client = Groq(api_key=st.secrets["PRAGYANAI_GROQ_API_KEY"])

st.set_page_config(page_title="PragyanAI AI Curriculum Analyst", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #f0f2f6; }
    .status-box { padding: 10px; border-radius: 5px; background-color: #f8f9fa; border-left: 5px solid #ff4b4b; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.header("🧠 Advanced Curriculum Intelligence Bot")

# --- DATA AVAILABILITY CHECK ---
if 'master_curriculum' not in st.session_state or not st.session_state.master_curriculum:
    st.warning("⚠️ No data found. Please upload a syllabus in '1_Extraction' first.")
    st.stop()

# --- SIDEBAR: MULTI-DOC CONTEXT & MODE ---
with st.sidebar:
    st.title("Settings")
    
    # Enable multi-document comparison mode
    selected_docs = st.multiselect(
        "Select Contextual Documents", 
        options=list(st.session_state.master_curriculum.keys()),
        default=list(st.session_state.master_curriculum.keys())[:1],
        help="Select multiple documents to ask comparison questions."
    )
    
    analysis_mode = st.radio(
        "Analysis Lens", 
        ["Academic Flow", "Industry Alignment", "Exam Prep"],
        help="Adjusts how the AI prioritizes its reasoning."
    )
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# --- CONTEXT AGGREGATOR (The 'RAG' Part) ---
def get_enhanced_context(doc_list):
    context_str = ""
    for doc in doc_list:
        context_str += f"\n=== DOCUMENT: {doc} ===\n"
        
        # 1. Add Structured Table Data (from Page 2)
        expanded_key = f"expanded_{doc}"
        if expanded_key in st.session_state:
            df = st.session_state[expanded_key]
            context_str += "MODULE STRUCTURE & WEIGHTS:\n" + df.to_markdown(index=False) + "\n"
        
        # 2. Add Industry Gap Data (from Page 3)
        gap_key = f"gap_analysis_{selected_docs[0]}" # Linking to first doc for gap context
        if gap_key in st.session_state:
            context_str += "INDUSTRY GAP ANALYSIS:\n" + st.session_state[gap_key] + "\n"
            
        # 3. Add Raw Metadata
        context_str += f"METADATA: {st.session_state.master_curriculum[doc].get('metadata', 'N/A')}\n"
        
    return context_str

context_data = get_enhanced_context(selected_docs)

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about prerequisites, topic depth, or industry relevance..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving Cross-Document Context..."):
            
            # Complex Prompting for specific curriculum questions
            system_prompt = f"""
            You are a 'Senior Curriculum Architect'. Answer queries using the provided multi-document context.
            
            CONTEXT:
            {context_data}
            
            USER SELECTED MODE: {analysis_mode}
            
            SPECIFIC TASKS:
            1. COMPARISON: If multiple documents are selected, identify specific topic 'Deltas'.
            2. FLOW OF STUDY: Identify prerequisites. (e.g., 'You must master Module 2 Logic before Module 5 NLP').
            3. CONCEPT MAPPING: Pinpoint exactly which Module and Course a concept belongs to.
            4. INDUSTRY: If in Industry mode, highlight skills missing from the syllabus based on the Gap Analysis.
            
            FORMATTING: Use bold headers, bullet points for lists, and Markdown tables for comparisons.
            """
            
            try:
                chat_completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                    temperature=0.4 # Lower temperature for factual curriculum data
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error calling Groq API: {e}")

# --- ENHANCED FOOTER TOOLS ---
if selected_docs:
    st.divider()
    with st.expander("🎓 Quick Analysis Tools"):
        c1, c2, c3 = st.columns(3)
        if c1.button("Analyze Study Flow"):
            st.info("Ask: 'What is the logical order to study these modules?'")
        if c2.button("Compare Unique Topics"):
            st.info("Ask: 'What does Document A have that Document B doesn't?'")
        if c3.button("Identify Exam Heaviness"):
            st.info("Ask: 'Which concepts have the highest weightage for marks?'")
