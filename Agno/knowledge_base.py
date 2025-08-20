from agno.agent import Agent
from agno.models.google import Gemini
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()


pdf = PdfReader("PDF/pwc-ai-analysis.pdf")
full_text = "".join(page.extract_text() or "" for page in pdf.pages)
def always_return_full_pdf(agent, query, num_documents=None, **kwargs):
    """
    This function is used to return the full text of a PDF document
    regardless of the query or number of documents requested.
    """
    global full_text
    # Return the full text of the PDF as a single document
    return [{
        "content": full_text,
        "meta_data": {"source": "pwc-ai-analysis.pdf"}
    }]  


# Initialize the agent with the PDF retriever
agent = Agent(
    model=Gemini(id="gemini-2.0-flash"),
    knowledge=None,
    search_knowledge=True,
    retriever=always_return_full_pdf,
)

prompt = input("Enter Your Prompt: ")
agent.print_response(prompt)
