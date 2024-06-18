import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import ollama
import uuid
import os
from pathlib import Path

# Database setup
DATABASE_URL = "sqlite:///urls.db"  # Database URL for SQLite
Base = declarative_base()  # Base class for SQLAlchemy models

# Define a model for storing URL records
class URLRecord(Base):
    __tablename__ = 'urls'  # Name of the table in the database
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))  # Unique identifier for each record
    url = Column(String, unique=True, nullable=False)  # URL (must be unique and not null)
    heading = Column(String)  # Page heading
    summary = Column(Text)  # Summary of the page content
    tags = Column(Text)  # Tags extracted from the content

# Create the database and the URLRecord table
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Class to interact with the Ollama LLM
class LlmClient:
    def __init__(self, ollama_instance_url: str, model: str):
        self.ollama_instance_url = ollama_instance_url  # URL of the Ollama instance
        self.model = model  # Model to use for generation
        self.client = ollama.Client(host=ollama_instance_url)  # Initialize the Ollama client
        
        # API call options
        self.client_options = {
            # Uncomment and set values as needed
            # "num_ctx": 8000,
            # "temperature": 0.7,
            # "top_k": 40,
            # "top_p": 0.9,
        }

        # Load system prompt from file
        self.prompt_templates_dir = Path(__file__).parent / "prompts"
        self.system_prompt = ""
        system_prompt_path = self.prompt_templates_dir / "system.j2"
        if system_prompt_path.exists():
            with open(system_prompt_path, "r") as file:
                self.system_prompt = file.read()

    # Get a response from the LLM for a given input
    def get_llm_response(self, input: str = ""):
        response = self.client.generate(
            model=self.model,
            options=self.client_options,
            system=self.system_prompt,
            prompt=input,
        )
        output = response["response"]  # Extract the response content
        output = self.clean_output(output)  # Clean the output (remove any unwanted tokens)
        return output

    # Get a streamed response from the LLM for a given input
    def get_llm_response_stream(self, input: str = ""):
        response = self.client.generate(
            model=self.model,
            options=self.client_options,
            system=self.system_prompt,
            prompt=input,
            stream=True,
        )

        for chunk in response:
            output = chunk["response"]  # Extract the chunk content
            output = self.clean_output(output)  # Clean the output
            yield output

    # Clean the output by removing unwanted tokens
    def clean_output(self, output: str) -> str:
        ending_token = ""
        output = output.replace(ending_token, "")
        return output

# Remove tracking parameters from the URL
def strip_tracking(url):
    parsed_url = urlparse(url)  # Parse the URL into components
    query = parse_qs(parsed_url.query)  # Parse the query parameters
    query = {k: v for k, v in query.items() if not k.startswith(('amp_', 'precache_', 'utm_'))}  # Remove tracking parameters
    stripped_query = urlencode(query, doseq=True)  # Re-encode the query parameters
    stripped_url = parsed_url._replace(query=stripped_query)  # Replace the query part of the URL
    return urlunparse(stripped_url)  # Reconstruct the URL

# Fetch the content of the URL
def fetch_url_data(url):
    try:
        response = requests.get(url)  # Make a GET request to the URL
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')  # Parse the HTML content with BeautifulSoup
            text = soup.get_text()  # Extract the text content
            return text, soup  # Return the text content and the BeautifulSoup object
        else:
            print(f"Failed to retrieve the URL. Status code: {response.status_code}")
            return None, None
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None, None

# Summarise the text using Ollama
def summarise_with_ollama(llm_client, text):
    try:
        # Structured prompt for summarisation
        prompt = f"Concisely summarise web page information and descriptive SEO keywords and tags: \n\n{text[:2000]}"
        response = llm_client.get_llm_response(prompt)  # Get the response from Ollama
        
        # Simulating a structured response with summary and tags
        lines = response.split('\n')
        summary = lines[0]
        tags = ', '.join(set(word for word in response.split() if word.isalpha() and len(word) > 3))  # Extract tags
        short_summary = summary[:200] + '...' if len(summary) > 200 else summary  # Truncate the summary
        return short_summary, tags
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None, None

# Process a single URL
def process_url(llm_client, url):
    stripped_url = strip_tracking(url)  # Remove tracking parameters
    existing_record = session.query(URLRecord).filter_by(url=stripped_url).first()  # Check if the URL is already processed
    
    if existing_record:
        print(f"URL already processed: {stripped_url}")
        return False

    text, soup = fetch_url_data(stripped_url)  # Fetch the content of the URL
    
    if text and soup:
        heading = soup.title.string if soup.title else "No title found"  # Extract the page heading
        summary, tags = summarise_with_ollama(llm_client, text)  # Summarise the content
        
        if summary:
            # Create a new record and save it to the database
            new_record = URLRecord(url=stripped_url, heading=heading, summary=summary, tags=tags)
            session.add(new_record)
            session.commit()
            print(f"URL: {stripped_url}")
            print(f"Heading: {heading}")
            print(f"Summary: {summary}")
            print(f"Tags: {tags}")
            return True
        else:
            print("Failed to summarise text with Ollama.")
            return False
    else:
        print("Failed to fetch URL data.")
        return False

# Main function to process a list of URLs from a file
def main():
    llm_client = LlmClient(ollama_instance_url="http://localhost:11434", model="mistral:latest")  # Initialize the LLM client
    
    # Read URLs from the file
    with open("bmurllist.txt", "r") as file:
        urls = file.readlines()

    # Get already processed URLs from the database
    processed_urls = set(record.url for record in session.query(URLRecord.url).all())
    broken_urls = []

    # Process each URL
    for url in urls:
        url = url.strip()
        if url and url not in processed_urls:
            success = process_url(llm_client, url)
            if not success:
                broken_urls.append(url)  # Add to broken URLs list if processing fails
            processed_urls.add(url)  # Add to processed URLs set
    
    # Write broken URLs to a file
    with open("broken_urls.txt", "w") as file:
        for url in broken_urls:
            file.write(url + "\n")

if __name__ == "__main__":
    main()

