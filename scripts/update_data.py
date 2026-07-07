#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자 지표 대시보드 자동 데이터 수집 스크립트
- 지수/환율/VIX/SOX: 최근 3개월 종가 시계열
- 글로벌 시총 순위: 지정 종목 리스트의 시가총액 (KRW 종목은 USD 환산)
결과를 data/auto.json 에 저장. GitHub Actions에서 주기 실행.
"""
import json
import datetime as dt
from pathlib import Path

import yfinance as yf

OUT = Path(__file__).resolve().parent.parent / "data" / "auto.json"

# ── 시계열 수집 대상 ─────────────────────────────────────
SERIES = {
    "sp500":  ("^GSPC",  "S&P 500"),
    "nasdaq": ("^IXIC",  "나스닥"),
    "dow":    ("^DJI",   "다우존스"),
    "kospi":  ("^KS11",  "KOSPI"),
    "kosdaq": ("^KQ11",  "KOSDAQ"),
    "usdkrw": ("KRW=X",  "USD/KRW"),
    "vix":    ("^VIX",   "VIX"),
    "sox":    ("^SOX",   "SOX"),
    "tnx":  ("^TNX", "미 10년물 금리"),
}

# ── 시총 순위 대상 (필요 시 여기에 추가) ─────────────────
CAP_LIST = [
    ("NVDA",      "엔비디아",        False),
    ("MSFT",      "마이크로소프트",   False),
    ("AAPL",      "애플",            False),
    ("GOOGL",     "알파벳",          False),
    ("AMZN",      "아마존",          False),
    ("META",      "메타",            False),
    ("AVGO",      "브로드컴",        False),
    ("TSM",       "TSMC",           False),
    ("TSLA",      "테슬라",          False),
    ("BRK-B",     "버크셔 해서웨이",  False),
    ("LLY",       "일라이 릴리",      False),
    ("JPM",       "JP모건",          False),
    ("005930.KS", "삼성전자",        True),
    ("000660.KS", "SK하이닉스",      True),
]


def fetch_series():
    out = {}
    for key, (ticker, label) in SERIES.items():
        try:
            hist = yf.Ticker(ticker).history(period="3mo", interval="1d")
            hist = hist.dropna(subset=["Close"])
            out[key] = {
                "label": label,
                "dates": [d.strftime("%Y-%m-%d") for d in hist.index],
                "values": [round(float(v), 2) for v in hist["Close"]],
            }
            print(f"[OK] {label}: {len(hist)} rows")
        except Exception as e:
            print(f"[FAIL] {label}: {e}")
    return out


def fetch_marketcap(usdkrw_rate):
    out = []
    for ticker, name, is_kr in CAP_LIST:
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info
            cap = float(info["market_cap"])
            price = float(info["last_price"])
            prev = float(info["previous_close"])
            chg = (price - prev) / prev * 100 if prev else 0.0
            if is_kr and usdkrw_rate:          # 원화 시총 → USD 환산
                cap = cap / usdkrw_rate
            out.append({
                "ticker": ticker, "name": name, "kr": is_kr,
                "cap": round(cap, 0),
                "price": round(price, 2),
                "chg": round(chg, 2),
            })
            print(f"[OK] {name}: cap={cap:,.0f}")
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
    out.sort(key=lambda x: x["cap"], reverse=True)
    return out


def main():
    series = fetch_series()
    rate = series.get("usdkrw", {}).get("values", [None])[-1]
    caps = fetch_marketcap(rate)

    kst = dt.timezone(dt.timedelta(hours=9))
    payload = {
        "updated": dt.datetime.now(kst).strftime("%Y-%m-%d %H:%M KST"),
        "series": series,
        "marketcap": caps,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"saved -> {OUT}")


if __name__ == "__main__":
    main()
