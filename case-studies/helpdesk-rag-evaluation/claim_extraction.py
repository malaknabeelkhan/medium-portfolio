import json
from rag_pipeline import llm

def extract_claim(answer):
    prompt = f"""
Extract factual claims explicitly stated in the answer.

Rules:
1. Each claim must express one independently verifiable fact.
2. Do not introduce new information.
3. Do not add assumptions.
4. Return a JSON array of strings only.

Answer:
{answer}
"""
    schema = {
         "type":"array",
         "items":{"type":"string"}
    }


    response = llm(prompt,output_format=schema)
    try:
        claims = json.loads(response)
    except json.JSONDecodeError as error:
        print("Invalid JSON returned by model:")
        print(repr(response))
        raise ValueError("Claim extraction returned invalid JSON.") from error

    if not isinstance(claims, list):
        raise ValueError("Expected JSON list")

    if not all (isinstance(claim, str) and claim.strip() for claim in claims):
        raise ValueError("Every claim must be a non empty string")

    return claims


if __name__ == "__main__":
        answer = """
    A printer may be offline because its power cable
    is disconnected. Check the USB or network cable.
    Restarting the Print Spooler may also help.
    """

        claims = extract_claim(answer)

        for index, claim in enumerate(claims, start=1):
              print(f"{index}.{claim}")