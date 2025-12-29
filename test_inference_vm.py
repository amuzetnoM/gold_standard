import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path("~/syndicate").expanduser().resolve()
sys.path.insert(0, str(PROJECT_ROOT))

print("Loading local_llm...")
try:
    from scripts.local_llm import LLMConfig, LocalLLM

    print("local_llm loaded successfully.")
except Exception as e:
    print(f"Error loading local_llm: {e}")
    sys.exit(1)

model_path = os.path.expanduser("~/.cache/syndicate/models/Phi-3-mini-4k-instruct-q4.gguf")
print(f"Testing model at: {model_path}")

try:
    config = LLMConfig()
    llm = LocalLLM(model_path, config)
    print("Model initialized successfully.")

    prompt = "Hello, tell me a short joke about gold."
    print(f"Generating for prompt: {prompt}")

    response = llm.generate(prompt, max_tokens=50)
    print("\n--- RESPONSE ---")
    print(response)
    print("--- END RESPONSE ---")
except Exception as e:
    print(f"Error during inference: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
