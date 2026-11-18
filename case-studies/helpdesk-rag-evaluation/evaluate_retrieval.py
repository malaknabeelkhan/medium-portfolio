from milestone_2 import precision_at_k
from milestone_2 import recall_at_k
from milestone_2 import reciprocal_rank


def evaluate_retrieval(retrieval_results, ground_truth, k):

    evaluation_report = {}

    # TODO 1: Iterate through every query.
    for query in (retrieval_results):

        # TODO 2: Get retrieved documents and relevant documents.
            retrieved_docs = retrieval_results.get(query)
            relevant_docs = ground_truth.get(query)
        # TODO 3: Calculate Precision@K.
            precision = precision_at_k(retrieved_docs, relevant_docs, k)


        # TODO 4: Calculate Recall@K.
            recall = recall_at_k(retrieved_docs, relevant_docs, k)
        # TODO 5: Calculate Reciprocal Rank for this query.
            mrr = reciprocal_rank(retrieved_docs, relevant_docs)

        # TODO 6: Store all three metrics in evaluation_report.
            report = {
                "precision":precision, 
                "recall":recall, 
                "reciprocal_rank": mrr}          
            evaluation_report[query] = report

    return evaluation_report



# GROUND TRUTH

ground_truth = {
    "Q1": ["D2"],
    "Q2": ["D2"],
    "Q3": ["D2"],
    "Q4": ["D5"]
}


# RETRIEVAL RESULTS

retrieval_results = {
    "Q1": ["D2", "D1", "D3"],
    "Q2": ["D1", "D2", "D4"],
    "Q3": ["D1", "D3", "D2"],
    "Q4": ["D1", "D2", "D3"]
}


result = evaluate_retrieval(retrieval_results, ground_truth, k=3)

print(result)

# Output
# Q1 Precision@3: 0.67
# Q2 Precision@3: 0.33
# Q3 Precision@3: 0.33
# Q1 Recall@3: 0.67
# Q2 Recall@3: 1.00
# Q3 Recall@3: 0.50
# {'Q1': {'precision': 0.3333333333333333, 'recall': 1.0, 'reciprocal_rank': <function reciprocal_rank at 0x000001F21D122DE0>}, 'Q2': {'precision': 0.3333333333333333, 'recall': 1.0, 'reciprocal_rank': <function reciprocal_rank at 0x000001F21D122DE0>}, 'Q3': {'precision': 0.3333333333333333, 'recall': 1.0, 'reciprocal_rank': <function reciprocal_rank at 0x000001F21D122DE0>}, 'Q4': {'precision': 0.0, 'recall': 0.0, 'reciprocal_rank': <function reciprocal_rank at 0x000001F21D122DE0>}}