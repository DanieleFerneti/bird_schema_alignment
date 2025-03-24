# BIRD benchmark schema alignment

## Descrizione
Questo progetto si concentra sull'allineamento tra domande in linguaggio naturale e tabelle di database SQL, verificando la capacità di un LLM di individuare correttamente le tabelle pertinenti. L'analisi viene condotta confrontando le predizioni del modello con le tabelle reali estratte dalle query SQL. L'obiettivo è stato risolvere l'assignment assegnato [**Assignment.pdf**]. Per maggiori informazioni consultare il file [...]

## General info
- **Modello**: Utilizzata l'API gratuita di Groq con il modello LLaMA 3-70B-8192.

## Dataset
Il dataset utilizzato è **BIRD-benchmark (Mini-Dev)**, che contiene 500 coppie di query SQL e domande in linguaggio naturale. [here](https://github.com/bird-bench/mini_dev)

## Struttura del progetto
- **scripts/**: Contiene gli script principali per l'estrazione delle tabelle e il calcolo delle metriche.
  - `ask_tables.py`: Estrae le tabelle reali dalle query SQL e utilizza un LLM per predire le tabelle pertinenti basandosi sulle domande in linguaggio naturale.
  - `metrics.py`: Calcola le metriche di valutazione (Precision, Recall, F1-score) confrontando le tabelle reali e quelle predette.
- **results/**:
  - **tables_extracted/**: Contiene i file JSON con le tabelle estratte da SQL e quelle predette dall'LLM.
  - **metrics/**: Contiene i file JSON con i risultati delle metriche di valutazione e i grafici generati.

## Installazione
1. mkdir /Documents/advanced
2. Clonare il repository nella cartella advanced:
   ```bash
   git clone https://github.com/DanieleFerneti/bird_schema_alignment.git
   cd bird_schema_alignment

## Utilizzo
1. Estrarre le tabelle reali con espressioni regolari e predire le tabelle con il LLM:
   
       python3 scripts/ask_tables.py
   
3. Calcolare le metriche di valutazione:
   
       python3 scripts/metrics.py
   

## Risultati
Le tabelle estratte dalle **query SQL** sono salvate in:

    results/tables_extracted/output_sql.json

Le predizioni dell'**LLM** sono salvate in:

    results/tables_extracted/output_llm.json

Le metriche di valutazione globali **(Precision, Recall, F1-score)** sono disponibili in:

    results/metrics/evaluation_results.json

Le metriche di valutazione **(Precision, Recall, F1-score)** per ogni **singolo db** sono disponibili in:

    results/metrics/f1_per_db.json

Il confronto tra metriche calcolate manualmente e quelle dell'LLM è in:

    results/metrics/llm_evaluation_results.json

Un grafico delle F1-score per database è salvato in:

    results/metrics/f1_final_comparison.png

## Autore
- Daniele Ferneti
