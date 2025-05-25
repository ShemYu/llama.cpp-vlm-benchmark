# VLM Performance Evaluation Pipeline

## Overview
This project provides a pipeline to evaluate and compare the performance (specifically Time To First Token - TTFT) of language models. It benchmarks models running via Hugging Face Transformers library against their GGUF-quantized counterparts served by a `llama.cpp` API.

## Features
-   Benchmark Time To First Token (TTFT) for language models.
-   Compare Hugging Face `transformers` baseline performance against `llama.cpp` (via API).
-   Configurable models (Hugging Face identifiers and GGUF models via `llama.cpp` API).
-   Support for short and long text prompt datasets.
-   Generates a summary report table with average TTFT and success rates.
-   Exports detailed benchmark results to a CSV file.

## Project Structure
```
.
├── data/
│   ├── long_prompts.txt        # Long input prompts
│   └── short_prompts.txt       # Short input prompts
├── scripts/
│   └── benchmark.py            # Main benchmarking script
├── src/
│   ├── baseline_runner.py      # HF Transformers inference
│   ├── config.py               # Configuration file
│   ├── __init__.py
│   └── llamacpp_runner.py      # Llama.cpp API client
├── tests/
│   └── __init__.py
├── .gitignore                  # (Placeholder - not yet created in this project)
├── LICENSE                     # (Placeholder - not yet created in this project)
├── README.md
└── requirements.txt            # Python dependencies
```

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/exampleuser/vlm-performance-eval.git
    cd vlm-performance-eval
    ```

2.  **Create a Python Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install `transformers`, `torch`, and `requests`.

## Configuration

All configurations are managed in `src/config.py`. Before running the benchmark, modify this file to suit your setup:

-   **`BASELINE_MODEL_NAME`**: (String) The Hugging Face model identifier for the baseline tests.
    *   Example: `"gpt2"`, `"EleutherAI/pythia-70m-deduped"`
    *   The script will download this model if it's not cached locally by `transformers`.

-   **`LLAMACPP_API_BASE_URL`**: (String) The base URL of your running `llama.cpp` API service.
    *   Example: `"http://localhost:8000"`

-   **`LLAMACPP_MODEL_ALIAS`**: (String or None) This setting is crucial for testing GGUF models with the `llama.cpp` runner. It should be set to the **exact filename of the GGUF model** that your `llama.cpp` server is configured to serve (e.g., `"gemma-2-9b-it.Q4_K_M.gguf"`).
    *   The `llamacpp_runner.py` script will use this alias to request inference from your `llama.cpp` server.
    *   Ensure your `llama.cpp` server is started and explicitly configured to load and serve the model specified by this alias. Refer to the "Running the `llama.cpp` API Service" section below for server setup examples.
    *   If your server is serving a single, default model and doesn't require an alias or specific model name in the API request, you might set this to `None`. However, for clarity and explicit GGUF testing, specifying the filename is recommended.
    *   For comparison, the baseline (Hugging Face) runner uses the `BASELINE_MODEL_NAME` for its tests.
    *   Example: `"gemma-2-9b-it.Q4_K_M.gguf"`, `"mistral-7b-instruct-v0.1.Q4_K_M.gguf"`

-   **`SHORT_PROMPTS_FILE`**: (String) Path to the file containing short input prompts.
    *   Default: `"data/short_prompts.txt"`

-   **`LONG_PROMPTS_FILE`**: (String) Path to the file containing long input prompts.
    *   Default: `"data/long_prompts.txt"`

-   **`MAX_NEW_TOKENS_FOR_TTFT`**: (Integer) The number of new tokens to request for TTFT measurement. This should be a small value (e.g., 5-10) as we are primarily interested in how quickly the *first* token is generated.
    *   Default: `10`

-   **Using Gemma Models (e.g., `google/gemma-3-1b-it`)**:
    *   To use models like Gemma, set the `BASELINE_MODEL_NAME` to the appropriate Hugging Face identifier (e.g., `"google/gemma-3-1b-it"`).
    *   The `baseline_runner.py` script has been updated to include `trust_remote_code=True` when loading models. This is necessary for some models like Gemma that require custom code execution.
    *   **Note on Dependencies**: Running Gemma models requires `torch`, `transformers`, and potentially other large libraries. During development, full benchmarking of Gemma was hindered by environment disk space limitations during the installation of these dependencies. Users should ensure they have sufficient disk space and these libraries correctly installed in their environment.

## Running the `llama.cpp` API Service

This benchmarking tool **requires a separate `llama.cpp` API service to be running and accessible** at the URL specified in `LLAMACPP_API_BASE_URL`.

You are responsible for setting up and running this service. A common way to do this is using the server provided with `llama-cpp-python` (if you are using its Python bindings) or the main `llama.cpp` project's server:

**Using `llama-cpp-python` server:**
```bash
# Ensure llama-cpp-python is installed (pip install llama-cpp-python --upgrade)
python -m llama_cpp.server --model path/to/your/model.gguf --host 0.0.0.0 --port 8000
```

**Using `llama.cpp` main server:**
(Refer to `llama.cpp` documentation for exact command, often looks like)
```bash
./server -m path/to/your/model.gguf -c 4096 --host 0.0.0.0 --port 8000
```

-   Replace `path/to/your/model.gguf` with the actual path to your GGUF model file.
-   Ensure the host and port match what you set in `src/config.py`.
-   Refer to the [`llama.cpp`](https://github.com/ggerganov/llama.cpp) or [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python) documentation for more details on running the server, including GPU acceleration options and model compatibility.

## Running the Benchmark

Once you have:
1.  Installed dependencies (`pip install -r requirements.txt`).
2.  Configured `src/config.py` with your model names and API endpoint.
3.  Ensured your `llama.cpp` API service is running and accessible.

You can run the benchmark script from the project root directory:

```bash
python scripts/benchmark.py
```

## Understanding the Output

The script will output:

1.  **Live Progress:** Details of each prompt being tested with each runner (baseline, llama.cpp) and its measured TTFT. Error messages will be shown if a run fails.
    ```
    Starting VLM Performance Benchmark...
    Baseline Model: gpt2
    Llama.cpp API URL: http://localhost:8000
    Max new tokens for TTFT: 10
    ------------------------------

    Loading short prompts from: data/short_prompts.txt

    --- Testing short prompt 1/3 ---
    Running Baseline (gpt2)...
    Baseline TTFT: 0.0871s
    Running Llama.cpp (API: http://localhost:8000)...
    Llama.cpp TTFT: 0.0352s
    ...
    ```

2.  **Summary Report Table:** After all tests are complete, a formatted table summarizing the results will be printed:
    ```
    ========================================
            Benchmark Summary Report
    ========================================
    Prompt Type | Runner    | Avg TTFT (s) | Success Rate
    ----------------------------------------
    Short       | Baseline  | 0.0850       | 3/3
    Short       | Llama.cpp | 0.0340       | 3/3
    ----------------------------------------
    Long        | Baseline  | 0.5500       | 3/3
    Long        | Llama.cpp | 0.2100       | 3/3
    ========================================
    (Note: TTFT averages are for successful runs only)
    ```
    -   **Prompt Type:** "Short" or "Long" based on the input file.
    -   **Runner:** "Baseline" (Hugging Face) or "Llama.cpp".
    -   **Avg TTFT (s):** Average Time To First Token in seconds for successful runs in that category.
    -   **Success Rate:** Number of successful runs out of total attempts for that category. (e.g., 3/3 means all 3 prompts were processed successfully).

3.  **CSV Output File:**
    *   A detailed log of all benchmark runs is saved to a CSV file in the project root directory.
    *   The filename is timestamped, e.g., `benchmark_results_YYYYMMDD_HHMMSS.csv`.
    *   This file contains the following columns for each prompt and runner combination:
        *   `prompt_type`: e.g., "short", "long"
        *   `prompt_idx`: Index of the prompt within its file.
        *   `prompt_text`: The actual prompt text.
        *   `runner`: "baseline" or "llamacpp".
        *   `output_preview`: A short preview (first 50 characters) of the generated text. "ERROR" if the run failed.
        *   `ttft`: Time To First Token in seconds. -1.0 if the run failed.

## Customizing Input Prompts

-   You can modify or add new prompts to `data/short_prompts.txt` and `data/long_prompts.txt`.
-   The script expects one prompt per line.
-   Empty lines or lines consisting only of whitespace will be ignored by the `load_prompts` function.

## Troubleshooting
-   **Model Not Found (Hugging Face):**
    -   Ensure `BASELINE_MODEL_NAME` in `src/config.py` is a valid Hugging Face model identifier (e.g., "gpt2", "EleutherAI/pythia-70m-deduped").
    -   Check for typos in the model name.
    -   An internet connection is required for the first download of a model.

-   **Connection Errors (Llama.cpp API):**
    -   **Verify Service:** Double-check that your `llama.cpp` API service is running.
    -   **URL & Port:** Confirm that `LLAMACPP_API_BASE_URL` in `src/config.py` (e.g., `"http://localhost:8000"`) exactly matches the host and port your `llama.cpp` server is listening on.
    -   **Firewall:** Ensure no firewall is blocking connections to the `llama.cpp` server port.
    -   **Server Logs:** Check the console output of your `llama.cpp` server for any error messages or clues. It might indicate issues with the model loading or request handling.
    -   **Model Alias:** If your `llama.cpp` server is configured to serve multiple models or requires a specific model identifier in the API request, ensure `LLAMACPP_MODEL_ALIAS` is correctly set in `src/config.py`. If the server doesn't need it, `LLAMACPP_MODEL_ALIAS = None` is appropriate.

-   **Python Errors / Missing Modules:**
    -   Ensure you have activated your Python virtual environment (e.g., `source .venv/bin/activate`).
    -   Make sure all dependencies are installed: `pip install -r requirements.txt`.

-   **Incorrect TTFT Values or All Failures:**
    -   For `llama.cpp`, ensure the API endpoint structure in `src/llamacpp_runner.py` (`/v1/completions`) and the expected JSON response format match what your `llama.cpp` server provides. The current implementation assumes an OpenAI-compatible `/v1/completions` endpoint. If your server uses a different path or response structure (e.g., `/completion` or a chat-style endpoint), the `run_llamacpp_inference` function will need adjustments.
    -   For `baseline_runner`, ensure the chosen model is compatible with `AutoModelForCausalLM`.

-   **Low Performance / Unexpectedly High TTFT:**
    -   Ensure `MAX_NEW_TOKENS_FOR_TTFT` in `src/config.py` is a small number (e.g., 1-10).
    -   If running models on CPU, performance will be significantly slower than on GPU.
    -   For `llama.cpp`, ensure it's compiled with appropriate hardware acceleration (e.g., BLAS, cuBLAS for NVIDIA GPUs, Metal for Apple Silicon) for optimal performance.

## Running Tests (Optional)

This project includes placeholder unit and integration tests. To run them:

1.  Ensure you have installed the development dependencies:
    ```bash
    pip install pytest requests-mock
    ```
    (These should already be in `requirements.txt` if you've followed the main setup).

2.  Run pytest from the project root:
    ```bash
    python -m pytest
    ```

*Note: Many tests are placeholders and will require further implementation, especially those needing mocks for external services or Hugging Face models.*
```
