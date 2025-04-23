from fastapi import FastAPI
from pydantic import BaseModel
from SPARQLWrapper import SPARQLWrapper, JSON
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()
SPARQL_ENDPOINT = os.getenv("SPARQL_ENDPOINT", "https://sparql.knowledgehub.test.n4e.geo.tu-dresden.de/")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sparql_api")

# Initialize FastAPI app
app = FastAPI()

class SPARQLQuery(BaseModel):
    query: str

@app.post("/run_sparql/")
async def run_sparql(sparql_query: SPARQLQuery):
    """Execute a SPARQL query and return results."""
    try:
        sparql = SPARQLWrapper(SPARQL_ENDPOINT)
        sparql.setQuery(sparql_query.query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results
    except Exception as e:
        logger.error("SPARQL query failed", exc_info=True)
        return {"error": str(e)}
