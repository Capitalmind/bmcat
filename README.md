# bmcat
Bookmark Cataloguing
# URL Databasing Project

This project provides a tool for fetching, summarizing, and storing information about web pages. It uses the Ollama library for generating summaries and tags, SQLAlchemy for database management, and BeautifulSoup for HTML parsing.

## Features

- Fetches web page content from a list of URLs.
- Removes tracking parameters from URLs.
- Summarizes the content using the Ollama LLM.
- Extracts and stores the page heading, summary, and tags.
- Handles already processed URLs to avoid duplication.
- Logs broken URLs to a separate file.

## Installation

### Prerequisites

- Python 3.8+
- `ollama` library installed
- `requests`, `beautifulsoup4`, `sqlalchemy`, `ollama` Python packages

### Install Python Packages

```bash
pip install requests beautifulsoup4 sqlalchemy ollama
