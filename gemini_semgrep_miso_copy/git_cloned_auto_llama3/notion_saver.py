import os
import requests
import datetime

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "너님 토큰넣어요 여기에")

# 위에서 생성한 데이터베이스 ID
DATABASE_ID = "e640fdd1362a4d23998a4c9f36c90e6a"


def _already_exists(repo_name, headers):
    """Notion DB에 같은 이름의 레포가 이미 있는지 확인합니다."""
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": "Name",
            "title": {"equals": repo_name}
        }
    }
    try:
        resp = requests.post(query_url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200 and resp.json().get("results"):
            return True
    except Exception:
        pass
    return False


def save_to_notion(repo, status="Cloned"):
    """
    클론된 레포지토리 정보를 Notion 데이터베이스에 저장합니다.
    status: "Cloned", "Skipped", "Failed"
    """
    if not NOTION_TOKEN:
        print("[Notion] NOTION_TOKEN이 설정되지 않았습니다. notion_saver.py에서 토큰을 설정하세요.")
        return False

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }

    repo_name = repo.get("full_name", "Unknown")
    if _already_exists(repo_name, headers):
        print(f"[Notion] 이미 존재: {repo_name} (중복 스킵)")
        return True

    today = datetime.date.today().isoformat()

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": repo.get("full_name", "Unknown")}}
                ]
            },
            "URL": {
                "url": repo.get("html_url", "")
            },
            "Stars": {
                "number": repo.get("stargazers_count", 0)
            },
            "Language": {
                "rich_text": [
                    {"text": {"content": repo.get("language", "N/A") or "N/A"}}
                ]
            },
            "Description": {
                "rich_text": [
                    {"text": {"content": (repo.get("description", "") or "")[:2000]}}
                ]
            },
            "Clone Date": {
                "date": {"start": today}
            },
            "Status": {
                "select": {"name": status}
            },
        },
    }

    try:
        response = requests.post(NOTION_API_URL, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            print(f"[Notion] 저장 완료: {repo.get('full_name')}")
            return True
        else:
            print(f"[Notion] 저장 실패 ({response.status_code}): {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[Notion] 오류: {e}")
        return False
