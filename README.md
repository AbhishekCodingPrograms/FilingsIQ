# 📊 FilingsIQ

**AI-Powered SEC 10-K Filing Research Assistant**

FilingsIQ is a Retrieval-Augmented Generation (RAG) application that helps users research company risks using SEC Form 10-K filing excerpts. It retrieves relevant passages, generates answers with source references, and provides a claim-verification status.

## Features

- Semantic search over SEC filing excerpts
- Company-specific research for Apple, Microsoft, and NVIDIA
- Comparative business-risk analysis
- LLM-powered answers using Groq
- Local vector database using ChromaDB
- Fast embeddings using FastEmbed
- Citation-reference validation
- Claim-verification workflow
- Streamlit web interface with SEC source links

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| User interface | Streamlit |
| LLM inference | Groq API |
| Embeddings | FastEmbed |
| Vector database | ChromaDB |
| Data source | SEC Form 10-K filings |

## Architecture

1. User submits a research question.
2. FilingsIQ identifies mentioned companies.
3. FastEmbed generates a query embedding.
4. ChromaDB retrieves relevant filing excerpts.
5. Groq generates an evidence-grounded answer.
6. Citation references are checked.
7. The claim verifier evaluates the answer.
8. The interface displays the answer, verification status, and SEC links.

## Supported Companies

- Apple Inc.
- Microsoft Corporation
- NVIDIA Corporation

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/AbhishekCodingPrograms/FilingsIQ.git
cd FilingsIQ
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the dependencies listed in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file:

```text
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_supported_groq_model
```

Never commit `.env` or expose API keys.

### 5. Prepare the local data

Download and process the SEC filings, generate embeddings, and populate the ChromaDB collection using the project's ingestion scripts.

The database and data files must exist before running the application.

### 6. Run the application

```powershell
streamlit run app.py
```

## Verification and Limitations

- Citation-reference validation checks whether cited source numbers exist.
- Claim verification is an LLM-assisted check, not a guarantee of factual correctness.
- Answers may require manual review, especially when retrieved excerpts are incomplete.
- Missing evidence does not prove that a company has no corresponding risk.
- Consult the original SEC filing before relying on research conclusions.

## Security

- Keep API credentials in environment variables or deployment secrets.
- Do not commit `.env`, virtual environments, or private credentials.
- Review the SEC source material and generated answers before using them for decisions.

## Disclaimer

FilingsIQ is an educational research project. It is not investment, legal, or financial advice.

## Author

Abhishek Maurya
