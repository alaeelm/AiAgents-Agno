import os
import streamlit as st
from textwrap import dedent
from typing import Iterator
from agno.models.google import Gemini
from agno.workflow import Workflow
from agno.agent import Agent, RunResponse
from agno.utils.pprint import pprint_run_response
from agno.tools.googlesearch import GoogleSearchTools


gemini_key = os.environ["GOOGLE_API_KEY"]

client = Gemini(api_key=gemini_key)

# OCR the pdf and return the text
def ocr_pdf(pdf_path):
    # check if the file exists
    if not os.path.exists(pdf_path):
        st.error("PDF file not found")
        return
    
    uploaded_pdf = client.files.upload(
        file={
            "file_name": pdf_path,
            "content": open(pdf_path, "rb"),
        },
        purpose="ocr"
    )

    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)

    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url.url,
        },
        include_image_base64=True
    )

    with open("ocr_response.md", "w") as f:
        f.write("\n".join([page.markdown for page in ocr_response.pages]))

    return ocr_response.pages

# Main Agents Workflow
class ResearchAnalystWorkflow(Workflow):
    # Targeted report structure (Golden structure)
    structure_and_analysis_agent: Agent = Agent(
        name = 'Structure and Analysis Agent',
        model=Gemini(id='gemini-1.5-flash'),
        instructions = dedent("""
        You are an intelligent document analysis agent. You are given the raw text of a PDF (OCR processed). Your task is to analyze the content and produce a structured summary of the document’s subject, key points, and organization. The report discusses a specific country, which you must identify.
        Follow these steps:

        1. Detect and clearly state the COUNTRY being discussed (call this "Country X").
        2. Identify the MAIN TOPIC of the document (e.g. energy policy, health care reforms, education quality).
        3. Define the DOCUMENT STRUCTURE as a clean numbered outline with sections and subsections based on the logical flow of the text.
        4. Extract the KEY ENTITIES, KEY FIGURES (if any), and any important ORGANIZATIONS or AGENCIES mentioned.
        5. Summarize the KEY POINTS and INSIGHTS under each major section, focusing on the data, trends, problems, or conclusions made about Country X.

        Output format:

        COUNTRY: <Country X>
        TOPIC: <main subject of the document>

        STRUCTURE:
        1. <Section Title>
        - <Summary or bullet points>
        2. <Section Title>
        - <Summary or bullet points>
        ...

        KEY POINTS AND INSIGHTS:
        - Bullet points summarizing major findings, arguments, statistics, etc.
        - Must reflect what is emphasized in the document
        - Keep this detailed but concise

        This output will be used by a second agent to replicate a similar report for a different country. Be clear, complete, and well-structured.
        """),
    )

    def run(self, ocr_text: str, user_country: str) -> Iterator[RunResponse]:
        analysis_response: Iterator[RunResponse] = self.structure_and_analysis_agent.run(ocr_text)
        if analysis_response is None or not analysis_response.content:
            yield RunResponse(
                run_id=self.run_id,
                content="Sorry, could not get the analysis report.",
            )
            return

        reasearch_agent: Agent = Agent(
        name = 'Research Agent',
        model=Gemini(id='gemini-1.5-flash'),
        instructions = dedent(f"""
        You are a research agent. You are given a structured summary of a document about a topic in a specific country. Your task is to generate a new report on the **same topic** but focused on COUNTRY: {user_country}.

        You may use the GoogleSearchTools() tool to search for real-world information related to Country {user_country}.

        Instructions:

        1. Read the input summary carefully. It contains:
        - COUNTRY: <Country X>
        - TOPIC: <Main Topic>
        - STRUCTURE: <Numbered outline of the report>
        - KEY POINTS AND INSIGHTS from the original document

        2. Understand the structure and content focus. Your output must use **the same section headings** and address **the same themes**, but for **Country {user_country}**.

        3. For each section, use GoogleSearchTools() to find reliable and up-to-date information specific to Country {user_country}. For example:
        - Local policies
        - Trends
        - Statistics
        - Institutional efforts
        - Challenges and opportunities
        - Relevant events

        4. Rebuild the report using the exact structure, now filled with data and insights from Country {user_country}. The tone, depth, and organization should match the original as closely as possible.

        Output format:

        TITLE: <Same topic> in <Country {user_country}>

        1. <Section Title from original>
        - <Findings related to Country {user_country}>
        2. <Next Section>
        - <Continue same structure>

        Cite or refer to sources found via search where helpful.

        IMPORTANT: You must always stay exactly within the subject defined in the original document. Do not go broader, do not narrow the scope, and do not add or remove themes. Reproduce the same structure and content areas, adapted only to Country {user_country}. Nothing more, nothing less.
        """),
        tools=[GoogleSearchTools()],
        )
        yield from reasearch_agent.run(analysis_response.content, stream=True)

# Main function
if __name__ == "__main__":
    ocr_text = ""
    user_country = ""
    pdf_path = ""
    st.title("Research Analyst Multi-Agent System")
    with st.form("input_form"):
        pdf_path = st.file_uploader("Upload a PDF file", type=["pdf"])
        user_country = st.text_input("Enter your desired research country")
        submitted = st.form_submit_button("Submit")
    if submitted and pdf_path and user_country:
        with st.spinner("Processing PDF..."):
            # save the pdf locally
            with open(f'UploadedPDF/{pdf_path.name}', "wb") as f:
                f.write(pdf_path.read())
            st.success("PDF file uploaded successfully")        
            ocr_pdf(f'UploadedPDF/{pdf_path.name}')
            # read the ocr_response.md file
            with open("ocr_response.md", "r") as f:
                ocr_text = f.read()
            st.success("OCR completed successfully")
        with st.spinner("Running research workflow..."):
            # run the workflow
            workflow = ResearchAnalystWorkflow()
            # Display a placeholder for streaming
            output_placeholder = st.empty()
            full_output = ""
            # Run the workflow and stream the output
            response: Iterator[RunResponse] = workflow.run(ocr_text=ocr_text, user_country=user_country)
            for run_response in response:
                if run_response.content:
                    full_output += run_response.content
                    output_placeholder.markdown(full_output)
    else:
        st.write("No PDF file uploaded")