from rag_pipeline import generate_answer, llm
from vector_store import retrieve_context, retrieve_document_ids
from claim_extraction import extract_claim
from milestone_3 import evaluate_generation
from milestone_2 import evaluate_retrieval_dataset, ground_truth


evaluation_queries = {
    "Q1": "Why is my printer showing offline?",
    "Q2": "Why can't my computer connect to Wi-Fi?",
    "Q3": "How do I reset my Windows password?",
    "Q4": "Why can't I access websites using their domain names?"
}



def run_rag_evaluation(question, top_k=1):
    context, context_document_ids = retrieve_context(question, top_k=top_k)
    answer = generate_answer(question, context)
    claims = extract_claim(answer)

    evaluation = evaluate_generation(
        question,
        answer,
        context,
        claims,
        llm
    )

    return {
        "question": question,
        "retrieved_documents": context_document_ids,
        "answer": answer,
        "claims": claims,
        "evaluation": evaluation
    }



def run_complete_evaluation(k=1):
    retrievel_results = {}
    generation_results = {}

    for query, question in evaluation_queries.items():
        retrived_doc = retrieve_document_ids(question, k)
        retrievel_results[query] = retrived_doc
        result = run_rag_evaluation(question, top_k=k)
        generation_results[query] = result

    retrievel_metric = evaluate_retrieval_dataset(retrievel_results, ground_truth, k)

    return {
    "retrieval_results": retrievel_results,
    "retrieval_metrics": retrievel_metric,
    "generation_results": generation_results
    }





if __name__ == "__main__":

    results = run_complete_evaluation(k=1)

    print("\n" + "=" * 55)
    print("RETRIEVAL EVALUATION")
    print("=" * 55)

    for query_id, retrieved_docs in results["retrieval_results"].items():

        print(f"\n{query_id}")
        print("Retrieved:", retrieved_docs)

        metrics = results["retrieval_metrics"]["per_query"][query_id]

        for metric, score in metrics.items():
            print(f"{metric}: {score:.3f}")

    print("\nOVERALL RETRIEVAL METRICS")

    for metric, score in results["retrieval_metrics"].items():

        if metric != "per_query":
            print(f"{metric}: {score:.3f}")

    print("\n" + "=" * 55)
    print("GENERATION EVALUATION")
    print("=" * 55)

    for query_id, result in results["generation_results"].items():

        print(f"\n{query_id}")
        print("Answer:", result["answer"])

        print("\nClaims:")
        for claim in result["claims"]:
            print("-", claim)

        print("\nGeneration metrics:")
        for metric, score in result["evaluation"].items():
            print(f"{metric}: {score:.3f}")