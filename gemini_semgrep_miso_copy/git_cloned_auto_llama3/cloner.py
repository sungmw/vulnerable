import os
import subprocess

def clone_repo(repo):
    clone_url = repo["clone_url"]
    
    # cloner.py 파일이 있는 위치를 기준으로 cloned_repos 폴더 경로 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cloned_repos_dir = os.path.join(base_dir, "cloned_repos")
    
    # 폴더 생성 (이미 있으면 무시)
    os.makedirs(cloned_repos_dir, exist_ok=True)
    
    # 레포지토리 이름 추출
    repo_name = clone_url.rstrip('/').split('/')[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
        
    target_path = os.path.join(cloned_repos_dir, repo_name)
    
    # 이미 클론된 폴더가 없다면 클론 진행 (타겟 경로 직접 지정)
    if not os.path.exists(target_path):
        result = subprocess.run(["git", "clone", "--depth", "1", clone_url, target_path])
        return result.returncode == 0
    else:
        print(f"이미 클론된 레포지토리입니다: {repo_name}")
        return True
