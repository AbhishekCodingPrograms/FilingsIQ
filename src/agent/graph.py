from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph


class FilingsIQState(TypedDict, total=False):
    question: str
    companies: list[str]
    documents: list[str]
    answer: str
    sources: list[dict[str, Any]]
    citation_check: str
    verification_status: str
    error: str


def detect_companies(state: FilingsIQState) -> dict:
    """Identify companies mentioned in the user's question."""
    question = state["question"].lower()

    company_aliases = {
        "Apple": ["apple", "aapl"],
        "Microsoft": ["microsoft", "msft"],
        "NVIDIA": ["nvidia", "nvda"],
    }

    companies = [
        company
        for company, aliases in company_aliases.items()
        if any(alias in question for alias in aliases)
    ]

    return {"companies": companies}


def retrieve_documents(state: FilingsIQState) -> dict:
    """Placeholder for the existing ChromaDB retrieval function."""
    return {"documents": []}


def generate_answer(state: FilingsIQState) -> dict:
    """Placeholder for the existing Groq answer-generation function."""
    return {"answer": ""}


def verify_answer(state: FilingsIQState) -> dict:
    """Placeholder for citation and claim verification."""
    return {
        "citation_check": "NOT_RUN",
        "verification_status": "REVIEW",
    }


builder = StateGraph(FilingsIQState)

builder.add_node("detect_companies", detect_companies)
builder.add_node("retrieve_documents", retrieve_documents)
builder.add_node("generate_answer", generate_answer)
builder.add_node("verify_answer", verify_answer)

builder.add_edge(START, "detect_companies")
builder.add_edge("detect_companies", "retrieve_documents")
builder.add_edge("retrieve_documents", "generate_answer")
builder.add_edge("generate_answer", "verify_answer")
builder.add_edge("verify_answer", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({
        "question": "Compare Apple and Microsoft business risks."
    })

    print("Detected companies:", result["companies"])
    print("Verification status:", result["verification_status"])
