from execute_sparql import query_sparql
from utils import format_results, clean_sparql_query, generate_explanation

def generate_sparql(question, named_graph):
    """Uses OpenAI to generate a structured SPARQL query."""
    from langchain_openai import ChatOpenAI
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)

    prompt = f"""
    You are an expert in querying RDF datasets using SPARQL **for the Virtuoso triple store**.  
    Your task is to convert the following natural language question into a **correct**, **well-structured**, and **Virtuoso-compatible** SPARQL query.

    ### **Guidelines**
    1. **Use Correct Prefixes**  
       ```
       PREFIX sosa: <http://www.w3.org/ns/sosa/>
       PREFIX envthes: <http://vocabs.lter-europe.net/EnvThes/>
       PREFIX qudt: <https://qudt.org/schema/qudt/>
       PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
       PREFIX unit: <https://qudt.org/vocab/unit/>
       PREFIX schema: <https://schema.org/>
       PREFIX locn: <http://www.w3.org/ns/locn#>
       PREFIX geo: <http://www.opengis.net/ont/geosparql#>
       PREFIX n4e_hyd: <https://nfdi4earth.pages.rwth-aachen.de/knowledgehub/nfdi4earth-ontology/test_hyd#>
       ```

    2. **Follow Correct Data Structure**  
       - Observations are modeled using `sosa:Observation`.  
       - The observed property is linked using `sosa:observedProperty`.  
       - The result is linked using `sosa:hasResult` (not `sosa:result`).  
       - The numeric value of the result is stored in `qudt:numericValue`.  
       - The unit of measurement is stored in `qudt:unit`.  
       - The observation result time is associated with `sosa:resultTime`.  
       - Spatial data is stored using `geo:asWKT`.  

    3. **Query Formatting Rules**  
       - Ensure **balanced brackets**: double-check that every `{" has a corresponding "}`.  
       - **Use LIMIT** when the question asks for a specific number of results.  
       - **Use COUNT(*)** when the question asks for a count.  
       - **Use proper namespaces** (`envthes:`, `qudt:`) without errors.  
       - **For spatial queries, use Virtuoso-specific functions**:
         - `bif:st_x()`, `bif:st_y()`, `bif:st_z()` for extracting coordinates.  
         - `bif:st_distance()` for geodesic distance.  
         - `bif:st_intersects()` for spatial relationships.  

    4. **Examples for Reference (Few-Shot Learning)**  

    **Example 1: Location of a gauging station**  
    **Question:** "Where is the 'Schlehdorf' gauging station located?"  
    **SPARQL Query:**
    ```sparql
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX schema: <https://schema.org/>

    SELECT ?geomObj ?easting ?northing ?elevation
    WHERE {{
      GRAPH <{named_graph}> {{
        ?sensor schema:name "Schlehdorf" ;
                geo:hasGeometry ?geom .
        ?geom geo:asWKT ?geomObj.
        BIND (bif:st_x(?geomObj) AS ?easting)
        BIND (bif:st_y(?geomObj) AS ?northing)
        BIND (bif:st_z(?geomObj) AS ?elevation)
      }}
    }}
    ```

    **Example 2: Highest annual precipitation catchment**  
    **Question:** "Which catchment area recorded the highest annual precipitation in 2015?"  
    **SPARQL Query:**
    ```sparql
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    PREFIX envthes: <http://vocabs.lter-europe.net/EnvThes/>
    PREFIX qudt: <https://qudt.org/schema/qudt/>
    PREFIX schema: <https://schema.org/>

    SELECT ?catchment (SUM(?precipitation) AS ?totalAnnualPrecipitation) ?unit
    WHERE {{
      GRAPH <{named_graph}> {{
        ?observation a sosa:Observation ;
                     sosa:observedProperty envthes:30106 ;
                     sosa:madeBySensor ?sensor ;
                     sosa:resultTime ?resultTime ;
                     sosa:hasResult ?result.
        ?result qudt:numericValue ?precipitation;
                qudt:unit ?unit.
        ?sensor n4e_hyd:monitorsCatchment ?catchment.
        FILTER(YEAR(?resultTime) = 2015)
      }}
    }}
    GROUP BY ?catchment ?unit
    ORDER BY DESC(?totalAnnualPrecipitation)
    LIMIT 1
    ```

    **Example 3: Average flow rate calculation**  
    **Question:** "What is the average flow rate at a station?"  
    **SPARQL Query:**
    ```sparql
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    PREFIX envthes: <http://vocabs.lter-europe.net/EnvThes/> 
    PREFIX qudt: <https://qudt.org/schema/qudt/>

    SELECT (AVG(?flowRate) AS ?averageFlowRate) ?unit 
    WHERE {{
      GRAPH <{named_graph}> {{
        ?obs a sosa:Observation ;
             sosa:observedProperty envthes:21242 ;
             sosa:hasResult ?result .
        ?result qudt:numericValue ?flowRate;
                qudt:unit ?unit .
      }}
    }}
    ```
    
    5. **Convert the following natural language question into a well-structured SPARQL query.**  
       - Use the correct ontology classes and properties.  
       - Ensure proper formatting for Virtuoso.  
       - Check for **bracket balance** and **namespace correctness**.  
       
    ### **Input Question**  
    {question}

    ### **Output:**  
    Generate only the **SPARQL query** without any additional text.  
    **Ensure correct bracket placement to avoid syntax errors.**
    """
    response = llm.invoke(prompt)
    sparql_query = response.content.strip()

    if sparql_query.startswith("```"):
        sparql_query = sparql_query.replace("```sparql", "").replace("```", "").strip()

    return clean_sparql_query(sparql_query, named_graph)

def validate_sparql(sparql_query):
    """Validates the SPARQL query before execution."""
    if not sparql_query.strip():
        return False, "Error: The generated SPARQL query is empty."

    if sparql_query.count('{') != sparql_query.count('}'):
        return False, "Error: Mismatched braces in the SPARQL query."

    try:
        test_results = query_sparql(sparql_query)
        if 'results' not in test_results:
            return False, "Error: Query execution failed. Check the syntax."
    except Exception as e:
        return False, f"Error: Query validation failed - {str(e)}"

    return True, "Valid Query"

def ask_natural_language_question(question, named_graph):
    """Converts NL question to SPARQL, validates it, executes, and returns results with explanation."""
    sparql_query = generate_sparql(question, named_graph)
    is_valid, validation_message = validate_sparql(sparql_query)

    if not is_valid:
        return sparql_query, "Error: Invalid SPARQL Query.", validation_message

    results = query_sparql(sparql_query)
    formatted_answer = format_results(results)

    if not formatted_answer.strip():
        return sparql_query, "No results found for the query.", "No explanation available because no results were retrieved."

    verbalized_ans = generate_explanation(question, formatted_answer)
    return sparql_query, formatted_answer, verbalized_ans
