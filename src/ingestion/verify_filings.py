
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

print("Looking for filings in:", RAW_DIR)

files = list(RAW_DIR.glob("*_10k.json"))
print("Files found:", len(files))

if not files:
    print("No JSON files found. Check the data/raw folder.")

for path in files:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        metadata = record["metadata"]
        text = record["text"]

        print("\n" + "=" * 50)
        print("File:", path.name)
        print("Company:", metadata["company"])
        print("Filing date:", metadata["filing_date"])
        print("Text length:", f"{len(text):,} characters")
        print("Preview:", text[:250], "...")

    except (json.JSONDecodeError, KeyError, OSError) as exc:
        print(f"Error reading {path.name}: {exc}")
