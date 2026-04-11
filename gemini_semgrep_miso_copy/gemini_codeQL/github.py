import requests
import json
from config import GITHUB_SEARCH_URL, SEARCH_PARAMS, PATH
from file import file_R_to_Set, file_W_end_scan
import subprocess
import os

def search_repo(page):
    print("[+] Searching for target repositories")
    SEARCH_PARAMS["page"] = page
    res = requests.get(GITHUB_SEARCH_URL, params=SEARCH_PARAMS).json()
    return res

def parse_repo_data(res):
    print("[+] Parsing repository data")
    repo_list = {}
    if "items" not in res:
        return repo_list
    already_scanned = file_R_to_Set()
    for item in res["items"]:
        if item["full_name"] in already_scanned:
            continue
        full_name = item["full_name"]
        repo_list[full_name] = {
            "full_name": item["full_name"],
            "description": item["description"],
            "language": item["language"],
            "clone_url": item["clone_url"],
            "html_url": item["html_url"]
        }
    print(repo_list)
    return repo_list

def is_Clone_valid(repos):
    print("[+] Filtering repositories based on Gemini's analysis")
    target_repo = []
    for repo in repos:
        if repo["is_suitable"]==True:
            target_repo.append(repo["full_name"])
    return target_repo

def git_clone(repo_data):
    print(f"[+] Cloning repository: {repo_data['full_name']}")
    clone_url = repo_data["clone_url"]
    clone_path = f"{PATH}/Repo/"
    name = repo_data["full_name"].replace("/", "_")
    project_path = os.path.join(clone_path, name)
    print(project_path)
    result = subprocess.run(
        ["git", "clone", "--depth", "1", clone_url, project_path], 
        check=True
    )
    return project_path