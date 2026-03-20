import streamlit as st
from groq import Groq
import pandas as pd
import plotly.graph_objects as go
import json

# Initialize Groq Client from Secrets
# Note: Ensure PRAGYANAI_GROQ_API_KEY is defined in your secrets.toml
client_4 = Groq(api_key=st.secrets["PRAGYANAI_GROQ_API_KEY"])

st.set_page_config(page_title="PragyanAI Curriculum Delta & Comparison", layout="wide")

st.header("⚖️ Curriculum Comparison & Delta Mapping")
st.markdown("Identify unique strengths, core commonalities, and the gap to industry alignment across different institutions.")

# --- DATA CHECK ---
if 'master_curriculum' not in st.session_state or len(st.session_state.master_curriculum) < 1:
    st.warning("Please upload at least one syllabus in '1_Extraction' to compare.")
    st.stop()

# --- AGENTIC DELTA LOGIC ---
def get_delta_analysis(doc_a_name, doc_b_name):
    """
    Performs a deep-dive delta analysis between two specific curricula 
    using the Agentic JSON state.
    """
    data_a = st.session_state.master_curriculum[doc_a_name]
    data_b = st.session_state.master_curriculum[doc_b_name]
    
    # Access the agent initialized in utils.py
    if 'agent' not in st.session_state:
        st.error("Agent not initialized. Please go to the home page or extraction page first.")
        return "Error: Agent missing."
    
    agent = st.session_state.agent
    
    # We use a helper to make the data JSON serializable (handling DataFrames if present)
    def serialize_data(data):
        serializable = {}
        for k, v in data.items():
            if isinstance(v, pd.DataFrame):
                serializable[k] = v.to_dict(orient='records')
            else:
                serializable[k] = v
        return json.dumps(serializable)

    comparison_prompt = f"""
    Analyze the Delta between these two curricula:
    
    CURRICULUM A ({doc_a_name}): {serialize_data(data_a)}
    CURRICULUM B ({doc_b_name}): {serialize_data(data_b)}
    
    Tasks:
    1. Identify 'Unique Nodes': Concepts in A not in B, and vice versa.
    2. Identify 'Depth Gaps': Which one covers topics more practically? (Look for Lab vs Theory markers).
    3. Generate a 'Migration Path': If a student moves from A to B, what bridge concepts must they learn?
    """
    
    response = agent.client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": comparison_prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content

# --- GENERAL COMPARATIVE ANALYSIS LOGIC ---
def generate_comparison_matrix(doc_list):
    """Uses LLM to find Common, Unique, and Industry-Gap topics for multiple docs."""
    context_data = ""
    for doc in doc_list:
        concepts = st.session_state.get(f"expanded_{doc}", pd.DataFrame())
        concept_list = concepts['Concepts'].tolist() if not concepts.empty else ["Data not expanded"]
        context_data += f"\nCOLLEGE/DOC: {doc}\nCONCEPTS: {', '.join(concept_list)}\n"

    jd_context = st.session_state.get('industry_input', "General AI Industry Standards")

    prompt = f"""
    You are a Senior Academic Auditor. Compare the following curricula and the Industry JD.
    
    DATA:
    {context_data}
    
    INDUSTRY REQUIREMENTS:
    {jd_context}
    
    TASK:
    1. Identify the 'CORE SYLLABUS': Topics present in ALL selected colleges.
    2. Identify 'UNIQUE MAPPING': For each college, what specific topics do they teach that others DON'T?
    3. Calculate 'INDUSTRY DELTA': What % of the Industry JD is covered by these combined? What is missing?
    
    Return the response in structured Markdown with clear headers.
    """
    
    response = client_4.chat.completions.create(
        model="llama3-70b-8192", # Updated from prompt-guard to a reasoning model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# --- SELECTION ---
all_docs = list(st.session_state.master_curriculum.keys())
selected_docs = st.multiselect("Select Syllabi to Compare", all_docs, default=all_docs[:2])

if len(selected_docs) < 1:
    st.info("Select at least one document to see the analysis.")
    st.stop()

# --- UI LAYOUT ---
tab1, tab2, tab3 = st.tabs(["📊 Comparison Dashboard", "🎯 Multi-Doc Analysis", "⚖️ Two-Doc Delta Deep-Dive"])

with tab1:
    st.subheader("Curriculum Overlap & Coverage")
    categories = ['Foundations', 'Math/Logic', 'Modern AI (LLMs)', 'Practical Labs', 'Ethics']
    fig = go.Figure()
    for doc in selected_docs:
        # Dummy data for radar chart - derive from 'expanded_df' in production
        fig.add_trace(go.Scatterpolar(
            r=[80, 70, 40, 60, 50], 
            theta=categories,
            fill='toself',
            name=doc
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Curriculum Balance Radar"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    if st.button("Generate Multi-Doc Report"):
        with st.spinner("Analyzing differences..."):
            report = generate_comparison_matrix(selected_docs)
            st.markdown(report)
            st.download_button("Download Report", report, file_name="Multi_Doc_Comparison.md")

with tab3:
    st.subheader("Deep-Dive Delta (A vs B)")
    if len(selected_docs) != 2:
        st.info("Please select exactly two documents in the multiselect above to use this feature.")
    else:
        doc_a, doc_b = selected_docs[0], selected_docs[1]
        if st.button(f"Analyze Delta: {doc_a} vs {doc_b}"):
            with st.spinner("Agentic Delta Logic in progress..."):
                delta_report = get_delta_analysis(doc_a, doc_b)
                st.markdown(delta_report)
                st.download_button("Download Delta Analysis", delta_report, file_name=f"Delta_{doc_a}_vs_{doc_b}.md")

# --- THE "UNIQUE" TABLE ---
st.divider()
st.subheader("Unique Concept Breakdown")
cols = st.columns(len(selected_docs))

for i, doc in enumerate(selected_docs):
    with cols[i]:
        st.info(f"**{doc}**")
        if f"expanded_{doc}" in st.session_state:
            df = st.session_state[f"expanded_{doc}"]
            st.write("Primary Focus Areas:")
            st.dataframe(df[df['Weight'] >= 20][['Topic', 'Concepts']], hide_index=True)
        else:
            st.write("Please expand syllabus on Page 2 first.")
            
