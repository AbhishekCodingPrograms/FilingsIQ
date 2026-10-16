import json
from pathlib import Path
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def chunk_filing(record: dict[str, Any]) -> list[dict[str, Any]]:
    metadata = record.get("metadata")
    text = record.get("text")
    if not isinstance(metadata, dict):
        raise ValueError("Filing record must contain a metadata object.")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Filing record must contain non-empty text.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_text(text)
    return [
        {
            "metadata": {**metadata, "chunk_index": index},
            "text": chunk,
        }
        for index, chunk in enumerate(chunks)
    ]


def process_filing(input_path: Path, output_dir: Path = PROCESSED_DIR) -> Path:
    record = json.loads(input_path.read_text(encoding="utf-8"))
    chunks = chunk_filing(record)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{input_path.stem}_chunks.json"
    output_path.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    input_paths = sorted(RAW_DIR.glob("*_10k.json"))
    if not input_paths:
        raise FileNotFoundError(f"No filing JSON files found in {RAW_DIR}")

    for input_path in input_paths:
        output_path = process_filing(input_path)
        chunk_count = len(json.loads(output_path.read_text(encoding="utf-8")))
        print(f"Created {chunk_count} chunks: {output_path}")


if __name__ == "__main__":
    main()
