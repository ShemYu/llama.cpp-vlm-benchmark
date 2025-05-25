# src/config.py

# --- Baseline Model Configuration ---
# Hugging Face model identifier for the baseline (non-llama.cpp) model
# Example: "gpt2", "EleutherAI/pythia-70m-deduped"
BASELINE_MODEL_NAME = "google/gemma-3-1b-it"

# --- Llama.cpp API Configuration ---
# Base URL of your llama.cpp server API
# Example: "http://localhost:8000"
LLAMACPP_API_BASE_URL = "http://localhost:8000"

# Optional: Model alias or specific GGUF model name if your llama.cpp server
# uses it to select among multiple models. Set to None if not needed.
# Example: "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
LLAMACPP_MODEL_ALIAS = "gemma-2-9b-it.Q4_K_M.gguf" # Or specify a model alias string

# --- Input Data Configuration ---
# Paths to the prompt files
SHORT_PROMPTS_FILE = "data/short_prompts.txt"
LONG_PROMPTS_FILE = "data/long_prompts.txt"

# --- Benchmarking Parameters ---
# Number of new tokens to request for TTFT measurement (should be small)
# This value will be used for both baseline and llama.cpp runners.
MAX_NEW_TOKENS_FOR_TTFT = 10
