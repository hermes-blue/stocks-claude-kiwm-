import sys
sys.path.insert(0, ".")
from src.auth import get_token, get_headers

t = get_token()
if t:
    print(f"토큰 OK: {t[:30]}...")
    print(f"헤더 키 목록: {list(get_headers().keys())}")
else:
    print("FAIL")
