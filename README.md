# BIRD benchmark schema alignment

## Descrizione
Questo progetto si concentra sull'allineamento tra domande in linguaggio naturale e tabelle di database SQL, verificando la capacità di un LLM di individuare correttamente le tabelle pertinenti. L'analisi viene condotta confrontando le predizioni del modello con le tabelle reali estratte dalle query SQL. L'obiettivo è stato risolvere l'assignment assegnato [**Assignment.pdf**]. Per maggiori informazioni consultare il file [**report_on_the_work_done.pdf**]

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
1. Creare una cartella advanced:
    ```bash
   mkdir Documents/advanced
   cd Documents/advanced
2. Clonare la repository:
   ```bash
   git clone https://github.com/DanieleFerneti/bird_schema_alignment.git
   cd bird_schema_alignment
3. Prima di iniziare, assicurati che la seguente struttura di cartelle sia presente nel percorso appropriato:
   ```bash
   ls
  ```
  Documents/advanced/bird_schema_alignment/
  ├── mini_dev/
  ├── scripts/
  └── results/
  ```
  Queste tre cartelle sono necessarie per il corretto funzionamento del progetto.  

## Utilizzo
1. Posizionarsi nella cartella **bird_schema_alignment/**:

       cd ~/Documents/advanced/bird_schema_alignment

2. Crea l'**ambiente virtuale**:

       python3 -m venv venv

3. Attivare l'ambiente virtuale su **Linux/macOS**

       source venv/bin/activate
   
   Attivare l'ambiente virtuale su **Windows**
   
       .\venv\Scripts\activate

   Quando l'ambiente virtuale è attivato, il nome dell'ambiente (di solito venv) apparirà all'inizio della riga del terminale :
   ```bash
   (venv) ~/Documents/advanced/bird_schema_alignment$

6. Con l'ambiente virtuale attivato, **installa le librerie necessarie** con il comando:

       pip install -r requirements.txt
       
5.Posizionarsi nella cartella **scripts/**:

       cd scripts/

6. Estrarre le tabelle reali con espressioni regolari e predire le tabelle con il LLM:
   
       python3 ask_tables.py
   
7. Calcolare le metriche di valutazione:
   
       python3 metrics.py
   
## Risultati
Le tabelle estratte dalle **query SQL** sono salvate in:

    results/tables_extracted/output_sql.json

Le predizioni dell'**LLM** sono salvate in:

    results/tables_extracted/output_llm.json

Le metriche di valutazione globali **(Precision, Recall, F1-score)** sono disponibili in:

    results/metrics/evaluation_results.json

La metrica di valutazione **(F1-score)** per ogni **singolo db** è disponibili in:

    results/metrics/f1_per_db.json

Il confronto tra metriche calcolate manualmente e quelle dell'LLM è in:

    results/metrics/llm_evaluation_results.json

Un grafico delle F1-score per database è salvato in:

    results/metrics/f1_final_comparison.png

## Autore
- Daniele Ferneti
