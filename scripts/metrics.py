import json
import requests
import time
import matplotlib.pyplot as plt
from pathlib import Path


HOME_DIR = Path.home()
PATH = HOME_DIR / "Documents/advanced/bird_schema_alignment"
# Global variable for the file path
#PATH = "/home/daniele/Documents/advanced/bird_schema_alignment"

def load_json(file_path):
    """
    Loads and returns data from a JSON file.
    
    Args:
        file_path: Path to the JSON file to be loaded
        
    Returns:
        The loaded JSON data
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def calculate_metrics(real_values, predicted_values):
    """
    Calculates precision, recall, and F1 score metrics.
    
    Args:
        real_values: Ground truth values
        predicted_values: Model predictions
        
    Returns:
        Dictionary containing precision, recall, and F1 score
    """
    total_tp, total_fp, total_fn = calculate_tp_fp_fn(real_values, predicted_values)
    
    # Calculate precision, recall, and F1 score with zero-division handling
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }

def calculate_tp_fp_fn(real_values, predicted_values):
    """
    Calculates true positives, false positives, and false negatives.
    
    Args:
        real_values: List of lists with ground truth values
        predicted_values: List of lists with predicted values
        
    Returns:
        Tuple of (true positives, false positives, false negatives)
    """
    total_tp = 0
    total_fp = 0
    total_fn = 0

    for rv, pv in zip(real_values, predicted_values):
        # Set of ground truth values for current entry
        rv_set = set(rv) 
        # Set of all ground truth values from other entries
        other_rv_set = set().union(*[other_rv for other_rv in real_values if other_rv != rv]) 
        for predString in pv:
            if predString in rv_set:
                total_tp += 1  # Correctly predicted
            elif predString in other_rv_set:
                total_fn += 1  # Missed a correct prediction
            else:
                total_fp += 1  # Incorrectly predicted

    return total_tp, total_fp, total_fn

def call_groq_api_with_retry(prompt, max_retries=3, initial_wait=2):
    """
    Calls the Groq API with exponential backoff retry logic.
    
    Args:
        prompt: The text prompt to send to the API
        max_retries: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds before retrying
        
    Returns:
        API response JSON
        
    Raises:
        Exception: If all retry attempts fail
    """
    # API call configuration
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    }
    
    # Exponential backoff implementation
    wait_time = initial_wait
    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 429:
                print(f"Rate limit exceeded. Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
                continue
            response.raise_for_status()
        except Exception as e:
            print(f"Attempt {attempt+1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
            else:
                print("Maximum number of attempts reached")
                raise e
    raise Exception("All API call attempts failed")

def calculate_metrics_with_llm(real_values, predicted_values):
    """
    Uses an LLM to calculate evaluation metrics based on TP, FP, FN values.
    
    Args:
        real_values: Ground truth values
        predicted_values: Model predictions
        
    Returns:
        Dictionary containing metrics calculated by the LLM
    """
    # Calculate base values for metrics
    total_tp, total_fp, total_fn = calculate_tp_fp_fn(real_values, predicted_values)
    
    # Create prompt for the LLM
    prompt = f"""
    Given these aggregate numbers calculated on a complete dataset of {len(real_values)} records:
    - True Positives (TP): {total_tp}
    - False Positives (FP): {total_fp}
    - False Negatives (FN): {total_fn}
    
    Calculate precision, recall and F1 score
  
    Return ONLY a JSON object with the calculated numerical results:
    {{
        "precision": value,
        "recall": value,
        "f1_score": value
    }}
    """
    
    try:
        # Call the LLM API
        response_data = call_groq_api_with_retry(prompt)
        llm_response = response_data["choices"][0]["message"]["content"].strip()
        
        # Parse the JSON response, handling different formats
        if "```json" in llm_response:
            llm_response = llm_response.split("```json")[1].split("```")[0].strip()
        elif "```" in llm_response:
            llm_response = llm_response.split("```")[1].split("```")[0].strip()
        metrics_llm = json.loads(llm_response)
        return metrics_llm
    except Exception as e:
        # Fallback to manual calculation if LLM call fails
        print(f"Error calculating metrics with LLM: {e}")
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }

def calculate_metrics_per_db(ground_truth_grouped, predictions_grouped):
    """
    Calculates F1 scores for each database ID.
    
    Args:
        ground_truth_grouped: Ground truth values grouped by database ID
        predictions_grouped: Predictions grouped by database ID
        
    Returns:
        Dictionary mapping database IDs to their F1 scores
    """
    db_metrics = {}

    # Calculate metrics for each database ID
    for db_id, gt_tables in ground_truth_grouped.items():
        if db_id in predictions_grouped:
            predicted_tables = predictions_grouped[db_id]
            
            # Calculate metrics for each db_id
            total_tp, total_fp, total_fn = calculate_tp_fp_fn(gt_tables, predicted_tables)
            
            # Calculate F1 score for this database
            precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
            recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            db_metrics[db_id] = f1
    
    return db_metrics

def plot_f1_scores(db_metrics, output_file):
    """
    Creates a bar chart of F1 scores per database ID and saves it to a file.
    
    Args:
        db_metrics: Dictionary mapping database IDs to F1 scores
        output_file: Path where the plot image will be saved
    """
    # Extract data for plotting
    db_ids = list(db_metrics.keys())
    f1_scores = list(db_metrics.values())
    
    # Create the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(db_ids, f1_scores, color='skyblue')
    plt.xlabel('db_id')
    plt.ylabel('F1 Score')
    plt.title('F1 Score per db_id')
    plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(output_file)
    print(f"Plot saved as image in: {output_file}")
    plt.close()  # Close the figure after saving

def main():
    """
    Main function that orchestrates the evaluation process:
    1. Loads ground truth and prediction data
    2. Calculates metrics using both standard functions and LLM
    3. Compares results and generates per-database metrics
    4. Creates and saves visualizations
    """
    # Define file paths
    ground_truth_file = f"{PATH}/results/tables_extracted/output_sql.json"
    predictions_file = f"{PATH}/results/tables_extracted/output_llm.json"
    results_file = f"{PATH}/results/metrics/evaluation_results.json"
    llm_results_file = f"{PATH}/results/metrics/llm_evaluation_results.json"
    f1_per_db_file = f"{PATH}/results/metrics/f1_per_db.json"
    plot_image_file = f"{PATH}/results/metrics/f1_final_comparison.png"
    
    # Load the data files
    ground_truth = load_json(ground_truth_file)
    predictions = load_json(predictions_file)
    
    # Group extracted tables by database ID
    ground_truth_grouped = {}
    for entry in ground_truth:
        db_id = entry.get("db_id")
        # Create a new list for this db_id if it doesn't exist yet
        if db_id not in ground_truth_grouped:
            ground_truth_grouped[db_id] = []
        # Add tables to the appropriate db_id group if they exist
        if "tables_extracted" in entry:
            ground_truth_grouped[db_id].append(entry["tables_extracted"])

    # Similarly group prediction tables by database ID
    predictions_grouped = {}
    for entry in predictions:
        db_id = entry.get("db_id")
        # Create a new list for this db_id if it doesn't exist yet
        if db_id not in predictions_grouped:
            predictions_grouped[db_id] = []
        # Add predicted tables to the appropriate db_id group if they exist
        if "tables_extracted" in entry:
            predictions_grouped[db_id].append(entry["tables_extracted"])

    # Calculate global metrics across all database IDs
    # Extract tables from ground truth and predictions
    real_values = [d["tables_extracted"] for d in ground_truth if "tables_extracted" in d]
    predicted_values = [d["tables_extracted"] for d in predictions if "tables_extracted" in d]
    
    # Calculate metrics using the standard calculation function
    metrics = calculate_metrics(real_values, predicted_values)
    
    # Save standard calculation results to file
    with open(results_file, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)
    
    print(f"Results calculated by Python function saved to {results_file}")
    
    # Calculate metrics using the LLM approach
    metrics_llm = calculate_metrics_with_llm(real_values, predicted_values)
    
    # Save LLM calculation results to file
    with open(llm_results_file, "w", encoding="utf-8") as file:
        json.dump(metrics_llm, file, indent=4)
    
    print(f"LLM results saved to {llm_results_file}")
    
    # Print comparison of standard vs LLM metrics in a formatted table
    print("\nResults comparison:")
    print(f"{'Metric':<10} {'Calculated':<15} {'LLM':<15}")
    print("-" * 40)
    for metric in ["precision", "recall", "f1_score"]:
        if metric in metrics_llm:
            print(f"{metric:<10} {metrics[metric]:<15.4f} {metrics_llm[metric]:<15.4f}")
        else:
            print(f"{metric:<10} {metrics[metric]:<15.4f} {'N/A':<15}")
    
    # Calculate F1 score for each individual database ID
    db_metrics = calculate_metrics_per_db(ground_truth_grouped, predictions_grouped)
    
    # Save per-database F1 scores to file
    with open(f1_per_db_file, "w", encoding="utf-8") as file:
        json.dump(db_metrics, file, indent=4)
    
    print(f"F1 for each db_id saved to {f1_per_db_file}")
    
    # Generate and save visualization of F1 scores
    plot_f1_scores(db_metrics, plot_image_file)  # Add the image file path
    print(f"The F1 chart has been saved as an image in {plot_image_file}")

# Execute the main function if this script is run directly
if __name__ == "__main__":
    main()
