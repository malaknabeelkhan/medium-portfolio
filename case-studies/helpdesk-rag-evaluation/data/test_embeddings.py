import ollama

response = ollama.embed(
    model="nomic-embed-text",
    input="The printer is not printing."
)

print("Number of embeddings:", len(response["embeddings"]))
print("Vector dimensions", len(response["embeddings"][0]))