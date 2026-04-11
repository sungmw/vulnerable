def file_R_to_Set():
    with open('check_repo_list.txt', 'r') as file:
        alr_scanned_repo = {line.strip() for line in file}
    return alr_scanned_repo

def file_W_end_scan(end_scan_repo):
    print(f"[+] file write scanned repo : {end_scan_repo} ")
    already_scanned = file_R_to_Set()
    if end_scan_repo not in already_scanned:
        with open('check_repo_list.txt', 'a') as file:
            file.write(end_scan_repo + '\n')