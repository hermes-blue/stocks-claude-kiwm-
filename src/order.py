import time
import requests
from src.auth import get_headers
from src.config import BASE_URL, ACCOUNT_NO, DRY_RUN

ORDER_ENDPOINT = "/api/dostk/ordr"
BALANCE_ENDPOINT = "/api/dostk/acnt"


def _to_int(val: str) -> int:
    return int(str(val).replace("+", "").replace("-", "").strip() or 0)


def _to_float(val: str) -> float:
    try:
        return float(str(val).strip())
    except Exception:
        return 0.0


def buy_market(code: str, qty: int) -> bool:
    """시장가 매수. 성공하면 True 반환."""
    if DRY_RUN:
        print(f"[DRY_RUN] 매수 — {code} {qty}주 (실제 주문 미전송)")
        return True

    headers = get_headers()
    headers["api-id"] = "kt10000"

    try:
        resp = requests.post(
            f"{BASE_URL}{ORDER_ENDPOINT}",
            headers=headers,
            json={
                "dmst_stex_tp": "KRX",
                "stk_cd": code,
                "ord_qty": str(qty),
                "ord_uv": "",
                "trde_tp": "3",
                "cond_uv": "",
            },
            timeout=10,
        )
        resp.raise_for_status()
        print(f"[주문] 매수 완료 — {code} {qty}주")
        return True
    except Exception as e:
        print(f"[주문] 매수 실패 — {code}: {e}")
        time.sleep(1)
        return False


def sell_market(code: str, qty: int, reason: str = "") -> bool:
    """시장가 매도. 성공하면 True 반환."""
    if DRY_RUN:
        print(f"[DRY_RUN] 매도 — {code} {qty}주 [{reason}] (실제 주문 미전송)")
        return True

    headers = get_headers()
    headers["api-id"] = "kt10001"

    try:
        resp = requests.post(
            f"{BASE_URL}{ORDER_ENDPOINT}",
            headers=headers,
            json={
                "dmst_stex_tp": "KRX",
                "stk_cd": code,
                "ord_qty": str(qty),
                "ord_uv": "",
                "trde_tp": "3",
                "cond_uv": "",
            },
            timeout=10,
        )
        resp.raise_for_status()
        print(f"[주문] 매도 완료 — {code} {qty}주 [{reason}]")
        return True
    except Exception as e:
        print(f"[주문] 매도 실패 — {code}: {e}")
        time.sleep(1)
        return False


def fetch_balance() -> list[dict]:
    """
    잔고 조회 (kt00018). 보유 종목 리스트 반환.
    반환: [{"code": "005930", "qty": 10, "avg_price": 75000, "current": 59000, "eval_rate": -52.71}]
    """
    if DRY_RUN:
        print("[DRY_RUN] 잔고 조회 (실제 API 미호출) — 빈 잔고 반환")
        return []

    headers = get_headers()
    headers["api-id"] = "kt00018"

    try:
        resp = requests.post(
            f"{BASE_URL}{BALANCE_ENDPOINT}",
            headers=headers,
            json={"qry_tp": "1", "dmst_stex_tp": "KRX"},
            timeout=10,
        )
        resp.raise_for_status()
        raw = resp.json()

        result = []
        for item in raw.get("acnt_evlt_remn_indv_tot", []):
            qty = _to_int(item.get("rmnd_qty", "0"))
            if qty <= 0:
                continue
            code = item.get("stk_cd", "").lstrip("A")  # A005930 → 005930
            avg = _to_int(item.get("pur_pric", "0"))
            cur = _to_int(item.get("cur_prc", "0"))
            rate = _to_float(item.get("prft_rt", "0"))
            print(f"[잔고] {code} {item.get('stk_nm','')} | {qty}주 | 수익률: {rate:+.2f}%")
            result.append({
                "code": code,
                "qty": qty,
                "avg_price": avg,
                "current": cur,
                "eval_rate": rate,
            })
        return result
    except Exception as e:
        print(f"[잔고] 조회 실패 — {e}")
        return []
