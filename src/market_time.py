from datetime import datetime
import zoneinfo

KST = zoneinfo.ZoneInfo("Asia/Seoul")


def now_kst() -> datetime:
    return datetime.now(KST)


def is_market_open() -> bool:
    """정규장 여부 확인 (평일 09:00~15:30, 공휴일 미처리)."""
    now = now_kst()

    # 주말 제외
    if now.weekday() >= 5:
        return False

    market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)

    return market_open <= now <= market_close


def log_market_status():
    if is_market_open():
        print(f"[시장] 정규장 운영 중 ({now_kst().strftime('%H:%M:%S')})")
    else:
        print(f"[시장] 장 외 시간 ({now_kst().strftime('%H:%M:%S')}) — 매매 중단")
