from collections import Counter
import json

with open('golden_dataset.json','r',encoding='utf-8') as f:
    data = json.load(f)
print("Total Example: ", len(data))

categories = [item["expected_output"]["category"] for item in data]
print(Counter(categories))