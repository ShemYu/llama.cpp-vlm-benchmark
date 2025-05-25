import time
import requests
import json

def run_llamacpp_inference(api_base_url: str, prompt: str, model_alias: str = None, n_predict: int = 10) -> tuple[str, float]:
    """
    Runs inference by calling a llama.cpp API service and measures Time To First Token (TTFT).
    Assumes an OpenAI-compatible completions endpoint.
    Returns the generated text (or part of it) and TTFT in seconds.
    """
    # Ensure the base URL doesn't have a trailing slash, then append endpoint
    if api_base_url.endswith('/'):
        api_base_url = api_base_url[:-1]
    endpoint = f"{api_base_url}/v1/completions" # Or /v1/chat/completions if more appropriate

    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "n_predict": n_predict, # Max tokens to generate
        # "model": model_alias, # Include if your server uses this to select models
        # "stream": True, # Set to True for more accurate TTFT if server supports SSE
    }

    # Remove None values from payload
    if model_alias:
        payload["model"] = model_alias
    
    # If not using streaming, this approach is simpler
    # For streaming, you'd use response.iter_lines() or similar
    
    try:
        start_time = time.perf_counter()
        response = requests.post(endpoint, headers=headers, json=payload) # Add stream=True to payload and requests.post if using streaming
        response.raise_for_status() # Raise an exception for bad status codes

        # Assuming non-streaming for simplicity first:
        # The first token is available once the response is received and parsed.
        end_time = time.perf_counter()
        ttft = end_time - start_time

        # For a non-streaming OpenAI-compatible /v1/completions endpoint:
        response_data = response.json()
        generated_text = response_data.get("choices", [{}])[0].get("text", "").strip()
        
        # If using /v1/chat/completions, the structure might be:
        # generated_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # If streaming were implemented and server sends SSE:
        # first_token_text = ""
        # for line in response.iter_lines():
        #     if line:
        #         decoded_line = line.decode('utf-8')
        #         if decoded_line.startswith('data: '):
        #             json_data = json.loads(decoded_line[len('data: '):])
        #             if not first_token_text: # Capture TTFT on first actual data
        #                 end_time = time.perf_counter() # TTFT measured here
        #                 ttft = end_time - start_time 
        #             # Extract token from json_data (depends on actual API response structure)
        #             # e.g., token = json_data.get("choices", [{}])[0].get("text", "")
        #             # first_token_text += token # Accumulate if needed or just grab first
        #             # if some condition for first token is met: break
        #             # This part needs actual API spec for streaming
        # generated_text = first_token_text # Or however it's assembled

        return generated_text, ttft

    except requests.exceptions.RequestException as e:
        print(f"Error during llama.cpp API request: {e}")
        return "", -1.0
    except Exception as e:
        print(f"Error processing llama.cpp response: {e}")
        return "", -1.0

if __name__ == '__main__':
    # Example usage (optional, for direct testing of the module)
    # This will only work if you have a llama.cpp server running at the specified URL
    # test_api_url = "http://localhost:8000" # Replace with your llama.cpp server URL
    # test_prompt = "Explain what a GGUF file is in one sentence."
    # print(f"Testing llama.cpp inference via API: {test_api_url} with prompt: '{test_prompt}'")
    # output, ttft = run_llamacpp_inference(test_api_url, test_prompt)
    # if ttft != -1.0:
    #     print(f"Generated output: '{output}'")
    #     print(f"Time To First Token (TTFT): {ttft:.4f} seconds")
    # else:
    #     print("llama.cpp inference failed.")
    pass
