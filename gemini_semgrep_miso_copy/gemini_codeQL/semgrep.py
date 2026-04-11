import subprocess

def prepare_semgrep_scan(clone_path, repo):
    print(f"[+] Preparing Semgrep scan for: {repo['full_name']}")
    # Semgrep은 데이터베이스 생성이 필요 없으므로 경로를 반환합니다.
    return clone_path

def run_semgrep(clone_path):
    print(f"[+] Running Semgrep analysis for: {clone_path}")
    result = subprocess.run(
        ["semgrep", "--config", "auto", clone_path,
         "--output", f"{clone_path}_semgrep.sarif",
         "--format", "sarif"],
        check=True,
        text=True
    )
