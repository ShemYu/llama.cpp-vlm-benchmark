# tests/test_llamacpp_runner.py
import pytest
import requests_mock # from the requests-mock library
from src import llamacpp_runner

API_BASE_URL = "http://test-llamacpp-api:8000"

def test_run_llamacpp_inference_success(requests_mock):
    # TODO: Mock the requests.post call for a successful response
    # Example for non-streaming:
    # requests_mock.post(f"{API_BASE_URL}/v1/completions", json={
    #     "choices": [{"text": " generated text"}]
    # })
    # prompt = "Hello"
    # output, ttft = llamacpp_runner.run_llamacpp_inference(API_BASE_URL, prompt)
    # assert output == "generated text"
    # assert ttft > 0
    pass

def test_run_llamacpp_inference_api_error(requests_mock):
    # TODO: Mock requests.post for a 500 error
    # requests_mock.post(f"{API_BASE_URL}/v1/completions", status_code=500, text="Server Error")
    # prompt = "Hello"
    # output, ttft = llamacpp_runner.run_llamacpp_inference(API_BASE_URL, prompt)
    # assert output == ""
    # assert ttft == -1.0
    pass

def test_run_llamacpp_inference_connection_error(requests_mock):
    # TODO: Mock requests.post to raise a requests.exceptions.ConnectionError
    # from requests.exceptions import ConnectionError
    # requests_mock.post(f"{API_BASE_URL}/v1/completions", exc=ConnectionError)
    # prompt = "Hello"
    # output, ttft = llamacpp_runner.run_llamacpp_inference(API_BASE_URL, prompt)
    # assert output == ""
    # assert ttft == -1.0
    pass

# TODO: Add tests for streaming if that feature is implemented in llamacpp_runner
