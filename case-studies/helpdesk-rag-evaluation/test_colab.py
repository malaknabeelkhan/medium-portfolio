import os
import requests
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("COLAB_BASE_URL")

response = requests.get(
    f"{base_url.rstrip('/')}/api/tags",
    timeout=30
)

response.raise_for_status()

print(response.json())
