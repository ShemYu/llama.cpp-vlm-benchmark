import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def run_baseline_inference(model_name_or_path: str, prompt: str, max_new_tokens: int = 10) -> tuple[str, float]:
    """
    Runs baseline inference using Hugging Face Transformers and measures Time To First Token (TTFT).
    Returns the generated text (or part of it) and TTFT in seconds.
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        model = AutoModelForCausalLM.from_pretrained(model_name_or_path)

        # Ensure model is on GPU if available, for fair comparison later
        # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # model.to(device)

        inputs = tokenizer(prompt, return_tensors="pt") # .to(device)

        start_time = time.perf_counter()

        # Generate a small number of tokens to approximate TTFT
        # For more accurate TTFT, a streaming approach or custom generation loop might be needed
        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, pad_token_id=tokenizer.eos_token_id)

        end_time = time.perf_counter()

        ttft = end_time - start_time

        generated_text = tokenizer.decode(outputs[0, inputs['input_ids'].shape[1]:], skip_special_tokens=True) # Slice off prompt tokens

        return generated_text, ttft

    except Exception as e:
        print(f"Error during baseline inference: {e}")
        return "", -1.0 # Indicate error

if __name__ == '__main__':
    # Example usage (optional, for direct testing of the module)
    # model_id = "gpt2" # Replace with a small model for testing, e.g., "gpt2"
    # test_prompt = "Hello, how are you?"
    # print(f"Testing baseline inference with model: {model_id} and prompt: '{test_prompt}'")
    # output, ttft = run_baseline_inference(model_id, test_prompt)
    # if ttft != -1.0:
    #     print(f"Generated output (first {len(output.split())} tokens): '{output}'")
    #     print(f"Time To First Token (TTFT): {ttft:.4f} seconds")
    # else:
    #     print("Baseline inference failed.")
    pass
