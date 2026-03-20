import streamlit as st

st.header("Syllabus Delta & Industry Alignment")

if st.session_state.master_curriculum:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Core Syllabus (Intersection)")
        st.write("Topics common across all uploaded colleges.")
        
    with col2:
        st.subheader("Unique Syllabus (Difference)")
        st.write("Unique strengths of each specific college.")

    st.divider()
    st.subheader("Industry Delta (The Gap)")
    # Logic: Compare Master Syllabus vs Industry Input (from Page 3)
    # Highlight what is missing (e.g., MLOps, LLM Deployment)
