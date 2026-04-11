import requests
import time
import json
import os

PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "search_progress.json")
PAGES_PER_RUN = 10

def _load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"last_page": 0}

def _save_progress(last_page):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"last_page": last_page}, f)

def search_github_repositories():
    progress = _load_progress()
    start_page = progress["last_page"] + 1
    end_page = start_page + PAGES_PER_RUN - 1

    print(f"[검색 범위] page {start_page} ~ {end_page}")

    url = "https://api.github.com/search/repositories"

    headers = {
        "Accept": "application/vnd.github.mercy-preview+json"
    }

    keywords = ["web application", "web app", "rest api", "web server", "web platform", "admin dashboard", "web portal"]
    seen = set()
    all_repos = []

    for page in range(start_page, end_page + 1):
        for keyword in keywords:
            params = {
                "q": f"{keyword} language:python stars:100..2000",
                "sort": "updated",
                "order": "desc",
                "per_page": 30,
                "page": page
            }

            response = requests.get(url, params=params, headers=headers)

            # rate limit 걸리면 대기
            if response.status_code == 403:
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                wait = max(reset_time - int(time.time()), 60)
                print(f"[Rate Limit] {wait}초 대기 중...")
                time.sleep(wait)
                response = requests.get(url, params=params, headers=headers)

            data = response.json()

            for repo in data.get("items", []):
                if repo["id"] not in seen:
                    seen.add(repo["id"])
                    all_repos.append(repo)

            # API 호출 간격 (rate limit 방지)
            time.sleep(3)

        print(f"[검색 완료] page {page} - 누적 {len(all_repos)}개 레포지토리 후보 발견")

    _save_progress(end_page)
    print(f"[진행 저장] 다음 실행 시 page {end_page + 1}부터 시작")
    return all_repos
