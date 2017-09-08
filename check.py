import hashlib

def check_sha1(wait_for_check):
    with open(wait_for_check.path, 'rb') as f:
        data = hashlib.sha1(f.read()).hexdigest()
    if data != wait_for_check.sha1:
        raise ValueError("The given file is cracked.")

def check_libs(check_lists):
    for wait_for_check in check_lists:
        check_sha1(wait_for_check)

def check_assets(check_lists):
    for wait_for_check in check_lists:
        check_sha1(wait_for_check)