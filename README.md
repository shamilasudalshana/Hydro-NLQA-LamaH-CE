# LamaH-CE SPARQL Query Interface 🚀

A web-based interface that allows users to query hydrological knowledge graphs using SPARQL and natural language questions, powered by LLMs like OpenAI GPT.

## 🌍 Features
- Browse a list of pre-defined SPARQL queries by category.
- Execute and inspect raw SPARQL queries directly via UI.
- Ask questions in natural language and get SPARQL queries + results + verbalized answers.
- Backend based on FastAPI, frontend built with Streamlit.

---

## 📁 Project Structure
```
LamaH-CE-SPARQL-App/
│
├── app/                        # Backend & logic
│   ├── backend.py             # FastAPI app
│   ├── execute_sparql.py      # Query runner
│   ├── nl_query_handler.py    # Natural language → SPARQL logic
│   ├── prompt.py              # Prompt template (if used)
│   ├── qachain.py             # QA logic
│   ├── get_entities_relations.py # NER utility (optional)
│   ├── utils.py               # Shared functions
│
├── frontend/                  # Streamlit apps
│   ├── frontend.py            # Direct SPARQL interface
│   ├── frontend_nl_qa.py      # Natural Language Q&A interface
│   └── assets/                # Logos (PNG)
│
├── configs/                   # Question banks
│   ├── questions.yaml
│   └── questions_validation.yaml
│
├── .env.example               # Sample environment config
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── .gitignore
```

---

## ⚙️ Installation & Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/LamaH-CE-SPARQL-App.git
cd LamaH-CE-SPARQL-App
```

### 2. Set up the virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
```
Edit `.env` and add your OpenAI key:
```
OPENAI_API_KEY=your-api-key-here
```

---

## 🚀 Running the App

### Start Backend (FastAPI)
```bash
uvicorn app.backend:app --host 0.0.0.0 --port 8000 --reload
```

### Run Frontend (Choose one)
#### Direct SPARQL Query UI
```bash
streamlit run frontend/frontend.py
```

#### Natural Language + SPARQL Q&A UI
```bash
streamlit run frontend/frontend_nl_qa.py
```

---

## 💡 Example Questions (NL Q&A)
- "What are the coordinates of the gauging station 'Bangs'?"
- "Which year recorded the highest precipitation in the catchment monitored by sensor X?"
- "How many observations are there in the dataset?"

---

## 🤝 Acknowledgments
- Built using [Streamlit](https://streamlit.io/), [FastAPI](https://fastapi.tiangolo.com/), [LangChain](https://www.langchain.com/), and [OpenAI](https://platform.openai.com/).
- Part of the [LamaH-CE](https://www.ufz.de/index.php?en=48988) hydrological modeling framework and the [NFDI4Earth](https://www.nfdi4earth.de/) initiative.

---

## 🛡 License
MIT License
