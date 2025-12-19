import os
import sys
import json
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure we can import from local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import our cleaning pipeline
from Preprocessing.preprocessing import fetch_and_process_data

# ==========================================
# CONFIGURATION
# ==========================================
# Ensure you have set the GROQ_API_KEY environment variable.
# You can set it via terminal: $env:GROQ_API_KEY="your_key"
# Or hardcode it here (not recommended for production).
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ==========================================
# LANGSMITH CONFIGURATION
# ==========================================
# Set these in your environment or .env file
# export LANGCHAIN_TRACING_V2=true
# export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
# export LANGCHAIN_API_KEY="your_langchain_api_key"
# export LANGCHAIN_PROJECT="news-agent-summarizer"

if os.environ.get("LANGCHAIN_TRACING_V2") == "true":
    if not os.environ.get("LANGCHAIN_API_KEY"):
         print("WARNING: LANGCHAIN_TRACING_V2 is true but LANGCHAIN_API_KEY is missing.")
    else:
         print(">>> LangSmith Tracing Enabled.")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY environment variable not found.")
    print("Please set it, or the LLM call will fail.")

# Initialize the Groq Chat Model
# Using 'mixtral-8x7b-32768' or 'llama3-70b-8192' as commonly available powerful models on Groq.
llm = ChatGroq(
    temperature=0,
    model_name="llama-3.1-8b-instant", 
    groq_api_key=GROQ_API_KEY
)

# Define the summarization prompt
summarize_prompt = ChatPromptTemplate.from_template(
    """
    You are a helpful news assistant.
    Summarize the following news content into strictly 3-4 lines.
    Capture the key points clearly.
    
    IMPORTANT: Return ONLY the summary text. Do not start with "Here is a summary" or similar phrases.

    Title: {title}
    Content: {content}

    Summary:
    """
)

# Create a chain
# Input: {"title": ..., "content": ...} -> Model -> Output (Str)
chain = summarize_prompt | llm | StrOutputParser()

def main():
    print(">>> PART 1: Fetching and Preprocessing Data...")
    articles = fetch_and_process_data()
    
    if not articles:
        print("No articles found to summarize.")
        return

    print(f"\n>>> PART 2: Summarizing {len(articles)} Articles using Groq LLM...")
    
    final_results = []
    
    for idx, article in enumerate(articles, start=1):
        try:
            print(f"\n[{idx}/{len(articles)}] Summarizing: {article['title']}")
            
            # Invoke the chain
            summary = chain.invoke({
                "title": article['title'],
                "content": article['content']
            })
            
            # Cleaning potential chatty prefixes if the model ignores the system prompt
            clean_summary = summary.strip()
            # Simple heuristic to remove common prefixes if they still appear
            prefixes = ["Here is a summary", "Here's a summary", "The following is a summary", "Summary:"]
            for prefix in prefixes:
                if clean_summary.lower().startswith(prefix.lower()):
                    clean_summary = clean_summary[len(prefix):].strip().lstrip(":").strip()

            # Update the article dictionary
            processed_article = {
                "source": article['source'],
                "title": article['title'],
                "summary": clean_summary
            }
            
            final_results.append(processed_article)
            
            # Print immediately for feedback
            print(f"Summary: {clean_summary}\n")
            print("-" * 50)
            
        except Exception as e:
            print(f"[ERROR] Could not summarize article: {e}")

    # Optional: Save to a JSON file
    output_filename = "summarized_news.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Summarized {len(final_results)} articles.")
    print(f"Results saved to {output_filename}")

if __name__ == "__main__":
    main()
