import time
from openai import OpenAI
def ask_model(config,user_message, system_prompt=None):
    client = OpenAI(base_url=config["base_url"],api_key=config["api_key"])
    messages = []
    if system_prompt:
        messages.append({"role":"system","content":system_prompt})
    messages.append({"role":"user","content":user_message})

    start = time.time()
    response = client.chat.completions.create(model=config["model"], messages=messages,temperature=0)
    latency = time.time() - start
    return response.choices[0].message.content, latency