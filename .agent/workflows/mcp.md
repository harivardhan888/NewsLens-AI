---
description: How to run and use the NewsLens AI MCP Server
---

# NewsLens AI MCP Workflow

This workflow explains how to run the NewsLens AI project as an MCP (Model Context Protocol) server.

## 1. Installation
Ensure you have the required dependencies installed:
// turbo
```bash
pip install -r requirements.txt
```

## 2. Configuration
Make sure your `.env` file is configured with the following:
- `GROQ_API_KEY`: For news summarization.
- `GMAIL_USER` & `GMAIL_APP_PASSWORD`: For sending emails.
- `RECIPIENT_EMAILS`: Comma-separated list of emails.

## 3. Running the MCP Server
You can run the MCP server using Python. This will start the server in Stdio mode.
// turbo
```bash
python mcp_server.py
```

## 4. Using with Claude Desktop
To use these tools in Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "newslens-ai": {
      "command": "python",
      "args": ["C:/Users/HARI VARDHAN REDDY/Downloads/Newslens_AI/mcp_server.py"],
      "env": {
        "GROQ_API_KEY": "...",
        "GMAIL_USER": "...",
        "GMAIL_APP_PASSWORD": "...",
        "RECIPIENT_EMAILS": "..."
      }
    }
  }
}
```

## 5. Available Tools
- `fetch_latest_news`: Scrapes BBC, CNN, and YouTube.
- `summarize_news_data`: Summarizes the raw news using AI.
- `send_news_brief_email`: Sends the summarized brief via email.

## 6. Available Resources
- `news://latest`: Access the latest summarized news JSON.
