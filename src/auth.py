import time
import requests
from datetime import datetime
from src.config import APP_KEY, APP_SECRET, BASE_URL

_token = ""
_token_expires_at = 0


def get_token() -> str:
    """액세스 토큰 반환. 만료 전이면 기존 토큰 재사용."""
    global _token, _token_expires_at

    if _token and time.time() < _token_expires_at:
        return _token

    if not APP_KEY or not APP_SECRET:
        print("[인증] APP_KEY / APP_SECRET 이 비어있습니다. .env 파일을 확인해주세요.")
        return ""

    print("[인증] 토큰 발급 요청 중...")
    try:
        resp = requests.post(
            f"{BASE_URL}/oauth2/token",
            headers={"Content-Type": "application/json;charset=UTF-8"},
            json={
                "grant_type": "client_credentials",
                "appkey": APP_KEY,
                "secretkey": APP_SECRET,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        _token = data["token"]
        expires_dt = datetime.strptime(data["expires_dt"], "%Y%m%d%H%M%S")
        _token_expires_at = expires_dt.timestamp() - 60
        print("[인증] 토큰 발급 성공")
        return _token
    except Exception as e:
        print(f"[인증] 토큰 발급 실패: {e}")
        return ""


def get_headers() -> dict:
    """API 호출에 필요한 공통 헤더 반환."""
    return {
        "Content-Type": "application/json;charset=UTF-8",
        "authorization": f"Bearer {get_token()}",
        "appkey": APP_KEY,
        "secretkey": APP_SECRET,
    }
