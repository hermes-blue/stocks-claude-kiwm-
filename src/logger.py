import os
from datetime import datetime
import zoneinfo

KST = zoneinfo.ZoneInfo("Asia/Seoul")
LOG_DIR = "logs"


def log(msg: str):
    os.makedirs(LOG_DIR, exist_ok=True)
    today = datetime.now(KST).strftime("%Y-%m-%d")
    ts = datetime.now(KST).strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(f"{LOG_DIR}/{today}.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")
