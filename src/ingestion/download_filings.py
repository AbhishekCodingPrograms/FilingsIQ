import json
import re
import time

from pathlib import Path
import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


HEADERS = {
    "User-Agent": "FillingsIQ Research Project - abhishekmaurya2104567@gmail.com",
    "Accept-Encoding": "gzip, deflate, br",
}


COMPANIES = {
    'MICROSOFT CORP': '0000789019',
    'APPLE INC': '0000320193',
    'NVIDIA CORP': '0001045810',

}

def get_latest_10k(cik : str)-> dict:
    """find the latest 10k filling using SEC company submission."""
    cik_padded = cik.zfill(10)
    url = (
        "https://data.sec.gov/submissions/"
        f"CIK{cik_padded}.json"
    )

    response = requests.get(url , headers = HEADERS , timeout = 30 )
    response.raise_for_status()
    data = response.json()

    recent = data["filings"]["recent"]

    for i , form in enumerate(recent["form"]):
        if form == "10-K":
            return {
               "cik": cik_padded,
               "company": data["name"],
               "form": form,
               "filing_date": recent["filingDate"][i],
               "accession_number": recent["accessionNumber"][i],
               "primary_document": recent["primaryDocument"][i],

            }
    raise ValueError(f"No 10-K filing found for CIK {cik}")


def download_filing(filing: dict) -> str:
    accession = filing["accession_number"].replace("-", "")
    cik = str(int(filing["cik"]))

    url = (
        "https://www.sec.gov/Archives/edgar/data/"
        f"{cik}/{accession}/{filing['primary_document']}"
    )
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    for tag in soup(["script", "style", "ix:header"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)

    if len(text) < 1000:
        raise ValueError(f"Extracted filing text is unexpectedly short: {url}")
    filing["source_url"] = url
    filing["document_length"] = len(text)
    return text


def main():
    for company, cik in COMPANIES.items():
        try:
            print(f"\nProcessing {company}...")

            filing = get_latest_10k(cik)
            text = download_filing(filing)

            record = {
                "metadata": filing,
                "text": text,
            }

            output_path = RAW_DIR / f"{company.lower()}_10k.json"
            output_path.write_text(
                json.dumps(record, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            print(f"Saved: {output_path}")
            print(f"Filing date: {filing['filing_date']}")
            print(f"Characters extracted: {len(text):,}")

        except (requests.RequestException, ValueError, KeyError) as exc:
            print(f"Failed to process {company}: {exc}")

        # Avoid sending requests too quickly to SEC servers.
        time.sleep(0.2)


if __name__ == "__main__":
    main()