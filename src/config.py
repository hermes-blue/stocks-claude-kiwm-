import os
from dotenv import load_dotenv

load_dotenv()

APP_KEY = os.getenv("KIWOOM_APP_KEY", "")
APP_SECRET = os.getenv("KIWOOM_APP_SECRET", "")
ACCOUNT_NO = os.getenv("KIWOOM_ACCOUNT_NO", "")
KIWOOM_ENV = os.getenv("KIWOOM_ENV", "paper")  # paper(모의) 또는 prod(실전)
DRY_RUN = os.getenv("DRY_RUN", "True").lower() != "false"

# 모의투자/실전투자 URL 자동 선택
if KIWOOM_ENV == "prod":
    BASE_URL = "https://api.kiwoom.com"
else:
    BASE_URL = "https://mockapi.kiwoom.com"

# 파일 경로
WATCHLIST_FILE = "data/watchlist.txt"
BOUGHT_FILE = "data/bought.txt"
POSITION_META_FILE = "state/position_meta.json"

# 매매 조건 (필요하면 .env 로 이전 가능)
ENTRY_THRESHOLD = float(os.getenv("ENTRY_THRESHOLD", "-3.0"))   # 등락률 이하면 매수
STOP_LOSS = float(os.getenv("STOP_LOSS", "-5.0"))               # 손절 %
TAKE_PROFIT_1 = float(os.getenv("TAKE_PROFIT_1", "5.0"))        # 1차 익절 % (절반 매도)
TAKE_PROFIT_2 = float(os.getenv("TAKE_PROFIT_2", "10.0"))       # 2차 익절 % (전량 매도)
TRAILING_TRIGGER = float(os.getenv("TRAILING_TRIGGER", "7.0"))  # 트레일링 시작 %
TRAILING_DROP = float(os.getenv("TRAILING_DROP", "3.0"))        # 정점 대비 하락 %

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))           # 종목당 대기 초
