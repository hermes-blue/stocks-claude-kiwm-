from datetime import date
from src.config import WATCHLIST_FILE, BOUGHT_FILE


def load_watchlist() -> list[str]:
    try:
        with open(WATCHLIST_FILE, encoding="utf-8") as f:
            codes = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return codes
    except FileNotFoundError:
        print(f"[관심종목] 파일 없음: {WATCHLIST_FILE}")
        return []


def save_watchlist(codes: list[str]):
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        for code in codes:
            f.write(code + "\n")


def remove_from_watchlist(code: str):
    codes = load_watchlist()
    if code in codes:
        codes.remove(code)
        save_watchlist(codes)
        print(f"[관심종목] {code} 제거 완료")


def add_to_bought(code: str, price: int):
    today = date.today().isoformat()
    with open(BOUGHT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{today},{code},{price}\n")
    print(f"[매수이관] {code} → {BOUGHT_FILE} 기록 완료 (매수가: {price:,}원)")


def load_bought_today() -> set[str]:
    today = date.today().isoformat()
    bought = set()
    try:
        with open(BOUGHT_FILE, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2 and parts[0] == today:
                    bought.add(parts[1])
    except FileNotFoundError:
        pass
    return bought
