import os
import time
from dotenv import load_dotenv
load_dotenv()

from github_search import search_github_repositories
from filters import is_valid_repo
from ai_filter import is_valid_repo_ai
from cloner import clone_repo
from notion_saver import save_to_notion

# 진행 상황 저장 파일 경로 (main.py와 같은 폴더에 생성)
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_page.txt")
PAGES_PER_RUN = 10  # 한 번 실행할 때 몇 페이지씩 돌릴지

def load_start_page():
    """last_page.txt에서 마지막으로 끝난 페이지를 읽어와서 다음 시작 페이지를 반환"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            last_page = int(f.read().strip())
            return last_page + 1
    return 1  # 파일이 없으면 첫 실행이므로 1부터

def save_last_page(page):
    """현재까지 완료한 마지막 페이지 번호를 저장"""
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(page))

def main():
    start_page = load_start_page()
    end_page = start_page + PAGES_PER_RUN - 1  # 10페이지씩

    print(f"\n🚀 이번 실행: {start_page}페이지 ~ {end_page}페이지")
    print(f"   (변경하려면 last_page.txt를 수정하거나 삭제하세요)\n")

    page = start_page

    while page <= end_page:
        print(f"\n{'='*50}")
        print(f"[라운드 {page}] 검색 시작...")
        print(f"{'='*50}")

        repos = search_github_repositories(page=page)

        if not repos:
            print("[완료] 더 이상 검색 결과가 없습니다.")
            break

        for repo in repos:
            # 1차 필터링: 메타데이터 기반
            if is_valid_repo(repo):
                # 2차 필터링: Ollama AI 기반
                if is_valid_repo_ai(repo):
                    success = clone_repo(repo)
                    # Notion에 저장
                    if success:
                        save_to_notion(repo, status="Cloned")
                    else:
                        save_to_notion(repo, status="Failed")
                else:
                    print(f"[Skip] AI 탈락: {repo['full_name']}")
                    save_to_notion(repo, status="Skipped")

        # 완료한 페이지 바로 저장 (중간에 꺼져도 이어서 가능)
        save_last_page(page)

        page += 1
        if page <= end_page:
            print(f"\n[대기] 다음 페이지 검색까지 30초 대기...")
            time.sleep(30)

    print(f"\n[종료] {start_page}~{end_page}페이지 검색 완료!")
    print(f"📌 다음 실행 시 {end_page + 1}페이지부터 이어서 진행됩니다.")

main()
