# 키움증권 자동매매 봇 — 핸드오프 문서

## 프로젝트 개요
- **목적**: 키움증권 REST API 기반 파이썬 자동매매 봇
- **경로**: `C:\Users\keato\coding\stocks(claudecode)`
- **GitHub**: https://github.com/hermes-blue/stocks-claude-kiwm-.git
- **환경**: Windows 11, Python 3.14.4, PowerShell, 가상환경 `.venv`

---

## 환경 설정

### 가상환경 활성화
```powershell
cd "C:\Users\keato\coding\stocks(claudecode)"
.venv\Scripts\Activate.ps1
```

### .env 구성 (실제 값 있음, 깃에 안 올라감)
```
KIWOOM_APP_KEY=...
KIWOOM_APP_SECRET=...
KIWOOM_ACCOUNT_NO=5321-1734
KIWOOM_ENV=prod          # 실전투자
DRY_RUN=True             # False로 바꾸면 실제 주문
POLL_INTERVAL=60         # 종목당 대기 초 (연습시 10)
ENTRY_THRESHOLD=-3.0     # 매수 진입 등락률 (연습시 -1.0)
```

### 키움 REST API 확인된 정보
| 항목 | 값 |
|---|---|
| 실전 BASE_URL | `https://api.kiwoom.com` |
| 모의 BASE_URL | `https://mockapi.kiwoom.com` |
| 토큰 endpoint | `POST /oauth2/token` |
| 토큰 요청 파라미터 | `grant_type`, `appkey`, `secretkey` |
| 토큰 응답 필드 | `token`, `expires_dt` (형식: `20260505145048`) |
| 시세 endpoint | `POST /api/dostk/mrkcond` + `api-id: ka10007` |
| 시세 요청 | `{"stk_cd": "005930"}` |
| 시세 응답 현재가 | `cur_prc` (부호 포함 문자열, abs() 처리 필요) |
| 시세 응답 등락률 | `flu_rt` (문자열) |
| 잔고 endpoint | `POST /api/dostk/acnt` + `api-id: kt00018` |
| 잔고 요청 | `{"qry_tp": "1", "dmst_stex_tp": "KRX"}` |
| 잔고 보유종목 | `acnt_evlt_remn_indv_tot` 배열 |
| 잔고 종목코드 | `stk_cd` (A 접두사 있음: `A005930` → `.lstrip("A")`) |
| 잔고 수량 | `rmnd_qty` (zero-padded 문자열) |
| 잔고 매입단가 | `pur_pric` |
| 잔고 현재가 | `cur_prc` |
| 잔고 수익률 | `prft_rt` (이미 % 계산된 float 문자열) |
| 매수 endpoint | `POST /api/dostk/ordr` + `api-id: kt10000` |
| 매도 endpoint | `POST /api/dostk/ordr` + `api-id: kt10001` |
| 주문 요청 | `dmst_stex_tp`, `stk_cd`, `ord_qty`, `ord_uv("")`, `trde_tp("3")`, `cond_uv("")` |
| 주문 응답 | `ord_no`, `return_code`, `return_msg` |

---

## 파일 구조
```
stocks(claudecode)/
├── .env                    ← 실제 키 (깃 제외)
├── .env.example            ← 키 없는 템플릿
├── .gitignore
├── requirements.txt        ← python-dotenv, requests, tzdata
├── run_screener.py         ← 스크리너 실행 진입점
├── run_watcher.py          ← 진입 감시 실행 진입점
├── run_position.py         ← 포지션 관리 실행 진입점
├── test_auth.py            ← 토큰 테스트용
├── test_balance.py         ← 잔고 테스트용
├── src/
│   ├── config.py           ← 모든 설정값 (.env 읽기)
│   ├── auth.py             ← 키움 토큰 발급/재사용
│   ├── market_time.py      ← 장 시간 체크 (평일 9시~15시30분)
│   ├── price.py            ← 종목 1개 시세 조회
│   ├── watchlist.py        ← 관심종목/매수이관 파일 읽기쓰기
│   ├── order.py            ← 매수/매도/잔고 조회
│   ├── position.py         ← 손절/익절/트레일링
│   ├── watcher.py          ← 라운드로빈 진입 감시 루프
│   ├── screener.py         ← 상한가+거래대금 스크리너
│   └── logger.py           ← 파일 로깅 (logs/날짜.txt)
├── data/
│   ├── watchlist.txt       ← 감시 중인 종목코드 목록
│   └── bought.txt          ← 매수된 종목 기록 (날짜,코드,가격)
├── state/
│   └── position_meta.json  ← 포지션 상태 (절반매도여부, 정점수익률)
└── logs/                   ← 날짜별 로그 파일 (자동 생성)
```

---

## 현재 관심종목 (data/watchlist.txt)
```
222080  씨아이에스
209640  와이제이링크
100790  미래에셋벤처투자
006340  대원전선
024840  KBI메탈
027360  아주IB투자
203650  드림시큐리티
010820  퍼스텍
017900  광전자
046970  우리로
215790  이노인스트루먼트
138360  앤로보틱스
036930  주성엔지니어링
010170  대한광통신
072950  빛샘전자
069540  빛과전자
```
- 058430 (포스코스틸리온): 테스트 중 이미 매수됨 → watchlist에서 제거됨
- PS일렉트로닉스: 코드 미확인, 아직 미추가

---

## 매매 조건 (config.py 기본값)
| 조건 | 값 |
|---|---|
| 진입 (등락률 이하) | -3.0% |
| 손절 | -5.0% |
| 1차 익절 (절반 매도) | +5.0% |
| 2차 익절 (전량 매도) | +10.0% |
| 트레일링 시작 | +7.0% |
| 트레일링 하락 폭 | -3.0% |

---

## 실행 방법
```powershell
# 진입 감시 봇
.venv\Scripts\python.exe run_watcher.py

# 포지션 관리 봇
.venv\Scripts\python.exe run_position.py

# 스크리너 (1회 실행)
.venv\Scripts\python.exe run_screener.py
```

---

## 완료된 것
- [x] 환경 세팅 (.env, .gitignore, 가상환경)
- [x] 키움 토큰 발급/재사용
- [x] 시세 조회 (실제 API 확인)
- [x] 잔고 조회 (실제 API 확인)
- [x] 라운드로빈 진입 감시 루프
- [x] DRY_RUN 스위치
- [x] 장 시간 체크
- [x] 파일 로깅 (logs/)
- [x] 관심종목 파일 관리
- [x] 매수 후 watchlist 이관
- [x] GitHub 연결 및 푸쉬

## 미완료/확인 필요한 것
- [ ] 주문 API 실전 체결 확인 (`trde_tp: "3"` 이 시장가 맞는지 문서 재확인 권장)
- [ ] 스크리너 엔드포인트 (상한가 조회 `/api/dostk/upperlimit` 등 — 문서 확인 필요)
- [ ] 포지션 관리 봇 실전 테스트
- [ ] PS일렉트로닉스 종목코드 확인
- [ ] 공휴일 처리 (현재 평일만 체크, 공휴일 미처리)

---

## 알려진 버그 및 수정 내역
- `cur_prc` 가 `-8050` 처럼 부호 포함 문자열로 올 수 있음 → `abs()` 로 처리 완료 (price.py)
- 포스코스틸리온(058430) 테스트 매수 시 매수가 `-8050` 으로 잘못 기록됨 → 수정 완료

---

## 사용자 참고
- 바이브코딩 초보, 쉬운 설명 선호
- 윈도우/PowerShell 환경
- 과다호출 절대 금지 (1종목 1분 1호출이 기본 정책)
- 실전 투자 계좌 사용 중 (DRY_RUN=False 시 실제 주문 나감)
