"""
ON-Trust Shield — 데이터 생성 모듈.
본 연구 50K 메인 분석 검증된 수치 기반.
"""
import numpy as np
import pandas as pd

# ============================================
# 50K 메인 분석 검증된 수치 (CONSTANTS - 변경 금지)
# ============================================
BASELINE_FAKE_RATE = 0.1322   # 전체 YelpZip 608K
BASELINE_50K = 0.1079         # 50K Top 200

# 시그너처 임계값
SIG1_THRESHOLD_LIFT = 1.81    # 23.98% / 13.22%
SIG2_THRESHOLD_RATIO = 0.20
SIG3_THRESHOLD_USERS = 5

# Promoter 확정 그룹 (50K)
PROMOTER_CONFIRMED_N = 24
PROMOTER_Z_MEAN = 1.50
PROMOTER_FIRST_90D_PCT = 100.0

# Terrorist 확정 그룹 (50K)
TERRORIST_CONFIRMED_N = 580
TERRORIST_Z_MEAN = -3.21

# 100% fake user (전체 EDA)
FAKE_USERS_ALL = 9434
ACTIVE_USERS = 90163
FAKE_USERS_RATIO = 0.105

# 50K 노드 / 엣지
N_NODES = {'review': 50000, 'user': 37481, 'product': 200}
N_EDGES = {
    'writes': 50000,
    'targets': 50000,
    'rating_extreme_promoter': 3332,
    'rating_extreme_terrorist': 334,
    'text_extreme': 351,
    'user_co_burst': 70532,
}
EDGE_DENSITY = {
    'rating_extreme_promoter': 1.12,
    'rating_extreme_terrorist': 2.64,
    'text_extreme': 2.81,
    'user_co_burst': 1.16,
}

# Multi-seed 성능
PR_AUC_HETEROSAGE = (0.2385, 0.0217)
PR_AUC_HOMOSAGE = (0.2249, 0.0038)
PR_AUC_HOMOGCN = (0.2191, 0.0037)
PR_AUC_HOMOGAT = (0.2232, 0.0016)
PR_AUC_XGBOOST = (0.2008, 0.0000)

# Stacking
STACKING_PR_AUC = 0.2243
STACKING_RECALL = 0.5095
STACKING_PRECISION = 0.2170
STACKING_TP = 215
HETEROSAGE_TP = 104
HETEROSAGE_RECALL = 0.2464
RECALL_GAIN_PP = 26.3

# Yelp Open
YELP_OPEN = {
    'promoter_z': 1.18,
    'terrorist_z': -2.16,
    'promoter_text': 395,
    'terrorist_text': 524,
    'promoter_users_sig3': 1708,
    'terrorist_users_sig3': 16,
    'ratio': 107,
}


# ============================================
# 25개 브랜드 데이터
# ============================================
def generate_brands():
    """25개 브랜드 (22 정상 + 2 모니터링 + 1 위험 = Brand D)."""
    np.random.seed(42)
    brands = []

    # 22개 정상
    for i in range(22):
        days = int(np.random.randint(20, 85))
        trust = int(np.clip(np.random.normal(88, 4), 82, 95))
        brands.append({
            'name': f'Brand_{chr(65+i)}',
            'day': days,
            'trust': trust,
            'trust_change': int(np.random.choice([-1, 0, 1, 2, 3])),
            'sig1_lift': float(np.random.uniform(0.3, 0.6)),
            'sig2_ratio': float(np.random.uniform(0.05, 0.12)),
            'sig3_users': 0,
            'status': 'normal',
        })

    # 2개 모니터링 (마지막에 추가)
    for i in [22, 23]:
        brands.append({
            'name': f'Brand_{chr(65+i)}',
            'day': int(np.random.randint(30, 70)),
            'trust': int(np.random.choice([72, 76])),
            'trust_change': int(-np.random.randint(5, 12)),
            'sig1_lift': float(np.random.uniform(1.2, 1.7)),
            'sig2_ratio': float(np.random.uniform(0.13, 0.18)),
            'sig3_users': int(np.random.randint(1, 4)),
            'status': 'monitoring',
        })

    # 4번째 (index 3) 를 Brand_D 위험으로 교체
    brands[3] = {
        'name': 'Brand_D',
        'day': 45,
        'trust': 67,
        'trust_change': -22,
        'sig1_lift': 2.06,
        'sig2_ratio': 0.271,
        'sig3_users': 12,
        'status': 'danger',
    }

    return brands


# ============================================
# Brand D 90일 시계열
# ============================================
def generate_brand_d_timeseries():
    np.random.seed(42)
    days = np.arange(1, 91)
    sig1 = []
    for d in days:
        if d < 30:
            sig1.append(float(np.random.uniform(0.32, 0.46)))
        elif d < 45:
            progress = (d - 30) / 15
            base = 1.05 + progress * 1.54
            sig1.append(float(base + np.random.uniform(-0.05, 0.05)))
        else:
            sig1.append(float(np.random.uniform(1.85, 2.20)))

    sig2 = []
    for d in days:
        if d < 30:
            sig2.append(float(np.random.uniform(0.06, 0.10)))
        elif d < 45:
            progress = (d - 30) / 15
            base = 0.09 + progress * 0.18
            sig2.append(float(base + np.random.uniform(-0.01, 0.01)))
        else:
            sig2.append(float(np.random.uniform(0.22, 0.28)))

    sample_days = [1, 7, 14, 21, 28, 30, 35, 40, 44, 45]
    sample_counts = [2, 3, 2, 3, 4, 5, 8, 14, 22, 28]

    # 신규 5점 리뷰 일별 카운트
    daily_5star = []
    for d in days:
        if d < 30:
            daily_5star.append(int(np.random.poisson(2)))
        elif d < 45:
            daily_5star.append(int(np.random.poisson(4 + (d-30)*0.5)))
        else:
            daily_5star.append(int(np.random.poisson(7)))

    return {
        'days': days.tolist(),
        'sig1': sig1,
        'sig2': sig2,
        'edges_sample_days': sample_days,
        'edges_counts': sample_counts,
        'daily_5star': daily_5star,
    }


# ============================================
# t-SNE 클러스터 데이터
# ============================================
def generate_tsne_data():
    np.random.seed(42)
    normal_x = np.random.normal(0, 0.35, 100)
    normal_y = np.random.normal(0, 0.35, 100)
    promoter_x = np.random.normal(1.2, 0.3, 50)
    promoter_y = np.random.normal(1.0, 0.3, 50)
    terrorist_x = np.random.normal(-1.2, 0.3, 30)
    terrorist_y = np.random.normal(-1.0, 0.3, 30)
    trajectory_days = [1, 7, 14, 21, 28, 30, 35, 40, 44, 45]
    trajectory_x = [0.12, 0.15, 0.10, 0.18, 0.20, 0.25, 0.35, 0.52, 0.68, 0.78]
    trajectory_y = [0.08, 0.05, 0.12, 0.15, 0.18, 0.22, 0.32, 0.48, 0.58, 0.65]
    return {
        'normal': (normal_x.tolist(), normal_y.tolist()),
        'promoter': (promoter_x.tolist(), promoter_y.tolist()),
        'terrorist': (terrorist_x.tolist(), terrorist_y.tolist()),
        'trajectory': (trajectory_days, trajectory_x, trajectory_y),
    }


# ============================================
# 작업장 사용자 47명 (시그너처 3)
# ============================================
def generate_suspect_users():
    np.random.seed(42)
    users = []

    # Workshop B 12명 (clustered)
    for i in range(12):
        x = 0.85 + np.random.normal(0, 0.05)
        y = 0.7 + np.random.normal(0, 0.05)
        users.append({
            'user_id': f'User_#{1234+i}',
            'x': float(x), 'y': float(y),
            'reviews': int(np.random.randint(3, 7)),
            'first_90d_pct': int(np.random.choice([100, 100, 100, 80])),
            'avg_z': float(round(np.random.uniform(1.7, 2.3), 2)),
            'co_burst': int(np.random.randint(6, 11)),
            'cluster': 'Workshop_B',
        })

    # 단독 의심 35명
    for i in range(35):
        x = np.random.uniform(0.4, 1.3)
        y = np.random.uniform(0.3, 1.1)
        users.append({
            'user_id': f'User_#{2001+i}',
            'x': float(x), 'y': float(y),
            'reviews': int(np.random.randint(2, 5)),
            'first_90d_pct': int(np.random.choice([100, 67, 100, 80])),
            'avg_z': float(round(np.random.uniform(1.1, 2.0), 2)),
            'co_burst': int(np.random.randint(0, 3)),
            'cluster': 'Single',
        })

    return users


# ============================================
# Activity feed 메시지
# ============================================
def generate_activity_feed():
    return [
        '04:00 KST · Brand_D Trust Score 89 → 67 · 🚨 Alert · 검토 큐 생성 (47건)',
        '03:45 KST · Brand_C 분석 완료 · Trust 91 (안정)',
        '03:30 KST · Brand_E 신규 리뷰 12개 처리 · 3개 시그너처 정상',
        '03:15 KST · Workshop B 패턴 식별 · 작업장 사용자 12명 클러스터링',
        '03:00 KST · Brand_M 시그너처 1 lift 0.42× (정상 범위)',
        '02:45 KST · co_burst 엣지 47개 추가 → user_co_burst 70,579개',
        '02:30 KST · Brand_F z-score 분포 일일 갱신',
        '02:15 KST · HeteroSAGE 모델 일일 재학습 완료',
        '02:00 KST · Multi-seed 평가 PR-AUC 0.2385 ± 0.0217 유지',
    ]
