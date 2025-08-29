import os
import streamlit as st
from agno.team import Team
from textwrap import dedent
from pypdf import PdfReader
from agno.agent import Agent
from agno.models.google import Gemini


st.title("AI Contract Reviewer")
st.write(
    "This is a tool that uses AI to review contracts and provide insights "
    "and suggestions on their structure, legality, and negotiability."
)

uploaded_file = st.file_uploader("Upload a contract", type=["pdf"])
full_text, file_name = "", "unknown.pdf"

if uploaded_file:
    file_name = uploaded_file.name
    reader = PdfReader(uploaded_file)
    full_text = "".join(page.extract_text() or "" for page in reader.pages)
    if not full_text:
        st.error("No text found in the contract.")
        st.stop()


def get_document():
    return [{"content": full_text, "meta_data": {"source": file_name}}]


with st.sidebar:
    api_key = st.text_input("GOOGLE API Key", key="chatbot_api_key", type="password")
    "Enter your Google API key. Get it from https://developers.google.com/generative-ai."


# -------------------------------
# Define a function to build agents only when API key is set
# -------------------------------
def build_agents(api_key: str):
    os.environ["GOOGLE_API_KEY"] = api_key

    # Structure Agent
    structure_agent = Agent(
        model=Gemini(id="gemini-1.5-flash"),
        name="Structure Agent",
        role="Contract Structuring Expert",
        instructions=dedent("""
            You are a Contract Structuring Expert. Your role is to evaluate the structure of a contract 
            and suggest improvements or build a proper structure from scratch if not provided, 
            following best legal and business practices.
            Use the tool `get_document` to retrieve the full contract text.
            Be concise but clear in your analysis.
            Output markdown structure if creating a new structure, 
            or bullet-point comments if evaluating.
        """),
        tools=[get_document],
        show_tool_calls=False,
        markdown=True,
    )

    # Legal Agent
    legal_agent = Agent(
        model=Gemini(id="gemini-1.5-flash"),
        name="Legal Agent",
        role="Legal issue Analyst",
        instructions=dedent("""
            You are a Legal Framework Analyst tasked with identifying legal issues in the contract.
            Use the `get_document` tool to access the contract.
            For every issue:
            - Quote the clause
            - Provide 'Issue:' explanation
            - Mention section or location
            Format:
            📄 Clause:
            "Quoted text"
            📍 Section: [...]
            ⚠️ Issue: Explanation
        """),
        tools=[get_document],
        show_tool_calls=False,
        markdown=True,
    )

    # Negotiation Agent
    negotiate_agent = Agent(
        model=Gemini(id="gemini-1.5-flash"),
        name="Negotiation Agent",
        role="Contract Negotiation Strategist",
        instructions=dedent("""
            You are a Contract Negotiation Strategist.
            Identify negotiable/unbalanced clauses.
            Must:
            - Quote exact clause
            - Explain why negotiable
            - Suggest counter-offer
            Format:
            1. **Quoted clause**
            2. **Why negotiable/problematic**
            3. **Counter-suggestion**
        """),
        tools=[get_document],
        show_tool_calls=False,
        markdown=True,
    )

    # Manager Agent
    manager_agent = Team(
        members=[structure_agent, legal_agent, negotiate_agent],
        model=Gemini(id="gemini-1.5-flash"),
        mode="coordinate",
        success_criteria=dedent("""
            A clear summary including:
            - Legal context with quoted text
            - Structure feedback
            - Negotiation strategies
        """),
        instructions=dedent("""
            You are the lead summarizer. Combine inputs from:
            - Legal Agent
            - Structure Agent
            - Negotiation Agent
            Requirements:
            - Keep quoted clauses
            - Summarize clearly
            - Avoid redundancy
            Final format:
            • Executive Summary
            • Legal Context
            • Structure Feedback
            • Negotiation Recommendations
            • Final Remarks
        """),
        add_datetime_to_instructions=False,
        show_tool_calls=False,
        markdown=True,
        enable_agentic_context=True,
        show_members_responses=False,
    )

    return manager_agent


# -------------------------------
# Button action
# -------------------------------
if st.button("Review Contract"):
    if not api_key:
        st.error("Please enter your Google API Key.")
        st.stop()
    if not uploaded_file:
        st.error("Please upload a contract first.")
        st.stop()

    # Build manager agent after key is set
    manager_agent = build_agents(api_key)

    output = ""
    placeholder = st.empty()

    with st.spinner("Analyzing..."):
        try:
            for event in manager_agent.run(
                message="Please analyze this contract by providing legal context, evaluating its structure, "
                        "and identifying negotiable terms. Combine the insights into a single summary.",
                stream=True,
            ):
                if (
                    hasattr(event, "event")
                    and event.event == "TeamRunResponseContent"
                    and hasattr(event, "content")
                    and event.content
                ):
                    output += event.content
                    placeholder.markdown(output)

            if output:
                st.download_button("Download Report", output, file_name="contract_review.md")

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
