# GitHub API configuration
GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
SEARCH_PARAMS = {
    "q": "stars:10000..146000 pushed:>2025-01-01 language:Javascript",
    "sort": "stars", 
    "order": "desc", 
    "per_page": 30
}
page = 1

# Gemini API configuration
# GEMINI_API_KEY = "input your key"
Model = 'gemini-2.5-flash'

# Clone Repo configuration
# PATH = "input path"

# Notion API configuration
NOTION_API_TOKEN = "input your token"
DB_ID = "input id"
NOTION_API_VERSION = "2022-06-28"
