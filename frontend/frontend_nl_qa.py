import streamlit as st
import requests
import pandas as pd
import yaml
import os
import sys
from dotenv import load_dotenv

# Add app/ folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
from nl_query_handler import ask_natural_language_question

# Load environment variables
load_dotenv()
API_URL = os.getenv("SPARQL_BACKEND_URL", "http://127.0.0.1:8000/run_sparql/")
NAMED_GRAPH = os.getenv("NAMED_GRAPH_URI", "http://hydroturtle/LamahCE")

st.set_page_config(page_title="LamaH-CE SPARQL Query Interface", page_icon="🌍", layout="wide")

# Load questions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(BASE_DIR, "../configs/questions_validation.yaml")

def load_questions():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

questions = load_questions()

# ---- Logos (Optional assets folder if needed) ----
# lamaH_logo = "assets/LamaH_CE_logo.png"
# nfdi4earth_logo = "assets/NFDI4Earth_logo.png"
# hydro_turtle_logo = "assets/Hydro_turtle_logo.png"


ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

lamaH_logo = os.path.join(ASSETS_DIR, "LamaH_CE_logo.png")
nfdi4earth_logo = os.path.join(ASSETS_DIR, "NFDI4Earth_logo.png")
hydro_turtle_logo = os.path.join(ASSETS_DIR, "Hydro_turtle_logo.png")


header_col1, header_col2 = st.columns([2, 3])
with header_col1:
    st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>LamaH-CE SPARQL Query Interface</h2>", unsafe_allow_html=True)
with header_col2:
    logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1])
    with logo_col1: st.image(lamaH_logo, width=70)
    with logo_col2: st.image(hydro_turtle_logo, width=80)
    with logo_col3: st.image(nfdi4earth_logo, width=100)

st.markdown("---")

# ---- Tabs for Modes ----
tab1, tab2 = st.tabs(["🔍 Direct SPARQL Queries", "🤖 Natural Language Q&A"])

# ---- Sidebar: Question selection ----
st.sidebar.header("📂 Select a Question Category")
selected_category = st.sidebar.selectbox("🗂️ Choose a Main Category:", list(questions.keys()))

selected_question = ""
sparql_query = ""

if selected_category:
    selected_subcategory = st.sidebar.selectbox(
        "📁 Choose a Subcategory:", list(questions[selected_category].keys()), key=f"{selected_category}_sub"
    )

    if selected_subcategory:
        selected_question = st.sidebar.selectbox(
            "❓ Choose a Question:",
            list(questions[selected_category][selected_subcategory].keys()),
            key=f"{selected_subcategory}_question"
        )
        sparql_query = questions[selected_category][selected_subcategory][selected_question]

# ---- TAB 1: Direct SPARQL ----
with tab1:
    query_col, result_col = st.columns([3, 2])
    with query_col:
        st.subheader("💡 Selected Question")
        st.markdown(f"**{selected_question}**")
        st.subheader("📝 SPARQL Query")
        query_text = st.text_area("Modify or review the query:", sparql_query, height=300)

    with result_col:
        st.subheader("📊 Query Results")

        def format_df(data):
            if "results" in data and "bindings" in data["results"]:
                rows, columns = [], set()
                for item in data["results"]["bindings"]:
                    row = {k: v["value"] for k, v in item.items()}
                    columns.update(row.keys())
                    rows.append(row)
                return pd.DataFrame(rows, columns=sorted(columns)) if rows else None
            return None

        if st.button("🚀 Run SPARQL Query"):
            if query_text.strip():
                with st.spinner("⏳ Running SPARQL query..."):
                    response = requests.post(API_URL, json={"query": query_text})
                    data = response.json()

                if "error" in data:
                    st.error(f"❌ Error: {data['error']}")
                else:
                    df = format_df(data)
                    if df is not None:
                        st.success("✅ Query executed successfully!")
                        st.dataframe(df)
                    else:
                        st.warning("⚠️ No results found.")
            else:
                st.warning("⚠️ Please enter a SPARQL query.")

# ---- TAB 2: Natural Language Q&A ----
with tab2:
    st.subheader("🤖 Ask a Question in Natural Language")
    st.markdown(f"**{selected_question}**")
    nl_question = st.text_area("🔍 Modify or Ask a New Question:", selected_question, height=100)

    if st.button("🤖 Generate SPARQL Query & Answer"):
        if nl_question.strip():
            with st.spinner("⏳ Processing..."):
                sparql_query_generated, generated_answer, verbalized_ans = ask_natural_language_question(
                    nl_question, NAMED_GRAPH
                )

            st.success("✅ Answer Generated!")
            st.text_area("📝 Generated SPARQL Query:", sparql_query_generated, height=450)
            st.text_area("📝 Generated Answer from SPARQL:", generated_answer, height=75)
            st.text_area("📖 Verbalized Answer:", verbalized_ans, height=200)
        else:
            st.warning("⚠️ Please enter a question.")
