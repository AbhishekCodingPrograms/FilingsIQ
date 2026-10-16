
import json
from pathlib import Path

import chromadb
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DB_DIR = PROJECT_ROOT / "chroma_db"

CHUNKS_PATH = PROCESSED_DIR / "chunks.json"
EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"
METADATA_PATH = PROCESSED_DIR / "embedding_metadata.json"

COLLECTION_NAME = "filingsiq_10k"


def load_chunks() -> list[dict]:
    chunk_files = sorted(PROCESSED_DIR.glob("*_chunks.json"))
    if not chunk_files and CHUNKS_PATH.is_file():
        chunk_files = [CHUNKS_PATH]
    if not chunk_files:
        raise FileNotFoundError(
            f"No chunk files found in {PROCESSED_DIR}. "
            "Run src/retrieval/chunk_filings.py first."
        )

    chunks = []
    for path in chunk_files:
        with path.open("r", encoding="utf-8") as file:
            file_chunks = json.load(file)
        if not isinstance(file_chunks, list):
            raise ValueError(f"Expected a JSON list of chunks in {path}")
        for index, chunk in enumerate(file_chunks):
            if not isinstance(chunk, dict) or not isinstance(chunk.get("text"), str):
                raise ValueError(f"Invalid chunk at index {index} in {path}")
            if not isinstance(chunk.get("metadata"), dict):
                raise ValueError(f"Missing chunk metadata at index {index} in {path}")
            chunks.append(chunk)
    return chunks


def main():
    chunks = load_chunks()

    with METADATA_PATH.open("r", encoding="utf-8") as file:
        metadata_records = json.load(file)

    embeddings = np.load(EMBEDDINGS_PATH)

    if not (len(chunks) == len(metadata_records) == len(embeddings)):
        raise ValueError("Chunks, metadata, and embeddings counts do not match.")
    if any(not isinstance(record.get("chunk_id"), str) for record in metadata_records):
        raise ValueError("Every embedding metadata record must contain a chunk_id.")

    client = chromadb.PersistentClient(path=str(DB_DIR))

    # Rebuild this project's collection from the current files.
    # This makes repeated runs deterministic.
    collection_names = {collection.name for collection in client.list_collections()}
    if COLLECTION_NAME in collection_names:
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    batch_size = 100

    for start in range(0, len(chunks), batch_size):
        end = min(start + batch_size, len(chunks))

        batch_chunks = chunks[start:end]
        batch_metadata = metadata_records[start:end]
        batch_embeddings = embeddings[start:end]

        collection.add(
            ids=[metadata["chunk_id"] for metadata in batch_metadata],
            documents=[chunk["text"] for chunk in batch_chunks],
            embeddings=batch_embeddings.tolist(),
            metadatas=[
                {
                    key: value
                    for key, value in metadata.items()
                    if value is not None
                    and isinstance(value, (str, int, float, bool))
                }
                for metadata in batch_metadata
            ],
        )

        print(f"Indexed {end}/{len(chunks)} chunks")

    print("\nVector database created successfully.")
    print("Collection:", COLLECTION_NAME)
    print("Total indexed chunks:", collection.count())
    print("Database location:", DB_DIR)


if __name__ == "__main__":
    main()
