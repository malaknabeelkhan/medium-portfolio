import os
import requests
from dotenv import load_dotenv

load_dotenv()
COLAB_BASE_URL = os.getenv("COLAB_BASE_URL")
COLAB_MODEL = os.getenv("COLAB_MODEL")
def llm(prompt,output_format=None):
    if not COLAB_BASE_URL:
        raise ValueError("Colab Base Url is not present in .env")

    url = f"{COLAB_BASE_URL.rstrip('/')}/api/generate"

    payload = {
        "model":COLAB_MODEL,
        "prompt":prompt,
        "stream":False,
        "options":{
            "temperature":0.1,
            "num_predict":512
        }
    }
    if output_format is not None:
        payload["format"] = output_format

    response = requests.post(
        url,
        json=payload,
        timeout=300
    )
    response.raise_for_status()
    result = response.json()
    return result["response"]

from vector_store import retrieve_context



def generate_answer(question, context):
    prompt = f"""
    You are an IT HelpDesk assistant.

    Answer the user's question using only the provided context.

    If the context does not contain enough information,
    clearly say that you do not have enough information.

    Do not invent troubleshooting steps.
    Context:
    {context}
    Question:
    {question}
"""
    return llm(prompt)


if __name__ == "__main__":
    question = "why is my printer showing offline"
    context, document_ids = retrieve_context(question)
    answer = generate_answer(question, context)
    print("Answer: ", answer)

