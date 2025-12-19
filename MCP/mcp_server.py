from fastmcp import FastMCP
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure root directory is in path so we can import local modules
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from Preprocessing.preprocessing import fetch_and_process_data
import app
from Mail_SMTP import mail

# Initialize FastMCP server
mcp = FastMCP("NewsLens AI")

@mcp.tool()
def fetch_latest_news(limit: int = 3) -> str:
    """
    Fetches the latest news from BBC, CNN, and YouTube.
    Args:
        limit: Number of articles to fetch per source (default 3).
    """
    try:
        # Note: We'd need to modify fetch_and_process_data to accept limit
        # For now, we'll use the default or a fixed limit if the function allows it.
        # Let's assume we can pass it or just use the default for now to avoid breaking preprocessing.py
        data = fetch_and_process_data() 
        return json.dumps(data[:limit*3], indent=2) # Simple trimming for now
    except Exception as e:
        return f"Error fetching news: {str(e)}"

@mcp.tool()
def summarize_news_data(news_json: str) -> str:
    """
    Summarizes the provided news JSON using the Groq-powered AI pipeline.
    Expects a JSON string containing a list of articles with 'title' and 'content'.
    """
    try:
        articles = json.loads(news_json)
        summarized = []
        
        # We can use the existing chain from app.py
        from app import chain
        
        for article in articles:
            print(f"Summarizing: {article.get('title')}")
            summary = chain.invoke({
                "title": article.get('title', 'No Title'),
                "content": article.get('content', 'No Content')
            })
            
            # Simple cleaning as done in app.py
            clean_summary = summary.strip()
            prefixes = ["Here is a summary", "Here's a summary", "The following is a summary", "Summary:"]
            for prefix in prefixes:
                if clean_summary.lower().startswith(prefix.lower()):
                    clean_summary = clean_summary[len(prefix):].strip().lstrip(":").strip()

            summarized.append({
                "source": article.get('source', 'Unknown'),
                "title": article.get('title', 'No Title'),
                "summary": clean_summary
            })
        
        # Save to file as expected by mailer
        output_filename = "summarized_news.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(summarized, f, indent=2, ensure_ascii=False)
            
        return json.dumps(summarized, indent=2)
    except Exception as e:
        return f"Error summarizing news: {str(e)}"

@mcp.tool()
def send_news_brief_email() -> str:
    """
    Sends the current summarized news brief (from summarized_news.json) via email.
    """
    try:
        mail.main()
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {str(e)}"

@mcp.resource("news://latest")
def get_latest_summarized_news() -> str:
    """
    Returns the contents of summarized_news.json if it exists.
    """
    try:
        if os.path.exists("summarized_news.json"):
            with open("summarized_news.json", "r", encoding="utf-8") as f:
                return f.read()
        return "No summarized news found. Run summarize_news_data first."
    except Exception as e:
        return f"Error reading news: {str(e)}"

if __name__ == "__main__":
    mcp.run()
