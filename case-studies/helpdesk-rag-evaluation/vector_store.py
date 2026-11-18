
import chromadb
import ollama

from documents import documents


# 1. Initialize persistent ChromaDB storage
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="helpdesk_documents"
)


# 2. Split documents into overlapping chunks
def chunk_document(text, chunk_size=100, overlap=20):

    words = text.split()
    chunks = []

    # TODO 1: Iterate through words using chunk_size.
    step = chunk_size - overlap
    for i in range(0, len(words), step):

    # TODO 2: Extract each chunk.
        
        chunk_words = (words[i:i+chunk_size])
    # TODO 3: Append the chunk to chunks.
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
    # TODO 4: Move forward by chunk_size - overlap.
    # TODO 5: Return chunks.

    return chunks


# 3. Embed and store document chunks
def index_documents(documents):

    ids = []
    texts = []
    metadatas = []

    for document in documents:

        chunks = chunk_document(document["content"])

        for index, chunk in enumerate(chunks):

            ids.append(f'{document["id"]}_chunk_{index}')
            texts.append(chunk)

            metadatas.append({
                "document_id": document["id"],
                "title": document["title"]
            })

    embeddings = ollama.embed(
        model="nomic-embed-text",
        input=texts
    )["embeddings"]

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"Indexed {len(ids)} chunks successfully.")


# if __name__ == "__main__":
#     index_documents(documents)




def retrieve_documents(question, top_k=3):

    # TODO 1: Generate an embedding for the question
    # using nomic-embed-text.
    question_embed = ollama.embed(
        model="nomic-embed-text",
        input=question
    )["embeddings"][0]

    # TODO 2: Search the ChromaDB collection
    # using collection.query().
    retrieved_result = collection.query(
        query_embeddings=question_embed,
        n_results=top_k,
        include=["documents","metadatas","distances"]
    )

    # TODO 3: Retrieve:
    # documents, metadatas, distances, ids.

    # TODO 4: Return the retrieved results.
    return retrieved_result

# question = "Why is my printer showing offline?"

# results = retrieve_documents(question, top_k=3)

# print("Documents:", results["documents"])
# print("Metadata:", results["metadatas"])
# print("Distances:", results["distances"])


def retrieve_context(question, top_k=1):
    results = retrieve_documents(question,top_k)
    # print("Documents:", results["documents"])
    # print("Metadatas:", results["metadatas"])
    chunks = results["documents"][0]
    metadata = results["metadatas"][0]

    context = "\n\n".join(chunks)

    document_ids = list(dict.fromkeys(
        item["document_id"] for item in metadata
    ))

    return context, document_ids



def retrieve_document_ids(question, top_k=1):
    total_chunks = collection.count()
    if total_chunks == 0:
        return []

    results = retrieve_documents(question, top_k=total_chunks)
    metadata = results["metadatas"][0]
    document_ids = list(dict.fromkeys(item["document_id"] for item in metadata))
    return document_ids[:top_k]


