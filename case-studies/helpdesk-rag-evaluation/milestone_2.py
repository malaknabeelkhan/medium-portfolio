
# ==========================================
# HELPDESK RAG EVALUATION LAB
# MILESTONE 2: RETRIEVAL EVALUATION
# LESSON 2.1: PRECISION@K
# ==========================================

def precision_at_k(retrieved_docs, relevant_docs, k):

    # TODO 1:
    top_k_retrieved_doc = retrieved_docs[:k]


    # TODO 2:
    counter = 0
    for doc in top_k_retrieved_doc:
        if doc in relevant_docs:
            counter+=1

    # TODO 3:
    precision = counter / k

    return precision




def recall_at_k(retrieved_docs, relevant_docs, k):

    # TODO 1:
    top_k_retrieved_doc = retrieved_docs[:k]


    # TODO 2:
    counter = 0
    for doc in top_k_retrieved_doc:
        if doc in relevant_docs:
            counter += 1

    # TODO 3:
    recall = counter / len(relevant_docs)


    return recall


# ==========================================
# LESSON 2.3: MEAN RECIPROCAL RANK (MRR)
# ==========================================

def mean_reciprocal_rank(retrieval_results, ground_truth):

    reciprocal_ranks = []

    # TODO 1:
    for query in retrieval_results:


        # TODO 2:
        retrieved_docs = retrieval_results.get(query)
        relevant_docs = ground_truth.get(query)


        # TODO 3:
        for index, value in enumerate(retrieved_docs):
            if value in relevant_docs:
                rank_position = index + 1
                mrr = 1 / rank_position
                reciprocal_ranks.append(mrr)
                break
        else:
            reciprocal_ranks.append(0)


    # TODO 4:
    final_mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)
    return final_mrr





def reciprocal_rank(retrieved_docs, relevant_docs):

    reciprocal_ranks = []

    # TODO 1:


        # TODO 3:
    for index, value in enumerate(retrieved_docs):
        if value in relevant_docs:
            rank_position = index + 1
            mrr = 1 / rank_position
            reciprocal_ranks.append(mrr)
            break
    else:
        reciprocal_ranks.append(0)


    # TODO 4:
    reciprocal_rank = sum(reciprocal_ranks) / len(reciprocal_ranks)
    return reciprocal_rank


def evaluate_retrieval(retrieved_docs, relevant_docs, k):
    precision = precision_at_k(retrieved_docs, relevant_docs, k)
    recall = recall_at_k(retrieved_docs, relevant_docs, k)
    rr = reciprocal_rank(retrieved_docs, relevant_docs)
    return{
        "precision":precision,
        "recall":recall,
        "reciprocal_rank":rr
    }



def evaluate_retrieval_dataset(retrieval_results, ground_truth,k):
    per_query_result = {}

    for query_id, retrieved_doc in retrieval_results.items():
        relevant_doc = ground_truth[query_id]

        metric = evaluate_retrieval(retrieved_doc, relevant_doc,k)

        per_query_result[query_id] = metric

    mean_precision = sum(result["precision"] for result in per_query_result.values()) / len(per_query_result)
    mean_recall = sum(result["recall"] for result in per_query_result.values()) / len(per_query_result)
    mean_reciprocal = mean_reciprocal_rank(retrieval_results, ground_truth)

    return{
        "per_query": per_query_result,
        "Mean_Precision": mean_precision,
        "Mean_Recall": mean_recall,
        "Mean_Reciprocal_Rank": mean_reciprocal
    }



ground_truth = {
    "Q1": ["D2"],  # Printer troubleshooting
    "Q2": ["D1"],  # Wi-Fi connectivity
    "Q3": ["D3"],  # Windows password reset
    "Q4": ["D4"]   # DNS troubleshooting
}