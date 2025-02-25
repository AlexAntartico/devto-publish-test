"""
This script converts a markdown file to the format expected by the dev.to API and verifies if an article with the same title already exists.

Functions:
    extract_front_matter(md_file):
        Extracts front matter from a markdown file.
        
    md_to_devto(md_file, api_key):
        Converts a markdown file to the format expected by the dev.to API and verifies if an article with the same title already exists.
        
    fetch_existing_articles(api_key):
        Fetches existing articles from the dev.to API.

Usage:
    python publish_script.py <path_to_markdown_file>

Environment Variables:
    DEVTO_API_KEY: The API key for authentication with the dev.to API.
"""
import json
import re
import yaml
import requests
import sys
import os


def extract_front_matter(md_file):
    """
    Extracts front matter from a markdown file.

    Args:
        md_file (str): The path to the markdown file.

    Returns:
        tuple: A tuple containing two elements:
            - dict: The front matter data parsed from YAML.
            - str: The body of the markdown file without the front matter.

    Raises:
        FileNotFoundError: If the specified markdown file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML front matter.
    """
    with open(md_file, 'r') as f:
        content = f.read()

    front_matter_match = re.search(r'^---\s*([\s\S]*?)\s*---', content, re.MULTILINE)
    if front_matter_match:
        front_matter = front_matter_match.group(1)
        # Load YAML front matter
        front_matter_data = yaml.safe_load(front_matter)
        body_markdown = content[len(front_matter_match.group(0)) + 3:].strip()
        return front_matter_data, body_markdown
    else:
        front_matter_data = {}
        body_markdown = content.strip()
    return front_matter_data, body_markdown[2]

def md_to_devto(md_file, api_key):
    """
    Converts a markdown file to the format expected by the dev.to API and verifies if an article with the same title already exists.

    Args:
        md_file (str): Path to the markdown file.
        api_key (str): API key for authentication with the dev.to API.

    Returns:
        tuple: A tuple containing two elements:
            - str: The JSON string of the article.
            - str: A string indicating whether the article should be 'create' or 'update'.

    Raises:
        ValueError: If required keys ('title', 'tags') are missing in the front matter of the markdown file.
    """
    front_matter_data, body_markdown = extract_front_matter(md_file)

    required_keys = ['title', 'tags']
    missing_keys = [key for key in required_keys if key not in front_matter_data]
    if missing_keys:
        raise ValueError(f"Missing keys in front matter: {', '.join(missing_keys)}")

    # Fetch existing articles
    existing_articles = fetch_existing_articles(api_key)

    # Verify if an article with the same title already exists
    existing_article = next((article for article in existing_articles if article['title'] == front_matter_data['title']), None)

    article_json = {
        "title": front_matter_data['title'],
        "published": front_matter_data.get('published', False),
        "body_markdown": body_markdown,
        "tags": front_matter_data['tags']
    }

    if existing_article:
        article_json['id'] = existing_article['id']
        return json.dumps({"article": article_json}), 'update'
    else:
        return json.dumps({"article": article_json}), 'create'


def fetch_existing_articles(api_key):
    """
    Fetches existing articles from the dev.to API.

    Args:
        api_key (str): The API key used for authentication.

    Returns:
        list: A list of articles fetched from the dev.to API.

    Raises:
        requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
    """
    url = "https://dev.to/api/articles/me"
    headers = {"api-key": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    """
    Verifies if the correct number of arguments are passed and calls the md_to_devto function.
    """
    if len(sys.argv) != 2:
        print("Usage: python publish_script.py <path_to_markdown_file>")
        sys.exit(1)

    md_file = sys.argv[1]
    api_key = os.environ.get('DEVTO_API_KEY')

    if not api_key:
        print("Please set the DEVTO_API_KEY environment variable with your dev.to API key.", file=sys.stderr)
        sys.exit(1)

    try:
        formatted_article, action = md_to_devto(md_file, api_key)
        result = {
            "article": json.loads(formatted_article),
            "action": action
        }
        print(json.dumps(result, indent=4))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
