import sys, requests, json
sys.path.insert(0, ".")
from src.auth import get_headers
from src.config import BASE_URL

headers = get_headers()
headers["api-id"] = "kt00018"

resp = requests.post(
    f"{BASE_URL}/api/dostk/acnt",
    headers=headers,
    json={"qry_tp": "1", "dmst_stex_tp": "KRX"},
    timeout=10,
)
print(f"상태: {resp.status_code}")
print(json.dumps(resp.json(), indent=2, ensure_ascii=False)[:1000])
