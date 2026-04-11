from github import search_repo, parse_repo_data, is_Clone_valid, git_clone
from ask_gemini import ask_gemini_for_target
from semgrep import prepare_semgrep_scan, run_semgrep
from file import file_R_to_Set, file_W_end_scan
from notion_api import Insert_notoionDB
from config import page

def main(page):
    search_repo_list = search_repo(page)
    repo_data = parse_repo_data(search_repo_list)
    gemini_answers = ask_gemini_for_target(repo_data)
    target_repos = is_Clone_valid(gemini_answers)
    for repo_name in target_repos:
        try:
            clone_path = git_clone(repo_data[repo_name])
            clone_path = prepare_semgrep_scan(clone_path, repo_data[repo_name])
            run_semgrep(clone_path)
            Insert_notoionDB(repo_name, repo_data[repo_name]['html_url']) 
        
        except Exception as e:
                    print(f"🚨 Error occurred while processing {repo_name}: {e}")
        
        finally:
            file_W_end_scan(repo_name)

if __name__ == "__main__":
    while True:
        main(page)
        page += 1