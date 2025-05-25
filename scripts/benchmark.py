import sys
import os
import time # For any additional diagnostic timing if needed
import csv
from datetime import datetime

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src import config
from src import baseline_runner
from src import llamacpp_runner
# import argparse # For potential future CLI arguments

def load_prompts(filepath: str) -> list[str]:
    prompts = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line:
                    prompts.append(stripped_line)
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {filepath}")
    return prompts

def main():
    print("Starting VLM Performance Benchmark...")
    print(f"Baseline Model: {config.BASELINE_MODEL_NAME}")
    print(f"Llama.cpp API URL: {config.LLAMACPP_API_BASE_URL}")
    if config.LLAMACPP_MODEL_ALIAS:
        print(f"Llama.cpp Model Alias: {config.LLAMACPP_MODEL_ALIAS}")
    print(f"Max new tokens for TTFT: {config.MAX_NEW_TOKENS_FOR_TTFT}")
    print("-" * 30)

    results = []

    prompt_files = {
        "short": config.SHORT_PROMPTS_FILE,
        "long": config.LONG_PROMPTS_FILE
    }

    for prompt_type, filepath in prompt_files.items():
        print(f"\nLoading {prompt_type} prompts from: {filepath}")
        prompts = load_prompts(filepath)
        if not prompts:
            print(f"No prompts found or file error for {filepath}. Skipping.")
            continue

        for i, prompt_text in enumerate(prompts):
            print(f"\n--- Testing {prompt_type} prompt {i+1}/{len(prompts)} ---")
            # print(f"Prompt: "{prompt_text[:100]}..."" if len(prompt_text) > 100 else f"Prompt: "{prompt_text}"")

            # Baseline Runner
            print(f"Running Baseline ({config.BASELINE_MODEL_NAME})...")
            try:
                baseline_output, baseline_ttft = baseline_runner.run_baseline_inference(
                    config.BASELINE_MODEL_NAME,
                    prompt_text,
                    max_new_tokens=config.MAX_NEW_TOKENS_FOR_TTFT
                )
                if baseline_ttft != -1.0:
                    print(f"Baseline TTFT: {baseline_ttft:.4f}s")
                    results.append({
                        'prompt_type': prompt_type,
                        'prompt_idx': i,
                        'prompt_text': prompt_text,
                        'runner': 'baseline',
                        'output_preview': baseline_output[:50], # Store a preview
                        'ttft': baseline_ttft
                    })
                else:
                    print("Baseline inference failed.")
                    results.append({
                        'prompt_type': prompt_type,
                        'prompt_idx': i,
                        'prompt_text': prompt_text,
                        'runner': 'baseline',
                        'output_preview': "ERROR",
                        'ttft': -1.0
                    })
            except Exception as e:
                print(f"Exception in baseline_runner: {e}")
                results.append({
                        'prompt_type': prompt_type,
                        'prompt_idx': i,
                        'prompt_text': prompt_text,
                        'runner': 'baseline',
                        'output_preview': f"ERROR: {e}",
                        'ttft': -1.0
                    })


            # Llama.cpp Runner
            print(f"Running Llama.cpp (API: {config.LLAMACPP_API_BASE_URL})...")
            try:
                llamacpp_output, llamacpp_ttft = llamacpp_runner.run_llamacpp_inference(
                    config.LLAMACPP_API_BASE_URL,
                    prompt_text,
                    model_alias=config.LLAMACPP_MODEL_ALIAS,
                    n_predict=config.MAX_NEW_TOKENS_FOR_TTFT
                )
                if llamacpp_ttft != -1.0:
                    print(f"Llama.cpp TTFT: {llamacpp_ttft:.4f}s")
                    results.append({
                        'prompt_type': prompt_type,
                        'prompt_idx': i,
                        'prompt_text': prompt_text,
                        'runner': 'llamacpp',
                        'output_preview': llamacpp_output[:50], # Store a preview
                        'ttft': llamacpp_ttft
                    })
                else:
                    print("Llama.cpp inference failed.")
                    results.append({
                        'prompt_type': prompt_type,
                        'prompt_idx': i,
                        'prompt_text': prompt_text,
                        'runner': 'llamacpp',
                        'output_preview': "ERROR",
                        'ttft': -1.0
                    })
            except Exception as e:
                print(f"Exception in llamacpp_runner: {e}")
                results.append({
                        'prompt_type': prompt_type,
                        'prompt_idx': i,
                        'prompt_text': prompt_text,
                        'runner': 'llamacpp',
                        'output_preview': f"ERROR: {e}",
                        'ttft': -1.0
                    })


    print("\n" + "=" * 30)
    print("Benchmark Finished.")
    print("=" * 30)

    if results: # 'results' is the list collected in the loops
        print_summary_report(results)
        save_results_to_csv(results)
    else:
        print("No results collected to report.")
    
    # The main function can still return results if needed, but its primary job is to orchestrate and report.
    return results

def calculate_stats(results: list[dict], prompt_filter: str, runner_filter: str) -> tuple[float, int, int]:
    """Helper to calculate stats for a specific prompt type and runner."""
    filtered_runs = [
        r for r in results
        if r['prompt_type'] == prompt_filter and r['runner'] == runner_filter
    ]
    successful_runs = [r for r in filtered_runs if r['ttft'] != -1.0]
    
    total_ttft = sum(r['ttft'] for r in successful_runs)
    avg_ttft = total_ttft / len(successful_runs) if successful_runs else 0.0
    
    return avg_ttft, len(successful_runs), len(filtered_runs)

def print_summary_report(results: list[dict]):
    """Prints a formatted summary report of the benchmark results."""
    print("\n" + "=" * 40)
    print("        Benchmark Summary Report")
    print("=" * 40)
    print(f"{'Prompt Type':<12} | {'Runner':<9} | {'Avg TTFT (s)':<12} | {'Success Rate':<12}")
    print("-" * 40)

    prompt_types = sorted(list(set(r['prompt_type'] for r in results)))
    runners = sorted(list(set(r['runner'] for r in results)))

    for p_type in prompt_types:
        for runner_name in runners:
            avg_ttft, num_successful, num_total = calculate_stats(results, p_type, runner_name)
            success_rate_str = f"{num_successful}/{num_total}"
            print(f"{p_type.capitalize():<12} | {runner_name.capitalize():<9} | {avg_ttft:<12.4f} | {success_rate_str:<12}")
        if p_type != prompt_types[-1]: # Add a separator between prompt types
            print("-" * 40)
            
    print("=" * 40)
    print("(Note: TTFT averages are for successful runs only)")

def save_results_to_csv(results: list[dict], filename_prefix: str = "benchmark_results"):
    """Saves the detailed benchmark results to a timestamped CSV file."""
    if not results:
        print("No results to save to CSV.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    
    # Assuming all dictionaries in results have the same keys
    headers = results[0].keys()
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nDetailed results saved to: {os.path.join(os.getcwd(), filename)}")
    except IOError as e:
        print(f"Error saving results to CSV: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving CSV: {e}")

if __name__ == "__main__":
    collected_results = main()
    # collected_results are now processed by print_summary_report and save_results_to_csv within main()
