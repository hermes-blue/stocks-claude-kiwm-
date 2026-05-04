import time
from src.position import run_position_manager
from src.market_time import is_market_open, now_kst
from src.config import POLL_INTERVAL

if __name__ == "__main__":
    print("[포지션봇] 시작")
    while True:
        if is_market_open():
            run_position_manager()
        else:
            print(f"[포지션봇] 장 외 시간 — 대기 중 ({now_kst().strftime('%H:%M:%S')})")
        time.sleep(POLL_INTERVAL)
