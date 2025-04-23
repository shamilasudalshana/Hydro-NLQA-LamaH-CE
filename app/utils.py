import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load env variables (for OpenAI key)
load_dotenv()

open_ai_api_key = os.getenv("OPENAI_API_KEY")
open_ai_model = "gpt-4o"  # default model
llm = ChatOpenAI(model=open_ai_model, temperature=0, api_key=open_ai_api_key)

def format_results(results):
    """Formats SPARQL results into a readable text."""
    if 'boolean' in results:
        return "Yes" if results['boolean'] else "No"

    answer_list = []
    for item in results.get('results', {}).get('bindings', []):
        values = [v['value'] for v in item.values()]
        answer_list.append(" - ".join(values))

    return "\n".join(answer_list)

def clean_sparql_query(sparql_query, named_graph):
    """Fixes common SPARQL syntax issues before execution."""

    if "SELECT ?s ?p ?o WHERE {" in sparql_query:
        sparql_query = sparql_query.replace("SELECT ?s ?p ?o WHERE {", "").rstrip("}")

    if "SELECT (COUNT(?sensor) AS ?sensorCount)" in sparql_query:
        sparql_query = sparql_query.replace(
            "SELECT (COUNT(?sensor) AS ?sensorCount)", "SELECT (COUNT(*) AS ?count)"
        )

    if "sosa:Sensor" in sparql_query and "PREFIX sosa:" not in sparql_query:
        sparql_query = f"PREFIX sosa: <http://www.w3.org/ns/sosa/>\n{sparql_query}"

    if f"GRAPH <{named_graph}>" not in sparql_query:
        sparql_query = sparql_query.replace("WHERE {", f"WHERE {{ GRAPH <{named_graph}> {{") + " } }"

    sparql_query = sparql_query.replace("```sparql", "").replace("```", "").strip()

    open_braces = sparql_query.count("{")
    close_braces = sparql_query.count("}")

    if open_braces > close_braces:
        sparql_query += "}" * (open_braces - close_braces)
    elif close_braces > open_braces:
        sparql_query = sparql_query.rstrip("}")

    sparql_query = sparql_query.replace("WHERE { {", "WHERE {").replace("} } }", "} }")

    return sparql_query.strip()

def generate_explanation(question, answer):
    """Generates a natural language explanation using LLM."""
    prompt = f"""
    You are an expert in SPARQL and semantic web queries.
    Given the following question and its SPARQL-derived answer, explain the answer in simple, natural language.

    Question: {question}
    Answer: {answer}

    Explanation:
    """
    response = llm.invoke(prompt)
    return response.content.strip()
