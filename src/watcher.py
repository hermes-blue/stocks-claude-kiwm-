import time
from src.price import fetch_price
from src.watchlist import load_watchlist, remove_from_watchlist, add_to_bought, load_bought_today
from src.order import buy_market
from src.market_time import is_market_open, now_kst
from src.logger import log
from src.config import POLL_INTERVAL, ENTRY_THRESHOLD

BUY_QTY = 1


def run_watcher():
    """관심종목 라운드로빈 진입 감시 루프."""
    log(f"[감시] 시작 - 진입 조건: 등락률 {ENTRY_THRESHOLD:+.1f}% 이하 | 폴링: {POLL_INTERVAL}초/종목")

    index = 0

    while True:
        stock_codes = load_watchlist()

        if not stock_codes:
            log("[감시] 관심종목 없음 - 60초 후 재시도")
            time.sleep(60)
            continue

        if not is_market_open():
            log(f"[감시] 장 외 시간 - 60초 후 재확인 ({now_kst().strftime('%H:%M:%S')})")
            time.sleep(60)
            index = 0
            continue

        code = stock_codes[index % len(stock_codes)]
        bought_today = load_bought_today()

        if code in bought_today:
            log(f"[감시] {code} 오늘 이미 매수 - 건너뜀")
        else:
            result = fetch_price(code)
            if result and result["change_rate"] <= ENTRY_THRESHOLD:
                log(f"[감시] {code} 진입 조건 충족 ({result['change_rate']:+.2f}%) - 매수 시도")
                ok = buy_market(code, BUY_QTY)
                if ok:
                    add_to_bought(code, result["current"])
                    remove_from_watchlist(code)
                    stock_codes = load_watchlist()

        index += 1
        time.sleep(POLL_INTERVAL)
