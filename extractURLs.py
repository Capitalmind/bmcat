import re
import requests
from pathlib import Path
import fnmatch

# Define the desktop path and current directory path
desktop_path = Path.home() / "Desktop"
current_directory_path = Path.cwd()

# Function to check if a URL is valid
def check_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        pass
    return False

# Function to find Bookmark*.html files in a given directory (case-insensitive)
def find_bookmark_files(directory):
    files = directory.glob("*")
    bookmark_files = [file for file in files if fnmatch.fnmatch(file.name.lower(), "bookmark*.html")]
    return bookmark_files

# Function to prompt the user to select a file
def select_file(files):
    print("Multiple bookmark files found:")
    for i, file in enumerate(files):
        print(f"{i + 1}: {file.name}")
    while True:
        try:
            choice = int(input("Select a file by number: ")) - 1
            if 0 <= choice < len(files):
                return files[choice]
        except ValueError:
            pass
        print("Invalid choice, please try again.")

# Function to extract URLs from a file
def extract_urls(file_path):
    urls = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # Extract URLs using a more precise regex and clean them
            found_urls = re.findall(r'(https?://[^\s"<>]+)', line)
            cleaned_urls = [url.strip('"').strip("'") for url in found_urls]
            urls.extend(cleaned_urls)
    return urls

# Function to process URLs
def process_urls(urls, test_urls):
    valid_urls = []
    broken_urls = []
    for url in urls:
        if test_urls:
            if check_url(url):
                valid_urls.append(url)
            else:
                broken_urls.append(url)
        else:
            valid_urls.append(url)
    return valid_urls, broken_urls

# Main function
def main():
    # First check the current directory for Bookmark*.html files
    bookmark_files = find_bookmark_files(current_directory_path)

    # If no bookmark files are found, check the desktop
    if not bookmark_files:
        bookmark_files = find_bookmark_files(desktop_path)

    if not bookmark_files:
        input_file = input("No Bookmark*.html files found. Please provide the path to the file: ")
        input_file = Path(input_file)
    elif len(bookmark_files) == 1:
        input_file = bookmark_files[0]
    else:
        input_file = select_file(bookmark_files)

    # Ask the user whether to test URLs
    test_urls = input("Do you want to test if URLs are alive or dead? (yes/no): ").strip().lower() == 'yes'

    # Extract URLs from the selected file
    urls = extract_urls(input_file)
    valid_urls, broken_urls = process_urls(urls, test_urls)

    # Define output file paths
    valid_urls_file = "valid_urls.txt"
    broken_urls_file = "broken_urls.txt"

    # Save valid and broken URLs to files
    with open(valid_urls_file, "w") as f:
        f.write("\n".join(valid_urls))
    if test_urls:
        with open(broken_urls_file, "w") as f:
            f.write("\n".join(broken_urls))

    print(f"Valid URLs saved to {Path(valid_urls_file).resolve()}")
    if test_urls:
        print(f"Broken URLs saved to {Path(broken_urls_file).resolve()}")

if __name__ == "__main__":
    main()

