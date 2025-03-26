import os
import re
import json
import time
from typing import List
from groq import Groq

# Global variable for the file path
PATH = "/home/daniele/Documents/advanced/bird_schema_alignment"

# Inizializza il client Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def extract_tables(sql_query: str) -> List[str]:
    """
    Extracts table names from a SQL query.
    
    Args:
        sql_query: The SQL query to analyze
        
    Returns:
        A list of unique table names
    """
    table_pattern = re.compile(r'\b(?:FROM|JOIN)\s+([`"\[]?[\w\.]+[`"\]]?)', re.IGNORECASE)
    tables = table_pattern.findall(sql_query)
    clean_tables = [table.strip('`"[]') for table in tables]
    return list(set(clean_tables))  # Remove duplicates

def query_llm(question: str, allowed_entities: List[List[str]]) -> List[str]:
    """
    Queries the LLM to get entities involved in a natural language query.
    
    Args:
        question: The natural language question
        allowed_entities: List of lists of entities to consider
        
    Returns:
        List of entities identified by the LLM
    """
    allowed_entities_flat = list(set([item for sublist in allowed_entities for item in sublist]))
    allowed_entities_str = ", ".join(allowed_entities_flat)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": (f"Return only a list of entities present in the query without explanations or additional text. "
                            "Example: if the query is 'What is the ratio of customers who pay in EUR against customers who pay in CZK?', "
                            "return ['customers']. "
                            f"The entities you can return must be among these: {allowed_entities_str}. "
                            f"Here's the query: {question}")
            }
        ],
        model="llama3-70b-8192",
    )

    entities = chat_completion.choices[0].message.content.split(', ')
    clean_entities = [entity.strip("`\"[]'") for entity in entities]
    return list(set(clean_entities))  # Remove duplicates

def process_json_file(input_file: str, output_sql_file: str, output_final_file: str):
    """
    Processes all entries from a JSON file containing questions and SQL queries,
    extracting tables and entities.

    Args:
        input_file: Path to the input JSON file
        output_sql_file: Path to save SQL extraction results
        output_final_file: Path to save LLM entity extraction results
    """
    print("Loading JSON file...")
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    sql_results = []
    final_results = []
    extracted_tables_global = []

    print("Extracting tables from SQL queries...")
    for entry in data:
        sql_query = entry.get("SQL", "")
        extracted_tables = extract_tables(sql_query)
        extracted_tables_global.append(extracted_tables)
        sql_results.append({
            "question_id": entry.get("question_id"),
            "db_id": entry.get("db_id"),
            "query": sql_query,
            "tables_extracted": extracted_tables
        })

    with open(output_sql_file, "w", encoding="utf-8") as file:
        json.dump(sql_results, file, indent=4)

    print(f"File with extracted tables saved to {output_sql_file}")

    print("Querying the LLM for each question...")
    for i, entry in enumerate(data):
        if i > 0 and i % 30 == 0:
            print("Pausing for 60 seconds to respect rate limits...")
            time.sleep(60)

        question = entry.get("question", "")
        sql_query = entry.get("SQL", "")
        extracted_tables = extract_tables(sql_query)

        filtered_tables = [
            tables for tables in extracted_tables_global if any(table in tables for table in extracted_tables)
        ]

        extracted_entities = query_llm(question, filtered_tables)

        final_results.append({
            "question_id": entry.get("question_id"),
            "db_id": entry.get("db_id"),
            "question": question,
            "tables_extracted": extracted_entities
        })

    with open(output_final_file, "w", encoding="utf-8") as file:
        json.dump(final_results, file, indent=4)

    print(f"File with LLM responses saved to {output_final_file}")
    print("Process completed successfully!")

# Execute the process on all queries
process_json_file(
    f"{PATH}/minidev/MINIDEV/mini_dev_mysql.json",
    f"{PATH}/results/tables_extracted/output_sql.json",
    f"{PATH}/results/tables_extracted/output_llm.json"
)
