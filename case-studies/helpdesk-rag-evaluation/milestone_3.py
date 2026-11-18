def calculate_faithfulness(supported_claims, total_claims):
    if total_claims == 0:
        return 0.0

    # TODO 1: Calculate faithfulness score
    faithfulness_score = supported_claims / total_claims

    # TODO 2: Return the score
    return faithfulness_score


# TEST
score = calculate_faithfulness(
    supported_claims=2,
    total_claims=3
)




def count_claims(claims):

    # TODO 1: Count the claims
    count = len(claims)

    # TODO 2: Return the count
    return count
    




def count_supported_claims(verification_results):

    # TODO 1: Initialize a counter
    counter = 0

    # TODO 2: Iterate through verification results
    for item in verification_results:


        # TODO 3: Count supported claims
        if item:
            counter += 1

    # TODO 4: Return the count
    return counter


import json
def get_evaluation_score(prompt, llm):

    schema = {
        "type": "number",
        "minimum": 0,
        "maximum": 1
    }

    response = llm(prompt, output_format=schema)

    score = float(json.loads(response))

    if not 0.0 <= score <= 1.0:
        raise ValueError(f"Invalid evaluation score: {score}")

    return score


def evaluate_faithfulness(verification_results):

    # TODO 1: Get total number of claims
    no_of_claims = count_claims(verification_results)

    # TODO 2: Count supported claims
    supported_claims = count_supported_claims(verification_results)

    # TODO 3: Calculate faithfulness score
    faithfulness_score = calculate_faithfulness(supported_claims ,no_of_claims)

    # TODO 4: Return the score
    return faithfulness_score





def verify_claim(context, claim, llm):

    prompt = f"""
    Retrieved context:
    {context}

    Claim:
    {claim}

    Determine whether the claim is supported by the context.

    Return only:
    SUPPORTED
    or
    NOT_SUPPORTED
    """

    # TODO 1: Send prompt to the LLM using llm
    response = llm(prompt).strip().upper()

    # TODO 2: Read the LLM response
    # TODO 3: Return True or False
    if response == "SUPPORTED":
        return True
    elif response == "NOT_SUPPORTED":
        return False
    else:
        raise ValueError(f"Unexpected LLM response: {response}")




# from google import genai

# client = genai.Client()

# def llm(prompt):
#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=prompt
#     )

#     return response.text

import ollama

def llm(prompt):
    response = ollama.generate(
        model="qwen2.5-coder:3b",
        prompt=prompt
    )
    return response['response']



def evaluate_answer_faithfulness(context, claims, llm):

    verification_results = []

    # TODO 1: Iterate through claims
    for claim in claims:

    # TODO 2: Verify each claim using verify_claim()
        result = verify_claim(context,claim,llm)

    # TODO 3: Append each verification result
        verification_results.append(result)

    # TODO 4: Calculate faithfulness using evaluate_faithfulness()
    score = evaluate_faithfulness(verification_results)
    # TODO 5: Return score and verification results
    return score, verification_results



def evaluate_answer_relevance(question, answer, llm):

    prompt = f"""
    User question:
    {question}

    Generated answer:
    {answer}

    Evaluate how relevant the answer is to the question.

    Return ONLY a number between 0 and 1.
    """

    return get_evaluation_score(prompt, llm)



def evaluate_context_relevance(question, context, llm):


    prompt = f"""
    You are evaluating context relevance in a RAG system.

    User question:
    {question}

    Retrieved context:
    {context}

    Evaluate how useful the retrieved context is for answering
    the user's question.

    Use these criteria:

    1. Relevance:
    Does the context contain information related to the question?

    2. Answerability:
    Does the context provide information that can help answer
    the question?

    3. Coverage:
    Does the context contain sufficient relevant information
    to answer the question?

    Scoring:
    - 0.0: Completely irrelevant; provides no useful information.
    - 0.25: Mostly irrelevant; contains very little useful information.
    - 0.50: Partially relevant; contains some useful information
    but lacks important information.
    - 0.75: Highly relevant; contains sufficient useful information
    with some gaps.
    - 1.0: Directly relevant and provides sufficient information
    to answer the question.

    Important rules:
    - Do not penalize context for containing additional relevant
    information that is not explicitly used in the answer.
    - Judge relevance to the question, not similarity to a
    generated answer.
    - Do not require the context to cover every possible scenario.
    - Evaluate only the retrieved context.
    - Don't penalize brief answer too much if it is correct

    Return ONLY a number between 0 and 1.
    """


    # TODO 1: Send prompt to LLM
    response = llm(prompt)

    # TODO 2: Convert response into float
    score = float(response)

    # TODO 3: Return score
    return score




def evaluate_generation(question, answer, context, claims, llm):

    # TODO 1: Calculate faithfulness
    faithfulness_score,_ = evaluate_answer_faithfulness(context, claims, llm)


    # TODO 2: Calculate answer relevance
    answer_relevance_score = evaluate_answer_relevance(question, answer, llm)

    # TODO 3: Calculate context relevance
    context_relevance_score = evaluate_context_relevance(question, context,llm)

    # TODO 4: Create evaluation report
    report = {
        "faithfulness": faithfulness_score,
        "answer_relevance": answer_relevance_score,
        "context_relevance": context_relevance_score
    }
    # TODO 5: Return report
    return report


