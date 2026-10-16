
import streamlit as st

from src.agent.basic_rag import answer_question

st.set_page_config(
    page_title="FilingsIQ",
    page_icon="📊",
    layout="wide",
)

st.title("📊 FilingsIQ")
st.caption("AI-powered SEC 10-K filing research assistant")

with st.sidebar:
    st.header("Research settings")
    company = st.selectbox(
        "Company filter",
        ["All companies", "Apple", "Microsoft", "NVIDIA"],
    )
    st.info("Verify important findings against the original SEC filing.")

question = st.text_area(
    "Ask your research question",
    placeholder="Compare Apple's and Microsoft's business risks.",
    height=120,
)

if st.button("Research", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Searching filings and generating your answer..."):
                result = answer_question(question, company)

            st.subheader("Research answer")

            verification = result["verification"]
            invalid_citations = result["invalid_citations"]

            if verification.get("overall_status") == "PASS" and not invalid_citations:
                st.success("Verification checks passed")
            else:
                st.warning("Draft — needs review")

            st.markdown(result["answer"])

            st.divider()
            st.subheader("Citation reference check")

            if invalid_citations:
                st.error(f"Unknown citations: {', '.join(invalid_citations)}")
            else:
                st.success("All cited source numbers exist.")

            st.subheader("Claim verification")
            st.write("Status:", verification.get("overall_status", "REVIEW"))

            if verification.get("error"):
                st.caption(f"Verifier detail: {verification['error']}")

            for finding in verification.get("findings", []):
                with st.expander(finding.get("claim", "Verification finding")):
                    st.write("Status:", finding.get("status", "UNCLEAR"))
                    st.write(finding.get("reason", ""))

            st.divider()
            st.subheader("SEC filing sources")

            for source in result["sources"]:
                st.markdown(
                    f"**[Source {source['number']}] "
                    f"{source['company']}** · {source['filing_date']}"
                )

                if source.get("url"):
                    st.markdown(f"[Open original SEC filing]({source['url']})")

                with st.expander("View retrieved excerpt"):
                    st.write(source.get("excerpt", ""))

        except Exception as exc:
            st.error(f"Research failed: {exc}")
            st.info(
                "Check the PowerShell terminal for details. "
                "Your existing terminal RAG script remains unchanged."
            )
