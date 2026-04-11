import datetime

def is_valid_repo(repo):
    # 1. 만약(if) 레포지토리의 별(stargazers_count) 개수가 100개 미만이라면
    # False(거짓/탈락)를 반환합니다. (즉, 인기가 없는 레포는 거릅니다)
    if repo["stargazers_count"] < 100:
        return False

    # 별이 너무 많은 대형 프로젝트는 이미 보안팀이 관리 중이므로 제외
    if repo["stargazers_count"] > 2000:
        return False
        
    # 2. 만약 이 레포지토리가 남의 것을 복사해온 포크(fork) 버전이라면
    # False를 반환합니다. (순수한 오리지널 원본 레포지토리만 남기기 위함입니다)
    if repo["fork"] == True:
        return False
        
    # 3. 만약 이 레포지토리가 더 이상 관리되지 않고 보관(archived) 처리된 상태라면
    # False를 반환합니다. (현재 활발하게 업데이트되는 레포만 남기기 위함입니다)
    if repo["archived"] == True:
        return False
        
    # 4. 언어 필터링: 웹 관련 언어(Python, Go, JavaScript, TypeScript)만 합격!
    valid_languages = ["Python", "Go", "JavaScript", "TypeScript"]
    if repo.get("language") not in valid_languages:
        return False
        
    # 5. 활동 흔적 필터링: 최근 3개월(90일) 내에 무언가 업데이트(push) 된 기록이 있는지 확인
    pushed_at_str = repo.get("pushed_at")
    if pushed_at_str:
        # 깃허브에서 준 시간 문자열(예: '2023-10-01T12:00:00Z')을 파이썬이 계산할 수 있는 '시간'으로 변환
        pushed_date = datetime.datetime.strptime(pushed_at_str, "%Y-%m-%dT%H:%M:%SZ")
        
        # 지금 현재 시간에서 90일을 뺀 '3개월 전 날짜'를 타임머신처럼 계산합니다.
        three_months_ago = datetime.datetime.utcnow() - datetime.timedelta(days=90)
        
        # 업데이트된 날짜가 3개월 전 날짜보다 더 옛날(작다면)이라면 방치된 것이므로 탈락!
        if pushed_date < three_months_ago:
            return False
            
    # 위 까다로운 장애물을 모두 무사히 통과했다면!
    # 최종적으로 True(참/합격)를 반환합니다. 여기서 합격해야만 다운로드가 진행됩니다.
    return True