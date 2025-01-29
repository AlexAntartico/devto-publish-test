import json
import re
import yaml
import sys

def extract_front_matter(md_file):
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

def md_to_devto(md_file):
    front_matter_data, body_markdown = extract_front_matter(md_file)

    if 'title' not in front_matter_data or 'tags' not in front_matter_data:
        # Is there a better way to not repeat double not in?
        raise ValueError("Title is required in front matter")

    article_json = {
        "article": {
            "title": front_matter_data['title'],
            "body_markdown": body_markdown,
            "tags": front_matter_data['tags'],
            "published": front_matter_data['published']
        }
    }

    return json.dumps(article_json)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python publish_script.py <path_to_markdown_file>")
        sys.exit(1)

    md_file = sys.argv[1]
    try:
        formatted_article = md_to_devto(md_file)
        print(formatted_article)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


