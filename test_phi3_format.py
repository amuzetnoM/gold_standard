import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path("~/syndicate").expanduser().resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.local_llm import LLMConfig, LocalLLM

model_path = os.path.expanduser("~/.cache/syndicate/models/Phi-3-mini-4k-instruct-q4.gguf")
config = LLMConfig()
llm = LocalLLM(model_path, config)

# Phi-3 specific prompt format
prompt = "<|user|>\nHello, tell me a short joke about gold.<|end|>\n<|assistant|>"
print(f"Generating for prompt (instruct format):\n{prompt}")

output = llm._llama(prompt, max_tokens=100, temperature=0.7, echo=False)

print("\n--- RAW OUTPUT ---")
print(output)
print("--- END RAW OUTPUT ---")

response = output["choices"][0]["text"]
print("\n--- TEXT RESPONSE ---")
print(response)
print("--- END TEXT RESPONSE ---")
