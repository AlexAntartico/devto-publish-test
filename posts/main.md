---
title: "How to upload Markdown files to Dev.to from GitHub"
description: "A short article on how to upload Markdown files from GitHub to Dev.to"
tags:
  - github
  - actions
  - devto
  - automation
published: true
---

# How to upload Markdown files to Dev.to from GitHub

This is a test post to show how to upload Markdown files to Dev.to.

You can do this with:
- GitHub actions
- Dev.to API Token
- A custom GitHub action
- A Python script

I am assuming you have a general knowledge with GitHub actions and Python scripting, but you can achieve this with a superficial knowledge. To know more about it, you can check the [GitHub documentation](https://docs.github.com/en/actions).

## GitHub action to upload Markdown file

You can use GitHub actions to automate the process of uploading Markdown files to Dev.to. Using this action will make your life easier as every time you push a new commit to your repository, the markdown document will be pushed as well. There are already several actions available that can help you with this task or you can create your own action, but why reinvent the wheel?

I did some quick research and initially decided to use this [Publish to dev.to](https://github.com/marketplace/actions/publish-to-dev-to) GitHub action. It's simple to use and gets the job done. Or so I thought, after 2 failed repositories and a bunch of attempts I falled back to the conventional curl POST method. To be fair, is probably due to my lack of knowledge in GitHub actions, but I will try to use it again in the future.

First, fetch your DEV.TO API key. For this, log in to your DEV.TO account and go to settings/extensions, scroll all the way to the bottom and in you will see a section Named "DEV Community API Keys". Name your project and click on "Generate API Key". Copy this key and save it in your GitHub repository secrets.

![Dev.to API Key](https://github.com/AlexAntartico/devto-publish-test/blob/main/images/Screenshot-2025-01-13-3.png?raw=true)

To save the key as a secret. go to your repository settings, click on secrets, and add a new secret with the name `DEVTO_TOKEN` and paste the key you copied from DEV.TO. Ensure you have saved at repository level.

![Repository Settings](https://github.com/AlexAntartico/devto-publish-test/blob/main/images/Screenshot-2025-01-13.png?raw=true)

![Add Secret](https://github.com/AlexAntartico/devto-publish-test/blob/main/images/Screenshot-2025-01-13-2.png?raw=true)

In your repository, create a new file called `.github/workflows/devto_publish.yml` and add the following code that you can [find here.](https://github.com/AlexAntartico/devto-publish-test/blob/main/.github/workflows/devto_publish.yml)

```yaml
name: Publish to Dev.to

on:
  push:
    branches:
      - main
    paths:
      - 'posts/**'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Upgrade pip and Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyyaml requests

    - name: Verify API Key Availability
      env:
        DEVTO_API_KEY: ${{ secrets.DEVTO_API_KEY }}  # Keep existing secret mapping
      run: |
        echo "API key character count: ${#DEVTO_API_KEY}"
        echo "API key empty check: $([ -z "$DEVTO_API_KEY" ] && echo 'Empty' || echo 'Set')"

    - name: Convert md to Dev.to format
      run: |
        python publish_script.py ./posts/main.md > formatted_article.json

    - name: Publish or Update to Dev.to
      env:
        DEVTO_API_KEY: ${{ secrets.DEVTO_API_KEY }}
      run: |
        action=$(jq -r '.action' formatted_article.json)
        article=$(jq -r '.article' formatted_article.json)

        if [ "$action" = "create" ]; then
          response=$(curl -X POST "https://dev.to/api/articles" \
            -H "api-key: $DEVTO_API_KEY" \
            -H "Content-Type: application/json" \
            -d "$article" -w "\n%{http_code}")
        elif [ "$action" = "update" ]; then
          article_id=$(echo $article | jq -r '.id')
          response=$(curl -X PUT "https://dev.to/api/articles/$article_id" \
            -H "api-key: $DEVTO_API_KEY" \
            -H "Content-Type: application/json" \
            -d "$article" -w "\n%{http_code}")
        else
          echo "Invalid action: $action"
          exit 1
        fi

        status_code=$(echo "$response" | tail -n1)
        if [ "$status_code" -ne 200 ] && [ "$status_code" -ne 201 ]; then
          echo "Failed to update article. Status code: $status_code"
          exit 1
        fi
```

## Brief explanation of GitHub action

1. Triggers when there's a push to the main branch that modifies files in the `posts/ directory`
2. Sets up the environment:
  - Runs on `ubuntu-latest`
  - Checks out the repository
  - Configures Python `3.11`
  - Installs required dependencies `pyyaml` and `requests`
3. Performs API key validation by checking its presence and length
4. Executes the publishing process:
  - Converts markdown files to Dev.to format using a Python script
  - Generates a formatted JSON article output
5. Handles article publication:
  - Determines whether to create new or update existing article
  - Makes appropriate API calls to Dev.to - `POST` for new, `PUT` for updates)
  - Includes proper headers and authentication using DEVTO_API_KEY
6. Includes error handling:
  - Validates HTTP response codes
  - Exits with failure if status code isn't `200` or `201`
  - Provides detailed error output for troubleshooting1

## The python script

This Python script handles the conversion and publishing of markdown files to Dev.to. Here's a breakdown of its main components. The script's main purpose is to convert markdown files to Dev.to API format and verify existing articles1

**extract_front_matter Function**
1. Takes a markdown file path as input and returns:
  - A dictionary containing parsed YAML front matter data
  - The markdown body content without the front matter1
2. Handles errors for:
  - Missing files
  - Invalid YAML parsing1
**md_to_devto Function**
3. Accepts:
  - Markdown file path
  - Dev.to API key
  - Returns:
    - JSON string of the article
    - Action string ('create' or 'update')1
4. Key operations:
  - Extracts front matter and body
  - Validates required fields (title, tags)
  - Checks for existing articles
  - Prepares article JSON with title, published status, content, and tags1
**fetch_existing_articles Function**
5. Takes API key as input
  - Returns list of existing articles from Dev.to
  - Raises HTTP errors for failed requests1
6. Main Execution
  - Validates:
    - Command line arguments
    - API key presence
  Outputs:
    - Formatted JSON result with article data and action
    - Error messages to stderr on failure

## Conclusion

The script and GitHub action provided in this article can help you automate the process of uploading markdown files to Dev.to. However, needs to be modified to incorporate more of the error handling in Pyton and create a more robust and maintainable solution. I hope this article helps you in your journey to automate your workflow and make your life easier.

I will create an updated version of this scripts with a new article in the future, so stay tuned for that.

Cheers and happy, happy coding!

Eduardo Mendoza
