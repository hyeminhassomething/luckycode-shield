# 🛡️ ON-Trust Shield

> ITDA 학술제 2026 본선 발표 시각화 대시보드
> CJ Frontier Labs 입주 브랜드 25개 신뢰도 실시간 모니터링 (Mission Control Center 컨셉)

## 실행

```bash
cd final/on_trust_shield
pip install -r requirements.txt
streamlit run app.py
```

브라우저: http://localhost:8501

## 구조

```
on_trust_shield/
├── app.py                       # 메인 대시보드 (단일 페이지)
├── utils/
│   ├── data_generator.py        # 50K 검증 수치 + 시뮬레이션 데이터
│   ├── charts.py                # Plotly 차트 (gauge, sig1-3, t-SNE)
│   └── styles.py                # 다크 테마 + 애니메이션 CSS
├── requirements.txt
└── README.md
```

## 페이지 구조

1. **Header** — Logo · LIVE 표시 (깜빡임) · 사용자 (김OO CJ Investment)
2. **KPI Hero Strip (4 카드)** — 모니터링 25 · 정상 22 · 모니터링 2 · 위험 1 (Brand_D 깜빡임)
3. **Brand Grid 5×5 (25개 카드)** — 정상 녹색 / 모니터링 amber / 위험 빨강 + glow
4. **Brand_D Detail Header** — 신뢰도 게이지 67/100 (▼22)
5. **3개 탭:**
   - **시그너처 분석** — 3컬럼 (시간 lift / 별점 z 분포 / 사용자 작업장)
   - **t-SNE 임베딩 이동** — Brand_D Day 1→45 궤적 + Promoter 클러스터 접근
   - **자동 검토 큐 (Slack)** — Slack 알림 UI + Workshop B 12명 표
6. **Activity Feed** — 하단 가로 스크롤 (Agent ACTIVE 펄스)
7. **Footer 4 카드** — HeteroSAGE PR-AUC · Stacking · 그래프 통계 · 외부 일반화

## 시각화 무기

- **다크 테마** (#0A0E1A) + CJ Red 액센트 + 네온 글로우
- **3가지 애니메이션:** danger-glow (위험 카드), pulse (live dot), scroll-feed (하단 피드)
- **인터랙티브:** 모든 Plotly 차트 hover · brand 카드 hover lift
- **3 시그너처 통합 시각화:** 시간(라인) + 별점(히스토+막대) + 사용자(산점도+엣지)

## 데모 시나리오 (1분)

```
[0:00-0:05] 페이지 로드 → KPI strip 4개 카드 (Brand_D 깜빡임 자연스럽게 시선 끔)
[0:05-0:15] Brand Grid 5x5 → Brand_D만 빨갛게 빛남
[0:15-0:25] 화면 스크롤 → Brand_D Detail 헤더 + 게이지 67 표시
[0:25-0:40] 시그너처 탭 3개 차트 순차 강조
            ① lift 곡선이 1.81× 임계값 넘는 Day 45 빨간 마커
            ② z 분포 비대칭 (양극 부풀어 오름)
            ③ Workshop B 12명 클러스터링 + co_burst 엣지
[0:40-0:55] 검토 큐 탭 → Slack 알림 카드 + 12명 위험도 progress bar 표
[0:55-1:00] 하단 activity feed 스크롤 강조 (Agent ACTIVE)
```

## 본 연구 검증 수치 (전부 50K 메인 분석)

| 지표 | 값 |
|---|---:|
| HeteroSAGE Multi-seed PR-AUC | 0.2385 ± 0.0217 |
| Stacking PR-AUC | 0.2243 |
| Stacking Recall (gain) | 50.9% (+26.3%p) |
| 50K baseline fake율 | 10.79% |
| Sig 1 임계값 (lift) | 1.81× |
| Sig 3 임계값 (작업장 사용자) | 5명 |
| 노드 수 | Review 50,000 / User 37,481 / Product 200 |
| co_burst 엣지 | 70,532 (농축도 1.16×) |
| Yelp Open 비율 (시그너처 3 근거) | ~107:1 |

## 발표 핵심 메시지

> "본 연구 모델은 단순 사후 탐지가 아닙니다.
> 첫 90일 골든 타임 안에서 3개 시그너처를 실시간 추적하고,
> Brand_D 같은 위험 브랜드를 자동 식별합니다.
> CJ 프론티어랩스 6기 25개 브랜드 모니터링이 가능합니다."
