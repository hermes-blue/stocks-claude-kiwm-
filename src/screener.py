"""
스크리너: 최근 N일 내 상한가 종목 + 거래대금 조건 필터링.
키움 REST API로 데이터 조회. (⚠ 엔드포인트 확인 필요)
"""
import time
import requests
from datetime import date, timedelta
from src.auth import get_headers
from src.config import BASE_URL, WATCHLIST_FILE

# 스크리너 조건
LOOKBACK_DAYS = 20          # 최근 N일 내 상한가
MIN_TRADE_AMOUNT = 5_000_000_000  # 거래대금 최소 50억
MIN_HIGH_DAYS = 1           # 상한가 최소 횟수

# ⚠ 확인 필요: 키움 REST API 상한가/거래대금 조회 엔드포인트
UPPER_LIMIT_ENDPOINT = "/api/dostk/upperlimit"   # 상한가 종목 조회
DAILY_CHART_ENDPOINT = "/api/dostk/dailychart"   # 일별 시세


def fetch_upper_limit_stocks() -> list[str]:
    """최근 N일 내 상한가 종목 코드 목록 조회."""
    codes = set()
    headers = get_headers()
    if not headers.get("authorization", "").startswith("Bearer "):
        print("[스크리너] 토큰 없음 — 종료")
        return []

    for i in range(LOOKBACK_DAYS):
        target_date = (date.today() - timedelta(days=i)).strftime("%Y%m%d")
        try:
            resp = requests.get(
                f"{BASE_URL}{UPPER_LIMIT_ENDPOINT}",
                headers=headers,
                params={"dt": target_date},  # ⚠ 확인 필요
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("list", []):
                codes.add(item.get("stk_cd", ""))
            print(f"[스크리너] {target_date} 상한가 조회 완료")
        except Exception as e:
            print(f"[스크리너] {target_date} 조회 실패 — {e}")
        time.sleep(1)  # 날짜별로 1초 간격

    return list(codes - {""})


def check_trade_amount(code: str) -> bool:
    """최근 5일 거래대금이 조건 이상인지 확인."""
    headers = get_headers()
    try:
        resp = requests.get(
            f"{BASE_URL}{DAILY_CHART_ENDPOINT}",
            headers=headers,
            params={"stk_cd": code, "cnt": "5"},  # ⚠ 확인 필요
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        amounts = [int(item.get("trd_amt", 0)) for item in data.get("list", [])]
        passing = sum(1 for a in amounts if a >= MIN_TRADE_AMOUNT)
        return passing >= MIN_HIGH_DAYS
    except Exception as e:
        print(f"[스크리너] {code} 거래대금 조회 실패 — {e}")
        return False


def run_screener():
    """스크리너 실행: 조건 통과 종목을 관심종목 파일에 저장."""
    print(f"[스크리너] 시작 — 최근 {LOOKBACK_DAYS}일 상한가 종목 조회")
    candidates = fetch_upper_limit_stocks()
    print(f"[스크리너] 상한가 후보: {len(candidates)}개")

    passed = []
    for code in candidates:
        if check_trade_amount(code):
            passed.append(code)
            print(f"[스크리너] {code} ✓ 조건 통과")
        else:
            print(f"[스크리너] {code} ✗ 거래대금 미달")
        time.sleep(1)

    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        for code in passed:
            f.write(code + "\n")

    print(f"[스크리너] 완료 — {len(passed)}개 종목 → {WATCHLIST_FILE} 저장")
