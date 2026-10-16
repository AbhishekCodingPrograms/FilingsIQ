
import json
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"

MODEL_NAME = "BAAI/bge-small-en-v1.5"


def load_chunks() -> list[dict]:
    chunk_files = sorted(DATA.glob("*_chunks.json"))
    if not chunk_files:
        raise FileNotFoundError(
            f"No per-filing chunk files found in {DATA}. "
            "Run src/retrieval/chunk_filings.py first."
        )

    chunks = []
    for path in chunk_files:
        with path.open(encoding="utf-8") as file:
            file_chunks = json.load(file)
        if not isinstance(file_chunks, list):
            raise ValueError(f"Expected a JSON list of chunks in {path}")

        for index, chunk in enumerate(file_chunks):
            if not isinstance(chunk, dict) or not isinstance(chunk.get("text"), str):
                raise ValueError(f"Invalid chunk at index {index} in {path}")
            metadata = chunk.get("metadata")
            if not isinstance(metadata, dict):
                raise ValueError(f"Missing chunk metadata at index {index} in {path}")

            chunk_index = metadata.get("chunk_index", index)
            chunk["chunk_id"] = (
                f"{metadata.get('cik', 'unknown')}_"
                f"{metadata.get('accession_number', path.stem)}_"
                f"{chunk_index}"
            )
            chunks.append(chunk)
    return chunks


def main():
    chunks = load_chunks()
    if not chunks:
        raise ValueError(f"No chunks found in {DATA}")

    print("Loading FastEmbed model:", MODEL_NAME)
    model = TextEmbedding(model_name=MODEL_NAME)

    texts = [chunk["text"] for chunk in chunks]

    print(f"Embedding {len(texts)} chunks...")
    vectors = np.asarray(
        list(model.embed(texts)),
        dtype=np.float32,
    )

    DATA.mkdir(parents=True, exist_ok=True)
    np.save(DATA / "embeddings.npy", vectors)

    metadata = [
        {
            **chunk["metadata"],
            "chunk_id": chunk["chunk_id"],
        }
        for chunk in chunks
    ]

    with (DATA / "embedding_metadata.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print("Embedding shape:", vectors.shape)
    print("Embeddings saved successfully.")


if __name__ == "__main__":
    main()
