import json
import re
import yaml
import requests

def extract_front_matter(md_file):
    with open(md_file, 'r') as f:
        content = f.read()

    front_matter_match = re.search(r'^---\s*([\s\S]*?)\s*---', content, re.MULTILINE)
    if front_matter_match:
        front_matter = front_matter_match.group(1)
        # Load YAML front matter
        front_matter_data = yaml.safe_load(front_matter)
        body_markdown = content[len(front_matter_match.group(0)) + 2:].strip()
        return front_matter_data, body_markdown
    else:
        raise ValueError("No front matter found in markdown file")

def md_to_devto(md_file):
    front_matter_data, body_markdown = extract_front_matter(md_file)

    if 'title' not in front_matter_data or 'tags' not in front_matter_data:
        # Is there a better way to not repeat double not in?
        raise ValueError("Title is required in front matter")

    article_json = {
        "article": {
            "title": front_matter_data['title'],
            "published": True,
            "body_markdown": body_markdown,
            "tags": front_matter_data['tags']
        }

    }

    return json.dumps(article_json)


if __name__ == "__main__":
    md_file = "posts/main.md"
    formatted_article = md_to_devto(md_file)
    print(formatted_article)

