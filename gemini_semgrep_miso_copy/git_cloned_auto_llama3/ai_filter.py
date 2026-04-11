import requests
import json

def is_valid_repo_ai(repo):
    """
    Ollama(llama3:8b)를 사용하여 레포지토리가 고품질의 오픈소스 프로젝트인지 한 번 더 확인합니다.
    """
    url = "http://localhost:11434/v1/chat/completions"
    
    repo_name = repo.get("full_name", "N/A")
    description = repo.get("description", "No description provided")
    topics = ", ".join(repo.get("topics", []))
    
    prompt = f"""
    You are a security researcher assistant. Analyze if this GitHub repository is a real-world web application or API service (NOT a tutorial, library, framework, CLI tool, or data analysis project).

    Repo Name: {repo_name}
    Description: {description}
    Topics: {topics}

    Criteria for YES:
    - It is an actual web application, API server, or web service
    - It likely has attack surfaces such as: user authentication, database queries, file uploads, API endpoints, user input handling
    - It is a standalone deployable project, not a reusable library or package

    Criteria for NO:
    - It is a tutorial, awesome-list, learning resource, or boilerplate template
    - It is a library/framework/SDK meant to be imported by other projects
    - It is a CLI tool, desktop app, or data science project with no web interface

    Answer ONLY 'YES' or 'NO'. No other text.
    """
    
    payload = {
        "model": "llama3:8b",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        ai_answer = result['choices'][0]['message']['content'].strip().upper()
        
        if ai_answer.startswith("YES"):
            print(f"[AI 합격] {repo_name}")
            return True
        else:
            print(f"[AI 탈락] {repo_name} (사유: AI 판단 기준 미달)")
            return False
            
    except Exception as e:
        print(f"[AI 오류] {repo_name} 평가 중 오류 발생: {e}")
        # 오류 발생 시 기본적으로 True를 반환하여 메타데이터 필터링 결과에 따름 (또는 False로 보수적 처리 가능)
        return True
