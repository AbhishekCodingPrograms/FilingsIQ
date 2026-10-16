
from pathlib import Path

import chromadb
from fastembed import TextEmbedding

ROOT = Path(__file__).resolve().parents[2]
DB_DIR = ROOT / "chroma_db"

COLLECTION_NAME = "filingsiq_10k"
MODEL_NAME = "BAAI/bge-small-en-v1.5"


def main():
    client = chromadb.PersistentClient(path=str(DB_DIR))

    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception as exc:
        raise RuntimeError(
            "ChromaDB collection not found. "
            "Run build_vector_db.py first."
        ) from exc

    print("Indexed chunks:", collection.count())

    if collection.count() == 0:
        print("The collection is empty. Build the index first.")
        return

    print("Loading FastEmbed model...")
    model = TextEmbedding(model_name=MODEL_NAME)

    print("\nFilingsIQ Semantic Search")
    print("Type 'exit' to quit.")

    while True:
        question = input("\nAsk a question: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            continue

        query_vector = list(model.query_embed(question))[0]

        results = collection.query(
            query_embeddings=[query_vector.tolist()],
            n_results=5,
            include=["documents", "metadatas", "distances"],
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        if not documents:
            print("No relevant passages found.")
            continue

        print("\nRetrieved passages:")

        for i, (document, metadata, distance) in enumerate(
            zip(documents, metadatas, distances),
            start=1,
        ):
            print("\n" + "=" * 65)
            print(f"Result {i}")
            print("Company:", metadata.get("company", "Unknown"))
            print("Filing date:", metadata.get("filing_date", "Unknown"))
            print("Distance:", round(distance, 4))
            print("Source:", metadata.get("source_url", "Unavailable"))
            print("\nPassage:")
            print(document[:1200])


if __name__ == "__main__":
    main()
