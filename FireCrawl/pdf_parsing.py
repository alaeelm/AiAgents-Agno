import logging
import os
from agno.agent import Agent
from agno.models.google import Gemini
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Récupérer les clés directement depuis .env
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Firecrawl
firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

# Initialize Agno Agent
agent = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=GOOGLE_API_KEY),
    system_message="You are a professional summarizer. Read documents carefully and give concise summaries."
)

# Crawl PDF URL
url_to_crawl = "https://www.pwc.com/gx/en/issues/analytics/assets/pwc-ai-analysis-sizing-the-prize-report.pdf"
response = firecrawl.crawl(url=url_to_crawl)
output_data = dict(response)

# Log raw content
pdf_text_content = output_data.get("data")
logging.info("PDF Raw Text Extracted.")

# Generate summary using Agno Agent
if pdf_text_content:
    summary = agent.print_response(
        f"Summarize the following PDF content:\n\n{pdf_text_content[:20000]}", 
        stream=True
    )
else:
    logging.warning("No content extracted from the PDF.")
