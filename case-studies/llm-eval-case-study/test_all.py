from models import MODELS
from llm_client import ask_model

for config in MODELS:
    try:
        answer,latency = ask_model(config,"Say hello in one word.")
        print(config["name"],"->",answer,f"({latency:.2f}s)")
    except Exception as e:
        print(config["name"], "FAILED:",e)