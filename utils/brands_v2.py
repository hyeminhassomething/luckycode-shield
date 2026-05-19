"""
15개 신생 브랜드 (CJ 프론티어랩스 6기 시뮬레이션) — 식당/식품 도메인.
ITDA 학술제 참가 대학 이름 활용.

Day 1 → 7 → 14 → 30 → 45 → 60 → 75 → 90 마일스톤 시계열.
어뷰징 탈락 2개 = 경희대 활용.
"""
import numpy as np

MILESTONES = [1, 7, 14, 30, 45, 60, 75, 90]

# 모든 브랜드는 식당/식품 카테고리만 사용
BRANDS_DEF = [
    # ===== 어뷰징 확정 탈락 2개 (경희대) =====
    {
        'name': 'KH Kitchen',
        'school': '경희대학교',
        'category': '캐주얼 다이닝',
        'tier': 'abuse_confirmed',
        'final_trust': 42,
        'description': '강남권 캐주얼 다이닝 신규 매장 · Day 30 작업장 동원 의혹',
        'insight_title': '🚨 어뷰징 확정 — 투자 부적합',
        'insight_detail': '시그니처 3개 모두 임계값 초과. Workshop B 12명 패턴 검출. 첫 90일+5점 lift 2.06× (임계 1.81×). co_burst 엣지 47개.',
        'invest_strategy': '❌ 투자 부적합 (브랜드 신뢰도 회복 후 7기 재신청 권장)',
    },
    {
        'name': '쿠시 델리',
        'school': '경희대학교',
        'category': '프리미엄 HMR',
        'tier': 'abuse_confirmed',
        'final_trust': 48,
        'description': '가정간편식(HMR) 신생 · Day 35 의심 리뷰 급증',
        'insight_title': '🚨 어뷰징 확정 — 투자 부적합',
        'insight_detail': '5점 비율 81% (정상 매장의 1.7배). rating_extreme_promoter 엣지 28개. 외부 어뷰징 대행 의뢰 가능성 高.',
        'invest_strategy': '❌ 투자 부적합 (도메인 전문가 추가 검증 필요)',
    },

    # ===== 위험 3개 =====
    {
        'name': 'KHU 베이커리',
        'school': '경희대학교',
        'category': '디저트 카페',
        'tier': 'danger',
        'final_trust': 58,
        'description': '디저트 카페 신생 · 시그니처 2 경계선 진입',
        'insight_title': '⚠️ 위험 — 추가 검증 필요',
        'insight_detail': 'z-score 분포 비대칭 관찰. 작업장 패턴은 미확인이나 의심 사용자 7명 발견. lift 1.45×.',
        'invest_strategy': '⚠️ 보류 (Day 120까지 추가 모니터링 후 재평가)',
    },
    {
        'name': '명륜 한식',
        'school': '성균관대학교',
        'category': '프리미엄 한식',
        'tier': 'danger',
        'final_trust': 62,
        'description': '프리미엄 한식당 · 초기 마케팅 어뷰징 흔적',
        'insight_title': '⚠️ 위험 — 추가 검증 필요',
        'insight_detail': '첫 90일 5점 lift 1.65× (임계값 1.81× 근접). 작업장 미발견, 단독 의심 5명.',
        'invest_strategy': '⚠️ 부분 투자 (5억 한정, 마케팅 비용 감액 조건)',
    },
    {
        'name': 'SG 비건스푼',
        'school': '서강대학교',
        'category': '비건 레스토랑',
        'tier': 'danger',
        'final_trust': 65,
        'description': '비건 레스토랑 · 텍스트 패턴 이상',
        'insight_title': '⚠️ 위험 — 추가 검증 필요',
        'insight_detail': '리뷰 텍스트 평균 길이 220자 (정상 매장 380자 대비 짧음). Promoter 텍스트 시그니처 일부 일치.',
        'invest_strategy': '⚠️ 단계적 투자 (1차 3억 → 검증 후 2차)',
    },

    # ===== 모니터링 4개 (상위 3 + 하위 1) =====
    {
        'name': '인하 푸드테크',
        'school': '인하대학교',
        'category': 'AI 식품 분석',
        'tier': 'monitoring_top',
        'final_trust': 74,
        'description': 'AI 영양 분석 식품 큐레이션 · 일관된 자연 리뷰',
        'insight_title': '🟡 모니터링 — 양호',
        'insight_detail': '시그니처 임계값 미달. 사용자 다양성 양호. 초기 마케팅 활동 자연스러움.',
        'invest_strategy': '🟢 정상 투자 진행 (Day 120 재검토)',
    },
    {
        'name': 'INHA 헬스밀',
        'school': '인하대학교',
        'category': '헬스 도시락',
        'tier': 'monitoring_top',
        'final_trust': 76,
        'description': '헬스 도시락 구독 · 안정적 성장 곡선',
        'insight_title': '🟡 모니터링 — 양호',
        'insight_detail': '신규 매장 정상 패턴. z-score 분포 정상 분포에 근접. Real 사용자 클러스터 형성.',
        'invest_strategy': '🟢 정상 투자 진행 (멘토링 추가 권장)',
    },
    {
        'name': '외대 ESG푸드',
        'school': '한국외국어대학교',
        'category': '친환경 식품',
        'tier': 'monitoring_top',
        'final_trust': 78,
        'description': '친환경 ESG 식품 · 견고한 사용자 베이스',
        'insight_title': '🟡 모니터링 — 양호',
        'insight_detail': '첫 90일 자연스러운 별점 분포 (5점 비율 42%). co_burst 엣지 0개.',
        'invest_strategy': '🟢 정상 투자 진행 + ESG 인증 지원',
    },
    {
        'name': '율전 다이닝',
        'school': '성균관대학교',
        'category': '다이닝 큐레이션',
        'tier': 'monitoring_low',
        'final_trust': 72,
        'description': '맛집 큐레이션 플랫폼 · 일부 텍스트 유사도 관찰',
        'insight_title': '🟡 모니터링 — 양호',
        'insight_detail': '미세한 텍스트 유사도 패턴 (text_extreme 엣지 4개). 즉시 위험은 아님.',
        'invest_strategy': '🟢 정상 투자 진행 (Day 150 텍스트 재검증)',
    },

    # ===== 최우수 ROI 3개 =====
    {
        'name': 'HUFS 글로벌푸드',
        'school': '한국외국어대학교',
        'category': '글로벌 식품',
        'tier': 'top_roi',
        'final_trust': 94,
        'description': '글로벌 시장 식품 큐레이션 · ROI 최우수',
        'insight_title': '⭐ 최우수 — 우선 투자 대상',
        'insight_detail': '시그니처 3개 모두 정상 분포. 사용자 다양성 최고 (Real 클러스터 견고). 첫 90일 매출 증가율 178%.',
        'invest_strategy': '🌟 최대 투자 (13억) + 글로벌 시장 진출 지원',
    },
    {
        'name': '서강 셰프스테이블',
        'school': '서강대학교',
        'category': '프리미엄 다이닝',
        'tier': 'top_roi',
        'final_trust': 92,
        'description': '프리미엄 셰프 다이닝 · 강력한 충성 고객',
        'insight_title': '⭐ 최우수 — 우선 투자 대상',
        'insight_detail': '재구매율 68% (업계 평균 22%). 가짜 리뷰 시그니처 전무. SNS 자연 확산 패턴.',
        'invest_strategy': '🌟 최대 투자 (13억) + B2B 유통망 연결',
    },
    {
        'name': 'SKKU 바이오푸드',
        'school': '성균관대학교',
        'category': '기능성 식품',
        'tier': 'top_roi',
        'final_trust': 91,
        'description': '바이오 기능성 식품 · 학술 IP 강력',
        'insight_title': '⭐ 최우수 — 우선 투자 대상',
        'insight_detail': '연구 기반 신뢰성 + 자연스러운 리뷰 분포. 식품영양학 전문가 인증 다수.',
        'invest_strategy': '🌟 최대 투자 (13억) + CJ제일제당 R&D 협업',
    },

    # ===== 정상 3개 =====
    {
        'name': '서강 브런치',
        'school': '서강대학교',
        'category': '브런치 카페',
        'tier': 'normal',
        'final_trust': 88,
        'description': '신생 브런치 카페 · 안정적 성장',
        'insight_title': '🟢 정상 — 통상 투자',
        'insight_detail': '시그니처 모두 정상. 일반 매장 패턴 일치. Day 60부터 자연 증가세.',
        'invest_strategy': '🟢 통상 투자 (7억) + 마케팅 지원',
    },
    {
        'name': '외대 글로벌키친',
        'school': '한국외국어대학교',
        'category': '다국적 요리',
        'tier': 'normal',
        'final_trust': 85,
        'description': '글로벌 요리 신생 · 외국인 타겟',
        'insight_title': '🟢 정상 — 통상 투자',
        'insight_detail': '외국인 사용자 비율 35% (자연 다양성). 어뷰징 시그니처 없음.',
        'invest_strategy': '🟢 통상 투자 (5억) + 글로벌 PR',
    },
    {
        'name': 'INHA 푸드랩',
        'school': '인하대학교',
        'category': '식품 R&D',
        'tier': 'normal',
        'final_trust': 84,
        'description': '식품 R&D 스타트업 · B2B 위주',
        'insight_title': '🟢 정상 — 통상 투자',
        'insight_detail': 'B2B 리뷰 위주로 작업장 동기 부재. 식품영양학 인증 다수 보유.',
        'invest_strategy': '🟢 통상 투자 (5억) + B2B 네트워킹',
    },
]


def generate_brands_v2():
    """15개 브랜드 + Day 시계열 trust score + 시그니처 추이."""
    np.random.seed(42)
    brands = []

    for i, b in enumerate(BRANDS_DEF):
        initial_trust = int(np.clip(np.random.normal(90, 2), 86, 94))
        final_trust = b['final_trust']

        tier = b['tier']
        trust_series = {}
        sig1_series = {}
        sig2_series = {}
        sig3_series = {}

        for day in MILESTONES:
            progress = day / 90
            if tier == 'abuse_confirmed':
                if day < 30:
                    t = int(initial_trust - progress * 4)
                    s1, s2, s3 = 0.4 + np.random.uniform(-0.05, 0.05), 0.08, 0
                elif day < 45:
                    decay_p = (day - 30) / 15
                    t = int(initial_trust - 5 - decay_p * 30)
                    s1 = 0.4 + decay_p * 1.7
                    s2 = 0.08 + decay_p * 0.20
                    s3 = int(decay_p * 12)
                else:
                    final_decay = (day - 45) / 45
                    t = int(60 - final_decay * (60 - final_trust))
                    s1 = 2.1 + np.random.uniform(-0.1, 0.1)
                    s2 = 0.28 + np.random.uniform(-0.02, 0.02)
                    s3 = 12 + int(np.random.uniform(0, 3))
            elif tier == 'danger':
                if day < 30:
                    t = int(initial_trust - progress * 3)
                    s1, s2, s3 = 0.45, 0.09, 0
                elif day < 60:
                    decay_p = (day - 30) / 30
                    t = int(initial_trust - 8 - decay_p * 18)
                    s1 = 0.45 + decay_p * 1.0
                    s2 = 0.09 + decay_p * 0.10
                    s3 = int(decay_p * 6)
                else:
                    t = int(70 - (day - 60) / 30 * (70 - final_trust))
                    s1 = 1.45 + np.random.uniform(-0.08, 0.08)
                    s2 = 0.18 + np.random.uniform(-0.01, 0.01)
                    s3 = 6 + int(np.random.uniform(-1, 2))
            elif tier in ('monitoring_top', 'monitoring_low'):
                t = int(initial_trust - progress * (initial_trust - final_trust))
                s1 = 0.5 + np.random.uniform(-0.05, 0.05)
                s2 = 0.11 + np.random.uniform(-0.01, 0.01)
                s3 = int(np.random.uniform(0, 2))
            elif tier == 'top_roi':
                t = int(initial_trust + progress * (final_trust - initial_trust))
                s1 = 0.42 + np.random.uniform(-0.04, 0.04)
                s2 = 0.08 + np.random.uniform(-0.005, 0.005)
                s3 = 0
            else:
                t = int(initial_trust + progress * (final_trust - initial_trust))
                s1 = 0.5 + np.random.uniform(-0.04, 0.04)
                s2 = 0.09 + np.random.uniform(-0.01, 0.01)
                s3 = 0

            trust_series[day] = int(np.clip(t, 35, 99))
            sig1_series[day] = float(round(s1, 2))
            sig2_series[day] = float(round(s2, 3))
            sig3_series[day] = int(s3)

        brand_record = {
            **b,
            'initial_trust': initial_trust,
            'trust_series': trust_series,
            'sig1_series': sig1_series,
            'sig2_series': sig2_series,
            'sig3_series': sig3_series,
        }
        brands.append(brand_record)

    return brands


def get_brand_at_day(brand, day):
    """특정 Day 의 brand 상태."""
    if day in MILESTONES:
        trust = brand['trust_series'][day]
        sig1 = brand['sig1_series'][day]
        sig2 = brand['sig2_series'][day]
        sig3 = brand['sig3_series'][day]
    else:
        lower = max([m for m in MILESTONES if m <= day], default=MILESTONES[0])
        upper = min([m for m in MILESTONES if m >= day], default=MILESTONES[-1])
        if lower == upper:
            t = 1.0
        else:
            t = (day - lower) / (upper - lower)
        trust = int(brand['trust_series'][lower] + t * (brand['trust_series'][upper] - brand['trust_series'][lower]))
        sig1 = brand['sig1_series'][lower] + t * (brand['sig1_series'][upper] - brand['sig1_series'][lower])
        sig2 = brand['sig2_series'][lower] + t * (brand['sig2_series'][upper] - brand['sig2_series'][lower])
        sig3 = int(brand['sig3_series'][lower] + t * (brand['sig3_series'][upper] - brand['sig3_series'][lower]))

    if trust < 60:
        if brand['tier'] == 'abuse_confirmed':
            status = 'abuse'
        else:
            status = 'danger'
    elif trust < 80:
        status = 'monitoring'
    else:
        status = 'normal'

    return {
        'trust': trust,
        'sig1': round(sig1, 2),
        'sig2': round(sig2, 3),
        'sig3': sig3,
        'status': status,
        'trust_change': trust - brand['initial_trust'],
    }
