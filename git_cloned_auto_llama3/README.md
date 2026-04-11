# Vuln - GitHub Repository Auto Collector for Security Research

GitHub에서 보안 분석(정적 분석)에 적합한 중소 규모 오픈소스 웹 애플리케이션을 자동으로 검색, 필터링, 클론하는 도구입니다.

## 목표

- SonarQube, Snyk 등 정적분석 도구로 취약점/버그를 탐지
- 실제 취약점 확인 후 CVE 작성 또는 제보

## 구조

```
main.py              # 실행 진입점 (page 1~10 자동 순회)
├── github_search.py # GitHub API 키워드 검색 (7개 키워드 × 페이지별 30개)
├── filters.py       # 1차 필터 - 메타데이터 기반
├── ai_filter.py     # 2차 필터 - Ollama(llama3:8b) AI 판단
└── cloner.py        # git clone --depth 1 으로 클론
```

## 필터링 파이프라인

```
GitHub API 검색 (~2,100개 후보)
    │
    ▼
1차 필터 (filters.py)
    - 별 100~2,000개 (중소 규모)
    - fork / archived 제외
    - 언어: Python, Go, JavaScript, TypeScript
    - 최근 3개월 내 활동
    │
    ▼
2차 필터 (ai_filter.py)
    - Ollama(llama3:8b)가 판단
    - 실제 웹앱/API 서비스인가?
    - 공격 표면(인증, DB, 파일업로드 등)이 있는가?
    - 튜토리얼/라이브러리/CLI 도구 제외
    │
    ▼
클론 (cloner.py)
    - cloned_repos/ 폴더에 저장
    - 이미 클론된 레포는 건너뜀
```

## 실행 방법

### 사전 준비

```bash
# Ollama 설치 및 모델 다운로드
ollama pull llama3:8b

# Python 의존성 설치
pip install requests
```

### 실행

```bash
# Ollama 실행 (별도 터미널)
ollama serve

# 메인 스크립트 실행
python3 main.py
```

## 설정 변경

- `github_search.py` - 검색 키워드, 별 범위, 페이지 수 조절
- `filters.py` - 별 상한/하한, 언어, 활동 기간 변경
- `ai_filter.py` - AI 프롬프트 수정으로 선별 기준 변경
- `main.py` - `max_page` 값으로 검색 깊이 조절
