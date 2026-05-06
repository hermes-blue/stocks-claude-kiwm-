import json
import os
from src.config import (
    POSITION_META_FILE,
    STOP_LOSS, TAKE_PROFIT_1, TAKE_PROFIT_2,
    TRAILING_TRIGGER, TRAILING_DROP,
)
from src.order import fetch_balance, sell_market


def load_meta() -> dict:
    if not os.path.exists(POSITION_META_FILE):
        return {}
    with open(POSITION_META_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_meta(meta: dict):
    with open(POSITION_META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def run_position_manager():
    """잔고 기준 익절/손절/트레일링 관리 루프."""
    print("[포지션] 포지션 관리 시작")
    meta = load_meta()
    holdings = fetch_balance()

    if not holdings:
        print("[포지션] 보유 종목 없음")
        return

    for h in holdings:
        code = h["code"]
        qty = h["qty"]
        rate = h["eval_rate"]

        if code not in meta:
            meta[code] = {"half_sold": False, "peak_rate": 0.0}

        m = meta[code]
        m["peak_rate"] = max(m["peak_rate"], rate)
        peak = m["peak_rate"]

        print(f"[포지션] {code} | 평가손익: {rate:+.2f}% | 정점: {peak:+.2f}% | 절반매도: {m['half_sold']}")

        # 손절
        if rate <= STOP_LOSS:
            print(f"[포지션] {code} 손절 실행 ({rate:.2f}% ≤ {STOP_LOSS}%)")
            if sell_market(code, qty, reason="손절"):
                del meta[code]
            continue

        # 트레일링 (1차 익절 이후 or 트리거 도달 후 하락)
        if peak >= TRAILING_TRIGGER and rate <= peak - TRAILING_DROP:
            print(f"[포지션] {code} 트레일링 매도 (정점 {peak:.2f}% → 현재 {rate:.2f}%)")
            if sell_market(code, qty, reason="트레일링"):
                del meta[code]
            continue

        # 2차 익절 (전량)
        if rate >= TAKE_PROFIT_2:
            print(f"[포지션] {code} 2차 익절 ({rate:.2f}% ≥ {TAKE_PROFIT_2}%)")
            if sell_market(code, qty, reason="2차익절"):
                del meta[code]
            continue

        # 1차 익절 (절반, 1회만)
        if rate >= TAKE_PROFIT_1 and not m["half_sold"]:
            half = max(1, qty // 2)
            print(f"[포지션] {code} 1차 익절 ({rate:.2f}% ≥ {TAKE_PROFIT_1}%) - {half}주 매도")
            if sell_market(code, half, reason="1차익절"):
                m["half_sold"] = True

    save_meta(meta)
    print("[포지션] 상태 저장 완료")
