# bmcat
Bookmark Cataloguing
# URL Databasing Project

This project provides a tool for fetching, summarizing, and storing information about web pages from bookmark URLs. It uses the Ollama library for generating summaries and tags, SQLAlchemy for database management, and BeautifulSoup for HTML parsing.

## Features

- Fetches web page content from a list of URLs.
- Removes tracking parameters from URLs.
- Summarizes the content using the Ollama LLM.
- Extracts and stores the page heading, summary, and tags.
- Handles already processed URLs to avoid duplication.
- Logs broken URLs to a separate file.

## Installation

- ollama from https://ollama.com/
- ollama pull 'model' from https://ollama.com/library/[models]
- pip install ollama (to interact with ollama)
- configure localhost:port in app.py to ensure they match local machine serving ollama, typically localhost:11434
- export bookmarks from browser and strip urls with shell script included

### Prerequisites

- Python 3.8+
- `ollama` library installed
- `requests`, `beautifulsoup4`, `sqlalchemy`, `ollama` Python packages

### Install Python Packages

```bash
pip install requests beautifulsoup4 sqlalchemy ollama

Setup Ollama
Ensure Ollama is running and accessible. Refer to the Ollama GitHub Repository for installation instructions.

Usage
Clone the Repository

bash
Copy code
git clone https://github.com/yourusername/url-databasing.git
cd url-databasing
Prepare the URL List

Create a file named bmurllist.txt in the project directory and add the URLs you want to process, each on a new line.

Create a Prompts Directory

Create a directory named prompts in the project directory and add a file named system.j2 with your system prompt.

Run the Script

bash
Copy code
python ollamatest.py
Configuration
LLM Client Options
The LlmClient class allows you to configure the options for the Ollama API calls. You can set these options in the client_options dictionary within the LlmClient class.

System Prompt
The system prompt is loaded from a file named system.j2 in the prompts directory. Ensure this file exists and contains your desired prompt.

Project Structure
bash
Copy code
url-databasing/
│
├── bmurllist.txt         # Bookmark URL List to process
├── broken_urls.txt       # Log of broken URLs
├── ollamatest.py         # Main script
├── prompts/
│   └── system.j2         # System prompt for Ollama
└── urls.db               # SQLite database (auto-generated)
Example
Here is an example of the content of bmurllist.txt:

Copy code
https://www.example.com
https://www.anotherexample.com
And an example system prompt in prompts/system.j2:

Copy code
Please summarize the following content and extract tags.
Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub.

License
This project is licensed under the MIT License. See the LICENSE file for details.
