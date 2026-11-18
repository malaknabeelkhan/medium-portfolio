
# ==========================================
# HELPDESK RAG EVALUATION LAB
# MILESTONE 1: DATASET FOUNDATION
# ==========================================


# 1. KNOWLEDGE BASE DOCUMENTS

documents = {
    "D1": "Wi-Fi troubleshooting: Check network connectivity, IP configuration, and DNS settings.",
    "D2": "Printer troubleshooting: Check printer power, connection, print queue, and spooler service.",
    "D3": "Password reset: Users can reset their Windows password through the approved IT process.",
    "D4": "DNS troubleshooting: Verify DNS server configuration and test name resolution."
}


# 2. EVALUATION QUESTIONS AND GROUND TRUTH

evaluation_queries = [
    {
        "query_id": "Q1",
        "question": "My laptop connects to Wi-Fi but cannot access internal resources.",
        "relevant_doc_ids": ["D1", "D4"]
    },
    {
        "query_id": "Q2",
        "question": "My printer is showing offline.",
        "relevant_doc_ids": ["D2"]
    },
    {
        "query_id": "Q3",
        "question": "How can I reset my Windows password?",
        "relevant_doc_ids": ["D99"]
    }
]


# 3. DATASET VALIDATION

def validate_dataset(documents, evaluation_queries):

    # Check whether documents and queries exist
    if not documents or not evaluation_queries:
        raise ValueError("Dataset cannot be empty")

    document_ids = set(documents.keys())
    seen_query_ids = set()
    for query in evaluation_queries:

        query_id = query["query_id"]
        relevant_ids = query["relevant_doc_ids"]

        # TODO 1:
        # it checks the query_id in seen_query_ids - if it exists then it raise value error or it is added to seen_query_ids if it is not in it already
        if query_id in seen_query_ids:
            raise ValueError("Duplicate query ID")
        seen_query_ids.add(query_id)


        # TODO 2:
        # It iterate through relevant_ids to pick one id and check it in document_ids. if it is not present then value error is raised.
        for doc_id in relevant_ids:
            if doc_id not in document_ids:
                raise ValueError(f"Invalid document ID: {id}")
                  
        # I am getting error of value error. I added the print statement to check it. I think it is because of the relevant_ids because it is list of lists. and document ids is dictionary.

    return True


# 4. RUN VALIDATION

if __name__ == "__main__":

    result = validate_dataset(documents, evaluation_queries)

    print("Dataset validation:", result)
    print("Total documents:", len(documents))
    print("Total evaluation queries:", len(evaluation_queries))
    print("Dataset is ready for evaluation!")
