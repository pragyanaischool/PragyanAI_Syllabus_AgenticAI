import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="Curriculum Knowledge Map", layout="wide")

st.header("🕸️ Curriculum Knowledge Graph")
st.markdown("Visualize the hierarchical and lateral relationships between Modules, Topics, and Concepts.")

# --- DATA CHECK ---
if 'master_curriculum' not in st.session_state or not st.session_state.master_curriculum:
    st.warning("Please process a syllabus in '1_Extraction' first.")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Graph Settings")
physics_enabled = st.sidebar.checkbox("Enable Physics (Bouncy Graph)", value=True)
node_distance = st.sidebar.slider("Node Distance", 100, 500, 250)

doc_names = list(st.session_state.master_curriculum.keys())
selected_doc = st.selectbox("Select Syllabus to Visualize", doc_names)

# --- GRAPH GENERATION FUNCTION ---
def build_curriculum_graph(df, doc_name):
    # Initialize Pyvis Network
    net = Network(
        height="600px", 
        width="100%", 
        bgcolor="#ffffff", 
        font_color="#333333", 
        directed=True
    )
    
    # Root Node (The Course)
    course_node = doc_name
    net.add_node(course_node, label=course_node, color="#EB4034", size=30, title="Root Course")

    for idx, row in df.iterrows():
        module_id = f"Module {row['Module']}"
        module_label = f"M{row['Module']}: {row['Topic']}"
        
        # 1. Add Module Node
        net.add_node(module_id, label=module_label, color="#34A8EB", size=25, title=row['Topic'])
        net.add_edge(course_node, module_id, weight=2)

        # 2. Add Sub-Topics / Concepts
        # Concepts are stored as a string in our session state, let's split them
        concepts = [c.strip() for c in str(row['Concepts']).split(',')]
        
        for concept in concepts:
            if concept:
                net.add_node(concept, label=concept, color="#99EE99", size=15)
                net.add_edge(module_id, concept)
                
                # Logic for cross-module links (Optional/Advanced)
                # If a concept like 'Probability' appears in multiple places, 
                # Pyvis automatically connects them if the string name is identical.

    # Physics configuration
    if physics_enabled:
        net.repulsion(node_distance=node_distance, spring_length=200)
    else:
        net.toggle_physics(False)
        
    return net

# --- RENDER ---
if f"expanded_{selected_doc}" in st.session_state:
    df = st.session_state[f"expanded_{selected_doc}"]
    
    with st.spinner("Generating Knowledge Map..."):
        # Create the graph
        nt = build_curriculum_graph(df, selected_doc)
        
        # Save and Read HTML
        path = "html_files"
        if not os.path.exists(path):
            os.makedirs(path)
            
        file_path = f"{path}/graph_{selected_doc}.html"
        nt.save_graph(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        components.html(html_content, height=650)
        
    st.success("Graph Generated! Use your mouse to scroll/zoom and drag nodes.")
    
    # Analysis Summary
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Total Modules:** {len(df)}")
    with col2:
        total_concepts = sum([len(str(c).split(',')) for c in df['Concepts']])
        st.write(f"**Total Key Concepts:** {total_concepts}")

else:
    st.info("Expand the syllabus on Page 2 to generate the concept nodes.")
