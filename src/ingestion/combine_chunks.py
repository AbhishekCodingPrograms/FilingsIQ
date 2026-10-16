
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed"
OUTPUT = DATA_DIR / "chunks.json"


def main():
    files = sorted(
        path for path in DATA_DIR.glob("*_chunks.json")
        if path.name != OUTPUT.name
    )

    if not files:
        raise FileNotFoundError(
            "No company chunk files found in data/processed."
        )

    combined = []

    for path in files:
        with path.open("r", encoding="utf-8") as file:
            records = json.load(file)

        if not isinstance(records, list):
            raise ValueError(f"Expected a list in {path.name}")

        combined.extend(records)
        print(f"Loaded {len(records)} chunks from {path.name}")

    with OUTPUT.open("w", encoding="utf-8") as file:
        json.dump(combined, file, ensure_ascii=False, indent=2)

    print("\nCombined chunks:", len(combined))
    print("Saved to:", OUTPUT)


if __name__ == "__main__":
    main()
