import json
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from google import genai
from google.genai import errors as genai_errors
from config import GEMINI_API_KEY, Model

MAX_RETRIES = 5
INITIAL_WAIT = 10  # seconds

def ask_gemini_for_target(repo_list):
    print("[+] Asking Gemini to identify suitable repositories...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    repo_data_str = json.dumps(repo_list)
    
    prompt = f"""
    너는 오픈소스 보안 취약점을 전문으로 하는 수석 보안 연구원이야.
    Semgrep 정적 분석으로 실제 CVE급 취약점(RCE, SSRF, SQLi, Path Traversal, Auth Bypass)을
    발견할 가능성이 높은 리포지토리를 선별해줘. 
    그리고 해당 프로젝트의 이름, 설명으로만 판단하지말고 실제 웹 서칭을 통해 
    프로젝트 구조, 기능, 사용자 입력이 어떻게 처리되는지, 어떤 기능을 하는 오픈 소스인지 꼼꼼히 분석해서 판단해줘. 
    프로젝트 이름이랑 설명으로만 판단하기엔 힘들다고 생각해. 꼭 웹 서칭을 병행해서 분석해줘.

    [필수 조건 - 하나라도 미충족 시 false]
    1. 메인 언어가 Python, JavaScript, TypeScript, Java, Go 중 하나일 것
    2. 라이브러리/프레임워크 자체가 아닌, 독립 배포 가능한 서버/앱/플랫폼일 것
    - 제외 예시: flask, django, fastapi (이것들은 "도구"이지 앱이 아님)
    - 포함 예시: 이 도구들을 이용해 만들어진 AI 플랫폼, 워크플로우 빌더, 웹 앱 등

    [공격 표면 판단 기준 - 이렇게 취약점이 잘 발견될 만한 구조를 갖췄는지 판단. 이것 말고도 다른 공격 표면이 있을 수 있음]
    A. 코드 실행 표면: 사용자 입력이 서버에서 코드/명령으로 실행될 수 있는 구조
    (예: Python Executor 노드, LLM 에이전트, 커스텀 스크립트 실행 기능)
    B. SSRF 표면: 사용자가 서버 측에서 요청할 URL/endpoint를 직접 지정 가능
    (예: webhook 설정, 외부 API 연동, 모델 URL 직접 입력)
    C. 파일시스템 접근: 파일 업로드, 경로 설정, 모델 로드 등
    D. 자체 인증/인가 구현: 외부 auth 라이브러리 의존 없이 자체 구현한 경우
    E. 성숙도 부족 시그널: 최근 1~2년 내 급성장한 AI/LLM 툴, 보안 정책 문서 부재
    F. 복합 공격 표면: API + 파일업로드 + 외부연동 + 코드실행이 동시에 존재

    [판단 예시]
    - flowise: true → 워크플로우 빌더, 노드에서 JS 코드 실행, 외부 API 연동
    - langflow: true → Python 코드 실행 노드, 서버 앱, AI 플랫폼
    - onlook: true → Electron 앱, 코드 직접 조작, 파일시스템 접근
    - flask: false → 프레임워크(도구), 앱이 아님
    - django: false → 프레임워크(도구), 앱이 아님  
    - langchain: false → 라이브러리, 그 자체로 배포 서버가 아님
    - youtube-dl: false → CLI 도구, 서버 공격 표면 없음

    [출력 형식]
    반드시 아래 JSON 배열로만 응답. 마크다운/설명 절대 금지.
    full_name은 입력 데이터의 full_name 필드를 그대로 사용 필수. 무조건이야 너 마음대로 바꾸면 안돼. 절대.
    [
    {{
        "full_name": "full_name",
        "is_suitable": true 또는 false,
        "reason": "한 줄 근거 (어떤 공격 표면이 있는지 또는 왜 제외인지)"
    }}
    ]

    [분석할 GitHub 데이터]
    {repo_data_str}
    """

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=Model, 
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            
            try:
                parsed_result = json.loads(response.text)
                print(parsed_result)
                return parsed_result
            except json.JSONDecodeError:
                print("🚨 JSON 파싱 에러 발생! 응답 원본:", response.text)
                return []

        except (genai_errors.ServerError, genai_errors.ClientError) as e:
            wait_time = INITIAL_WAIT * (2 ** (attempt - 1))
            print(f"⚠️ Gemini API 에러 (시도 {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                print(f"⏳ {wait_time}초 후 재시도...")
                time.sleep(wait_time)
            else:
                print("🚨 최대 재시도 횟수 초과. 이 페이지를 건너뜁니다.")
                return []