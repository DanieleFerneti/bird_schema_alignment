# BIRD benchmark schema alignment

## Description
This project focuses on the alignment between natural language questions and SQL database tables, verifying the ability of an LLM to correctly identify the relevant tables. The analysis is conducted by comparing the model's predictions with the actual tables extracted from SQL queries. The objective was to complete the assigned task [**Assignment.pdf**]. For more details, refer to the file [**report_on_the_work_done.pdf**].

## General info
- **Model**: Used the free Groq API with the LLaMA 3-70B-8192 model.

## Dataset
The dataset used is **BIRD-benchmark (Mini-Dev)**, which contains 500 pairs of SQL queries and natural language questions.[here](https://github.com/bird-bench/mini_dev)

## Project structure
- **scripts/**: Contains the main scripts for table extraction and metric calculation.
  - `ask_tables.py`: Extracts the actual tables from SQL queries and uses an LLM to predict the relevant tables based on natural language questions.
  - `metrics.py`: Computes evaluation metrics (Precision, Recall, F1-score) by comparing the actual tables with the predicted ones.
- **results/**: 
  - **tables_extracted/**: Contains JSON files with the tables extracted from SQL and those predicted by the LLM.
        -ciao 
  - **metrics/**: Contains JSON files with evaluation metric results and generated charts.
  - 
## Installation
1. Create a folder called **advanced**:
    ```bash
   mkdir Documents/advanced
   cd Documents/advanced
2. Clone the repository:
   ```bash
   git clone https://github.com/DanieleFerneti/bird_schema_alignment.git
   cd bird_schema_alignment
3. Before starting, ensure the following folder structure is present in the correct path:
   ```bash
   ls
  ```
  Documents/advanced/bird_schema_alignment/
  ├── mini_dev/
  ├── scripts/
  └── results/
  ```
  These three folders are necessary for the project to function correctly. 
  
## Before Usage
1. If you do not have an API key for Groq, please consult  [here][https://console.groq.com/keys] to create it.
2. When it has been created, please execute the following command in your terminal:

     export GROQ_API_KEY=<your-api-key-here>

3. Now, you are ready for the usage !!

## Usage
1. Navigate to the **bird_schema_alignment/** folder:

       cd ~/Documents/advanced/bird_schema_alignment

2. Create the **virtual environment**:

       python3 -m venv venv

3. Activate the virtual environment on **Linux/macOS**:

       source venv/bin/activate
   
   Activate the virtual environment on **Windows**:
   
       .\venv\Scripts\activate

   When the virtual environment is activated, its name (usually venv) will appear at the beginning of the terminal line:
   ```bash
   (venv) ~/Documents/advanced/bird_schema_alignment$

4. With the virtual environment activated, **install the required libraries** with the command:

       pip install -r requirements.txt
       
5.Navigate to the **scripts/** folder:

       cd scripts/

6. Extract the actual tables using regular expressions and predict the tables with the LLM:
   
       python3 ask_tables.py
   
7. Compute the evaluation metrics:
   
       python3 metrics.py
   
## Results
The tables extracted from **SQL queries** are saved in:

    results/tables_extracted/output_sql.json
    
The **LLM** predictions are saved in:

    results/tables_extracted/output_llm.json

The global evaluation metrics **(Precision, Recall, F1-score)** are available in:

    results/metrics/evaluation_results.json

The **(F1-score)** evaluation metric for each **individual database** is available in

    results/metrics/f1_per_db.json

The comparison between manually computed metrics and those from the LLM is in:

    results/metrics/llm_evaluation_results.json

A chart of F1-scores per database is saved in:

    results/metrics/f1_final_comparison.png

## Author
- Daniele Ferneti
