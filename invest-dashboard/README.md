# 시장 나침반 — 투자 지표 대시보드

주요 투자 지표(미국·한국 지수, 원달러 환율, VIX, SOX, 메모리 현물가, 글로벌 시총 순위)를
한 화면에서 확인하는 정적 대시보드. GitHub Pages + GitHub Actions로 운영.

## 구조

```
index.html                      # 대시보드 본체 (HTML/CSS/JS 단일 파일)
data/auto.json                  # 자동 수집 데이터 (Actions가 생성/갱신)
data/manual.json                # 메모리 현물가 등 수동 입력 데이터
scripts/update_data.py          # yfinance 수집 스크립트
.github/workflows/update-data.yml  # 하루 4회 자동 갱신 (KST 01:30/07:30/13:30/19:30)
```

## 배포 절차

1. GitHub에 새 리포지토리 생성 (예: `invest-dashboard`) 후 전체 파일 push
2. Settings → Pages → Branch: `main` / root 선택
3. Actions 탭에서 `Update dashboard data` 워크플로를 **Run workflow**로 1회 수동 실행
   → `data/auto.json` 생성 확인
4. `https://<계정>.github.io/invest-dashboard/` 접속

> `auto.json`이 없거나 로드 실패 시 페이지는 자동으로 샘플 데이터를 표시하고
> 상단에 "샘플 데이터 표시 중" 배지가 뜹니다. 로컬에서 파일을 직접 열어도 미리보기 가능.

## 메모리 가격 갱신

`data/manual.json`의 `dates` / `values` 배열에 값을 추가하고 commit하면 됩니다.
항목(예: HBM, DDR4) 추가도 같은 형식으로 자유롭게 가능.

## Add-on 로드맵 (제안)

| 순위 | 항목 | 수집 방법 |
|---|---|---|
| 2차 | 미 10년물 국채금리 | yfinance `^TNX` — SERIES에 한 줄 추가 |
| 2차 | 금 / WTI 유가 | yfinance `GC=F`, `CL=F` |
| 3차 | 비트코인 (김치프리미엄) | yfinance `BTC-USD` + 업비트 공개 API |
| 3차 | CNN Fear & Greed | 비공식 API (`edition.cnn.com` JSON) — 안정성 확인 필요 |
| 4차 | 관심 종목 워치리스트 | CAP_LIST와 동일 패턴으로 카드 추가 |

시계열 지표 추가 방법: `update_data.py`의 `SERIES` 딕셔너리에 티커 한 줄 추가 →
`index.html`에 카드 섹션 + `render()` 블록 추가.
