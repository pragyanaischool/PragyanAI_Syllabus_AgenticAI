# PragyanAI_Syllabus_AgenticAI
# System Architecture
- Orchestration: LangChain (for RAG and structured extraction).

- Inference: Groq Llama-3-70b (for high-speed reasoning).

- Frontend: Streamlit (Multi-page navigation).

- Data Persistence: st.session_state (to keep data alive across pages).

Folder Structure
Plaintext
project/
├── main.py              # Entry point & Navigation
├── pages/
│   ├── 1_Extraction.py  # Syllabus Parser
│   ├── 2_Expansion.py   # Topic/Weight Breakdown
│   ├── 3_Industry.py    # JD & Gap Analysis
│   ├── 4_Compare.py     # Delta & Unique Mapping
│   ├── 5_Knowledge.py   # Graph Visualization
│   ├── 6_Chat.py        # GraphRAG / Bot
│   ├── 7_Interviews.py  # Questions & Concepts
│   ├── 8_Lab_Projects.py# Labs & Industry Projects
│   └── 9_Assessments.py # MCQs & Coding Tasks
└── utils.py             # Groq & PDF helpers
