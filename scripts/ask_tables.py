import re
import json
import requests
import time
from typing import List
from pathlib import Path

HOME_DIR = Path.home()
PATH = HOME_DIR / "Documents/advanced/bird_schema_alignment"
# Global variable for the file path
#PATH = "/home/daniele/Documents/advanced/bird_schema_alignment"

def extract_tables(sql_query: str) -> List[str]:
    """
    Extracts table names from a SQL query.
    
    Args:
        sql_query: The SQL query to analyze
        
    Returns:
        A list of unique table names
    """
    # Regex to find tables after FROM or JOIN clauses
    table_pattern = re.compile(r'\b(?:FROM|JOIN)\s+([`"\[]?[\w\.]+[`"\]]?)', re.IGNORECASE)
    # Extract all matches from the query
    tables = table_pattern.findall(sql_query)
    # Clean table names by removing delimiters
    clean_tables = [table.strip('`"[]') for table in tables]
    return list(set(clean_tables))  # Remove duplicates

def query_llm(question: str, allowed_entities : List[List[str]]) -> List[str]:
    """
    Queries the LLM to get entities involved in a natural language query.
    
    Args:
        question: The natural language question
        allowed_entities: List of lists of entities to consider
        
    Returns:
        List of entities identified by the LLM
    """
    # Flatten the list of lists of entities into a single list
    allowed_entities_flat = [item for sublist in allowed_entities for item in sublist]

    # Remove duplicates from entities
    allowed_entities_flat = list(set(allowed_entities_flat))

    # Convert the list to a comma-separated string of entities
    allowed_entities_str = ", ".join(allowed_entities_flat)
    
    # API call configuration for Groq
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    # Prepare the prompt for the LLM
    data = {
        "model": "llama3-70b-8192",
        "messages": [{
            "role": "user",
            "content": (f"Return only a list of entities present in the query without explanations or additional text. "
                        "Example: if the query is 'What is the ratio of customers who pay in EUR against customers who pay in CZK?', "
                        "return ['customers']. "
                        f"The entities you can return must be among these: {allowed_entities_str}. "
                        f"Here's the query: {question}")
        }]
    }

    # Send the request to the API
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        # Extract and clean the entities from the response
        entities = result["choices"][0]["message"]["content"].split(', ')
        clean_entities = [entity.strip("`""[]'") for entity in entities] 
        return list(set(clean_entities))  # Return unique entities
    else:
        # Return empty list if API call fails
        return []

def process_json_file(input_file: str, output_sql_file: str, output_final_file: str):
    """
    Processes a JSON file containing questions and SQL queries, extracting tables and entities.
    
    Args:
        input_file: Path to the input JSON file
        output_sql_file: Path to save SQL extraction results
        output_final_file: Path to save LLM entity extraction results
    """
    print("Loading JSON file...")
    # Load the input JSON data
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    sql_results = []
    final_results = []
    extracted_tables_global = []
    
    print("Extracting tables from SQL queries...")
    # First pass: extract tables from SQL queries
    for entry in data:  # Process all queries in the JSON file
        sql_query = entry.get("SQL", "")
        extracted_tables = extract_tables(sql_query)
        extracted_tables_global.append(extracted_tables)
        sql_results.append({
            "question_id": entry.get("question_id"),
            "db_id" : entry.get("db_id"),
            "query": sql_query,
            "tables_extracted": extracted_tables
        })
    # Save SQL extraction results
    with open(output_sql_file, "w", encoding="utf-8") as file:
        json.dump(sql_results, file, indent=4)
    
    print(f"File with extracted tables saved to {output_sql_file}")
    
    print("Querying the LLM for each question...")
    # Second pass: query LLM for entities in the questions
    for i, entry in enumerate(data):  # Process all questions in the JSON file
        # Rate limiting: pause every 30 requests
        if i > 0 and i % 30 == 0:
            print("Pausing for 60 seconds to respect rate limits...")
            time.sleep(60)
        
        question = entry.get("question", "")
        sql_query = entry.get("SQL", "")
        extracted_tables = extract_tables(sql_query)
        # Filter relevant tables to provide context for the LLM
        filtered_tables = [
            tables for tables in extracted_tables_global if any(table in tables for table in extracted_tables)
        ]
        # Query LLM to extract entities from the question
        extracted_entities = query_llm(question, filtered_tables)
        
        final_results.append({
            "question_id": entry.get("question_id"),
            "db_id": entry.get("db_id"),
            "question": question,
            "tables_extracted": extracted_entities
        })
    
    # Save LLM extraction results
    with open(output_final_file, "w", encoding="utf-8") as file:
        json.dump(final_results, file, indent=4)
    
    print(f"File with LLM responses saved to {output_final_file}")
    print("Process completed successfully!")

# Execute the process with hardcoded file paths
process_json_file(f"{PATH}/minidev/MINIDEV/mini_dev_mysql.json", f"{PATH}/results/tables_extracted/output_sql.json", f"{PATH}/results/tables_extracted/output_llm.json")
