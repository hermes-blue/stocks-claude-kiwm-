import time
import requests
from src.auth import get_headers
from src.logger import log
from src.config import BASE_URL

PRICE_ENDPOINT = "/api/dostk/mrkcond"


def _parse_price(val) -> int:
    return abs(int(str(val).replace("+", "").replace(",", "").replace(" ", "") or 0))


def _parse_rate(val) -> float:
    try:
        return float(str(val).strip())
    except Exception:
        return 0.0


def fetch_price(stock_code: str) -> dict | None:
    """
    종목 1개 현재가 조회 (ka10007).
    반환: {"code": "005930", "current": 75000, "change_rate": -1.23}
    실패 시 None 반환 (재시도 없음).
    """
    headers = get_headers()
    headers["api-id"] = "ka10007"

    if not headers.get("authorization", "").startswith("Bearer "):
        log(f"[시세] {stock_code} 조회 실패 - 토큰 없음")
        return None

    try:
        resp = requests.post(
            f"{BASE_URL}{PRICE_ENDPOINT}",
            headers=headers,
            json={"stk_cd": stock_code},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        current = _parse_price(data.get("cur_prc", "0"))
        change_rate = _parse_rate(data.get("flu_rt", "0"))

        log(f"[시세] {stock_code} | 현재가: {current:,}원 | 등락률: {change_rate:+.2f}%")
        return {"code": stock_code, "current": current, "change_rate": change_rate}

    except Exception as e:
        log(f"[시세] {stock_code} 조회 실패 - {e} (넘어감)")
        time.sleep(1)
        return None
