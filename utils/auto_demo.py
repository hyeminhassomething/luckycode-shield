"""
🎬 ON-Trust Shield 본선 자동 재생 데모 (V5 — 시간 기반).
play_start_time(time.time()) 를 기록 → 매 render 시 elapsed 계산 → step idx 결정.
autorefresh 는 단순히 매 0.5초마다 페이지 rerun 만 시킴.
슬라이더는 HTML progress bar 로 교체 (widget 충돌 회피).
"""
import time
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh

from utils.brands_v2 import generate_brands_v2, get_brand_at_day, MILESTONES
from utils.deep_insight import DEEP_INSIGHT_DATA, render_deep_insight_modal


STEPS = [1, 7, 14, 30, 45, 60, 75, 90]
STEP_INTERVAL_SEC = 1.2  # 각 step 표시 시간
DECISION_DELAY_SEC = 1.5  # Day 90 후 결정 팝업까지 추가 대기

COLOR_STATUS = {
    'normal': '#34C759',
    'monitoring': '#FFB800',
    'danger': '#FF8C00',
    'abuse': '#FF3B30',
}


def _hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return ', '.join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))


def render_card_compact(brand, state, show_insight=False, highlight=False):
    color = COLOR_STATUS[state['status']]
    trust = state['trust']
    change = state['trust_change']
    sig1 = state['sig1']
    sig2 = state['sig2']
    sig3 = state['sig3']
    change_color = '#34C759' if change >= 0 else '#FF3B30'
    change_text = f'▲ +{change}' if change > 0 else (f'▼ {change}' if change < 0 else '—')

    glow = ''
    if state['status'] == 'abuse':
        glow = 'box-shadow:0 0 16px rgba(255,59,48,0.45);animation:pulse 1.5s infinite;'
    elif highlight:
        glow = f'box-shadow:0 0 12px rgba({_hex_to_rgb(color)},0.35);'

    insight_html = ''
    if show_insight:
        insight_html = (
            f"<div style='margin-top:6px;padding:6px 8px;"
            f"background:rgba({_hex_to_rgb(color)},0.12);"
            f"border-left:2px solid {color};border-radius:4px;'>"
            f"<div style='color:{color};font-size:9.5px;font-weight:700;line-height:1.3;'>"
            f"{brand['insight_title']}</div>"
            f"<div style='color:#FFD700;font-size:9.5px;margin-top:3px;font-weight:600;line-height:1.3;'>"
            f"{brand['invest_strategy']}</div>"
            f"</div>"
        )

    # 카드 — 매우 컴팩트 + Trust 점수만 28px
    return (
        f"<div style='background:#131829;border:1px solid #2A3447;"
        f"border-left:3px solid {color};border-radius:6px;"
        f"padding:4px 7px;margin-bottom:3px;{glow}'>"
        f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
        f"<div style='color:#FFFFFF;font-weight:700;font-size:10.5px;letter-spacing:-0.3px;'>"
        f"{brand['name']}</div>"
        f"<div style='color:{color};font-size:28px;font-weight:900;line-height:1;font-family:Inter;letter-spacing:-1.2px;'>"
        f"{trust}</div>"
        f"</div>"
        f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
        f"<div style='color:#8B96AB;font-size:8.5px;'>{brand['school'][:3]} · {brand['category']}</div>"
        f"<div style='color:{change_color};font-size:9px;font-family:JetBrains Mono;'>{change_text}</div>"
        f"</div>"
        f"<div style='color:#8B96AB;font-size:8px;font-family:JetBrains Mono;"
        f"letter-spacing:-0.3px;'>"
        f"S1: {sig1}× · S2: {int(sig2*100)}% · S3: {sig3}"
        f"</div>"
        f"{insight_html}"
        f"</div>"
    )


def render_auto_demo():
    """본선 자동 재생 데모 메인 (V5 — 시간 기반)."""

    # ====== CSS ======
    st.markdown("""
<style>
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.78; }
}
section[data-testid="stSidebar"] {
    width: 180px !important;
    min-width: 180px !important;
}
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.4rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    max-width: 100% !important;
}
.demo-header-compact {
    background: linear-gradient(90deg, #131829 0%, rgba(255,59,48,0.18) 100%);
    padding: 8px 14px;
    border-radius: 8px;
    border: 1px solid #2A3447;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.group-header {
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 5px;
    display: inline-block;
    margin: 6px 0 4px 0;
}
.group-header.green { background: rgba(52,199,89,0.18); color: #34C759; border-left: 3px solid #34C759; }
.group-header.yellow { background: rgba(255,184,0,0.18); color: #FFB800; border-left: 3px solid #FFB800; }
.group-header.orange { background: rgba(255,140,0,0.18); color: #FF8C00; border-left: 3px solid #FF8C00; }
.group-header.red { background: rgba(255,59,48,0.22); color: #FF3B30; border-left: 3px solid #FF3B30; }
.empty-slot {
    background: rgba(139,150,171,0.06);
    border: 1px dashed #2A3447;
    border-radius: 7px;
    padding: 12px;
    text-align: center;
    color: #5B6478;
    font-size: 10px;
    margin-bottom: 4px;
}
.decision-popup-v3 {
    background: linear-gradient(135deg, #1C2235 0%, rgba(255,59,48,0.12) 100%);
    border: 1px solid #FF3B30;
    border-radius: 8px;
    padding: 6px 12px;
    box-shadow: 0 0 18px rgba(255,59,48,0.25);
    margin: 4px 0 6px 0;
}
.stButton button {
    padding: 4px 12px !important;
    font-size: 12px !important;
    height: 32px !important;
    background-color: #1C2235 !important;
    color: #FFFFFF !important;
    border: 1px solid #2A3447 !important;
    font-weight: 600 !important;
}
.stButton button:hover {
    background-color: #2A3447 !important;
    border-color: #FF3B30 !important;
    color: #FFFFFF !important;
}
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #FF3B30, #BF5AF2) !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
}
.day-progress-wrap {
    background: #131829;
    border: 1px solid #2A3447;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.day-progress-bar-bg {
    background: #1C2235;
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    position: relative;
}
.day-progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #34C759 0%, #FFB800 60%, #FF3B30 100%);
    border-radius: 4px;
    transition: width 0.4s ease-out;
}
.day-markers {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
    color: #5B6478;
    font-size: 9px;
    font-family: JetBrains Mono, monospace;
}
.day-markers span.active {
    color: #FFD700;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

    # ====== State 초기화 ======
    if 'play_start_time' not in st.session_state:
        st.session_state.play_start_time = None  # None = 자동재생 아님
    if 'manual_day' not in st.session_state:
        st.session_state.manual_day = 1
    if 'force_decision' not in st.session_state:
        st.session_state.force_decision = False
    if 'detail_brand' not in st.session_state:
        st.session_state.detail_brand = None

    # ====== 1) 상세 분석 모달 (최우선 처리) ======
    if st.session_state.detail_brand is not None:
        st.session_state.play_start_time = None  # 자동재생 즉시 정지
        brand_name = st.session_state.detail_brand

        cback, _ = st.columns([2, 8])
        with cback:
            if st.button('← 결정 화면으로 돌아가기', use_container_width=True, type='primary'):
                st.session_state.detail_brand = None
                st.session_state.force_decision = True
                st.rerun()
        if brand_name in DEEP_INSIGHT_DATA:
            render_deep_insight_modal(DEEP_INSIGHT_DATA[brand_name])
        return

    # ====== 2) autorefresh — 자동재생 중이면 0.5초마다 페이지 rerun ======
    is_playing = st.session_state.play_start_time is not None
    if is_playing:
        st_autorefresh(interval=500, limit=100, key='play_refresh')

    # ====== 3) 현재 day / show_decision 계산 ======
    if is_playing:
        elapsed = time.time() - st.session_state.play_start_time
        # 각 step 마다 STEP_INTERVAL_SEC 초씩
        step_idx_float = elapsed / STEP_INTERVAL_SEC
        step_idx = int(step_idx_float)
        if step_idx >= len(STEPS):
            # 모든 step 끝남 → 결정 팝업 표시 후 자동재생 종료
            current_day = 90
            # Day 90 카드 그리드를 한 cycle 보여준 후 결정 팝업
            if elapsed >= len(STEPS) * STEP_INTERVAL_SEC + DECISION_DELAY_SEC:
                show_decision = True
                st.session_state.play_start_time = None
                st.session_state.manual_day = 90
                st.session_state.force_decision = True
            else:
                show_decision = False
        else:
            current_day = STEPS[step_idx]
            show_decision = False
    else:
        current_day = st.session_state.manual_day
        show_decision = st.session_state.force_decision

    # ====== 4) Header ======
    status_text = '🚨 결정의 순간' if show_decision else ('🎬 자동 재생 중' if is_playing else '⏸ 대기')
    st.markdown(f"""
<div class='demo-header-compact'>
<div style='display:flex;align-items:center;gap:12px;'>
<div style='color:#FFFFFF;font-weight:800;font-size:16px;'>🛡️ ON-Trust Shield · CJ Frontier Labs 6기</div>
<div style='color:#8B96AB;font-size:10px;'>15개 신생 식당/식품 브랜드 90일 모니터링</div>
</div>
<div style='display:flex;align-items:center;gap:10px;'>
<div style='color:#FFD700;font-size:14px;font-weight:800;font-family:JetBrains Mono;'>Day {current_day} / 90</div>
<div style='color:#FF3B30;font-size:11px;font-weight:700;'>{status_text}</div>
</div>
</div>
""", unsafe_allow_html=True)

    # ====== 5) 컨트롤 + 진행 바 (슬라이더 대신 HTML 프로그레스바) ======
    c1, c2, c3, c4, c5 = st.columns([1.2, 1, 1, 1, 1.2])
    with c1:
        if st.button('▶️ Play', use_container_width=True, type='primary', key='btn_play'):
            st.session_state.play_start_time = time.time()
            st.session_state.manual_day = 1
            st.session_state.force_decision = False
            st.session_state.detail_brand = None
            st.rerun()
    with c2:
        if st.button('⏸ Pause', use_container_width=True, key='btn_pause'):
            # 현재 day 를 manual_day 로 고정한 채 자동재생 종료
            st.session_state.manual_day = current_day
            st.session_state.play_start_time = None
            st.rerun()
    with c3:
        if st.button('⏮ Reset', use_container_width=True, key='btn_reset'):
            st.session_state.play_start_time = None
            st.session_state.manual_day = 1
            st.session_state.force_decision = False
            st.rerun()
    with c4:
        if st.button('⏭ Day 90', use_container_width=True, key='btn_d90'):
            st.session_state.play_start_time = None
            st.session_state.manual_day = 90
            st.session_state.force_decision = True
            st.rerun()
    with c5:
        if st.button('🔄 카드 그리드', use_container_width=True, key='btn_grid'):
            st.session_state.force_decision = False
            st.rerun()

    # 진행 바 (HTML)
    progress_pct = (current_day / 90) * 100
    if show_decision:
        progress_pct = 100
    marker_html = ''
    for d in STEPS:
        cls = 'active' if current_day >= d else ''
        marker_html += f"<span class='{cls}'>D{d}</span>"
    st.markdown(f"""
<div class='day-progress-wrap'>
<div class='day-progress-bar-bg'>
<div class='day-progress-bar-fill' style='width:{progress_pct:.1f}%;'></div>
</div>
<div class='day-markers'>{marker_html}</div>
</div>
""", unsafe_allow_html=True)

    # ====== 6) 브랜드 상태 + 그룹화 ======
    brands = generate_brands_v2()
    items = []
    for b in brands:
        state = get_brand_at_day(b, current_day)
        items.append({'brand': b, 'state': state})

    groups = {'normal': [], 'monitoring': [], 'danger': [], 'abuse': []}
    for it in items:
        groups[it['state']['status']].append(it)
    for k in groups:
        groups[k].sort(key=lambda x: -x['state']['trust'])

    # ====== 7) 메인 콘텐츠 ======
    if show_decision:
        _render_decision_popup(items, groups)
    else:
        _render_grid(groups)
        _render_signature_timeline(brands, current_day)

    # ====== 푸터 ======
    st.markdown("""
<div style='display:flex;gap:8px;margin-top:6px;
color:#8B96AB;font-size:10px;font-family:JetBrains Mono;'>
<span style='background:#131829;border:1px solid #2A3447;padding:4px 8px;border-radius:4px;'>
HeteroSAGE PR-AUC <b style='color:#34C759'>0.2385</b></span>
<span style='background:#131829;border:1px solid #2A3447;padding:4px 8px;border-radius:4px;'>
Stacking Recall <b style='color:#34C759'>50.9%</b> (+26.3%p)</span>
<span style='background:#131829;border:1px solid #2A3447;padding:4px 8px;border-radius:4px;'>
YelpChi ROC <b style='color:#FFD700'>0.845</b></span>
<span style='background:#131829;border:1px solid #2A3447;padding:4px 8px;border-radius:4px;'>
Yelp Open <b style='color:#FF8C00'>100:1</b> 비대칭</span>
</div>
""", unsafe_allow_html=True)


def _render_grid(groups):
    cols = st.columns(4)
    info = [
        ('normal', '🟢 정상 운영', 'green', cols[0]),
        ('monitoring', '🟡 모니터링', 'yellow', cols[1]),
        ('danger', '🟠 위험', 'orange', cols[2]),
        ('abuse', '🔴 어뷰징 확정', 'red', cols[3]),
    ]
    for key, label, css, col in info:
        with col:
            members = groups[key]
            count = len(members)
            st.markdown(f"<div class='group-header {css}'>{label} <b>({count})</b></div>",
                        unsafe_allow_html=True)
            if not members:
                st.markdown("<div class='empty-slot'>— 해당 없음 —</div>", unsafe_allow_html=True)
            else:
                # GNN 그래프 공간 확보 위해 카드 수 축소: 정상/모니터링 3, 위험/어뷰징 2
                max_show = 3 if key in ('normal', 'monitoring') else 2
                for item in members[:max_show]:
                    highlight = (key == 'abuse')
                    st.markdown(render_card_compact(item['brand'], item['state'],
                                                    highlight=highlight),
                                unsafe_allow_html=True)
                if count > max_show:
                    st.markdown(f"<div class='empty-slot'>+ {count - max_show}개 (스택)</div>",
                                unsafe_allow_html=True)


def _render_signature_timeline(brands, day):
    """GNN 추론 그래프 시각화 — Heterogeneous Force-directed Network (50K 실측 기반).

    실제 unified_analysis_50k.py 결과 기반:
      - 노드: user=37,481 / review=50,000 / product=200
      - 기본골격 엣지(2): writes=50K, targets=50K
      - 커스텀 시그니처 엣지(4): rating_extreme_promoter=3,332,
        rating_extreme_terrorist=334, text_extreme=351, user_co_burst=70,532
    HeteroSAGE 가 학습한 임베딩 공간을 2D 로 투영했을 때의 community structure 를
    재현 — 클러스터를 이루는 노드들과 어디에도 속하지 않는 outlier 노드들이 공존.
    """
    import numpy as np
    abuse_b = next(b for b in brands if b['tier'] == 'abuse_confirmed')
    rng = np.random.default_rng(42)
    fig = go.Figure()

    # === 0) 엣지 컬러 팔레트 — 2 base + 4 custom ===
    # 시각적 hierarchy:
    #   기본 골격 (base) → 얇고 muted 한 backbone, 차가운 회색-청색 톤
    #   커스텀 시그니처 (custom) → 두껍고 saturate 한 vivid 톤 + 클러스터 강조
    EDGE_COLORS = {
        # 기본 골격 (2) — backbone 느낌
        'writes':                    'rgba(170,185,210,{a})',   # 차분한 silver-gray
        'targets':                   'rgba(120,170,220,{a})',   # 차분한 light blue
        # 커스텀 시그니처 (4) — vivid pop
        'rating_extreme_promoter':   'rgba(255,59,48,{a})',     # 빨강
        'rating_extreme_terrorist':  'rgba(255,200,0,{a})',     # 형광 노랑
        'text_extreme':              'rgba(210,110,255,{a})',   # 형광 보라
        'user_co_burst':             'rgba(255,60,170,{a})',    # 핫핑크 마젠타
    }
    # 엣지 width hierarchy
    BASE_W = 0.35       # 기본 골격: 매우 얇게
    CUSTOM_W = 1.05     # 커스텀: 약 3배 두껍게 → 눈에 띄게

    # === 1) 클러스터 정의 ===
    # Day 진행에 따라 어뷰징 클러스터 노드 수 증가
    day_factor = min(1.0, max(0.0, (day - 14) / 70.0))  # 0.0(Day≤14) → 1.0(Day≥84)
    abuse_user_n = int(70 + 110 * day_factor) if day >= 30 else int(15 + 25 * day_factor)
    abuse_rev_n = int(70 + 130 * day_factor) if day >= 30 else int(20 + 30 * day_factor)

    # 클러스터 — 7개 군집 (가로 2 row × 3-4 col).
    # 노드 색: 2 base node type 색계 (user=녹/마젠타, product=주황) + 4 review 시그니처 색 (정상/Promoter/Terrorist/Text_extreme)
    # 클러스터 — 실제 t-SNE/UMAP 임베딩 투영처럼 organic overlap, off-grid.
    # rx/ry 로 타원 클러스터, 일부 클러스터는 다른 클러스터에 embed/bleed 됨.
    clusters = [
        # === 정상 도메인 (상단 — 일부 겹침) ===
        # 정상 사용자 ↔ 정상 리뷰: writes 엣지로 강하게 묶여 cluster boundary 가 흐릿
        dict(cx=-3.6, cy=1.55, rx=1.55, ry=1.30, n=130, color='#34C759',
             edge=EDGE_COLORS['writes'].format(a=0.20), name='정상 사용자',
             size=6, role='user_normal', edge_kind='base'),
        dict(cx=-0.5, cy=1.35, rx=1.85, ry=1.55, n=160, color='#5DADE2',
             edge=EDGE_COLORS['writes'].format(a=0.20), name='정상 리뷰',
             size=5, role='review_normal', edge_kind='base'),
        # Text-extreme 은 정상 리뷰 상단에 박혀있음 (review subtype)
        dict(cx=0.9, cy=2.45, rx=0.75, ry=0.60, n=42, color='#BF5AF2',
             edge=EDGE_COLORS['text_extreme'].format(a=0.60),
             name='Text-extreme 리뷰', size=5,
             role='review_text_ext', edge_kind='custom'),
        # 타 카테고리 사용자 — 정상 리뷰의 우상단에 살짝 겹침
        dict(cx=2.6, cy=1.65, rx=1.40, ry=1.15, n=90, color='#7FCBC4',
             edge=EDGE_COLORS['writes'].format(a=0.18), name='타 카테고리 사용자',
             size=5, role='user_other', edge_kind='base'),
        # Terrorist — 정상-우측 경계의 다리 위치 (review_normal-product 사이)
        dict(cx=3.0, cy=0.05, rx=0.85, ry=0.70, n=38, color='#FFB800',
             edge=EDGE_COLORS['rating_extreme_terrorist'].format(a=0.60),
             name='Terrorist 리뷰 (z≤-1, ⭐1)',
             size=6, role='review_terrorist', edge_kind='custom'),
        # Product hub — 우측 (review 가 모이는 곳)
        dict(cx=4.8, cy=0.55, rx=0.85, ry=0.75, n=32, color='#FF8C00',
             edge=EDGE_COLORS['targets'].format(a=0.35), name='식당 (Product)',
             size=10, role='product', edge_kind='base'),
        # === 어뷰징 도메인 (하단 — 강한 overlap) ===
        # Workshop B 사용자 ↔ Promoter 리뷰: co_burst + writes 로 엉켜있음
        dict(cx=-3.8, cy=-1.55, rx=1.55, ry=1.30, n=abuse_user_n, color='#A23B72',
             edge=EDGE_COLORS['user_co_burst'].format(a=0.55),
             name='Workshop B 사용자 (의심)',
             size=7, role='user_abuse', edge_kind='custom'),
        dict(cx=-0.4, cy=-1.75, rx=2.00, ry=1.55, n=abuse_rev_n, color='#FF3B30',
             edge=EDGE_COLORS['rating_extreme_promoter'].format(a=0.55),
             name='Promoter 리뷰 (z≥+1, ⭐5)',
             size=6, role='review_promoter', edge_kind='custom'),
    ]

    # === 2) 노드 좌표 생성 (각 클러스터 내부 — 가우시안 + 타원 분포) ===
    all_pos = {}  # role -> list[(x,y)]
    for c in clusters:
        pts = []
        # 살짝 회전된 타원 (organic feel)
        rot = rng.uniform(-0.25, 0.25)
        cr, sr = np.cos(rot), np.sin(rot)
        for _ in range(c['n']):
            theta = rng.uniform(0, 2 * np.pi)
            rad = np.sqrt(rng.uniform(0, 1))
            # 타원 분포 (rx, ry 다름) + 가우시안 jitter
            lx = rad * c['rx'] * np.cos(theta)
            ly = rad * c['ry'] * np.sin(theta)
            # 회전
            x = c['cx'] + (cr * lx - sr * ly) + rng.normal(0, 0.06)
            y = c['cy'] + (sr * lx + cr * ly) + rng.normal(0, 0.06)
            pts.append((x, y))
        all_pos[c['role']] = pts

    # === 2b) Outlier / 비클러스터 노드 ===
    # 클러스터 외곽이나 빈 공간에 흩어져 있는 floating 노드들 (realistic)
    outlier_pos = {'user': [], 'review': [], 'product': []}
    n_user_out = 60
    n_review_out = 75
    n_prod_out = 7
    for _ in range(n_user_out):
        outlier_pos['user'].append((rng.uniform(-5.7, 6.2), rng.uniform(-3.1, 3.0)))
    for _ in range(n_review_out):
        outlier_pos['review'].append((rng.uniform(-5.7, 6.2), rng.uniform(-3.1, 3.0)))
    for _ in range(n_prod_out):
        outlier_pos['product'].append((rng.uniform(3.6, 6.0), rng.uniform(-1.6, 1.7)))

    # === 3) Intra-cluster 엣지 (kNN — 각 노드당 가까운 이웃 3~5개) ===
    def add_intra_edges(pts, color, k=4, width=0.4, max_edges=None):
        if len(pts) < 2:
            return
        arr = np.array(pts)
        edges_x, edges_y = [], []
        count = 0
        for i in range(len(arr)):
            # 거리 계산
            d = np.sum((arr - arr[i]) ** 2, axis=1)
            d[i] = np.inf
            nbrs = np.argsort(d)[:k]
            for j in nbrs:
                if j <= i:
                    continue
                edges_x.extend([arr[i, 0], arr[j, 0], None])
                edges_y.extend([arr[i, 1], arr[j, 1], None])
                count += 1
                if max_edges is not None and count >= max_edges:
                    break
            if max_edges is not None and count >= max_edges:
                break
        fig.add_trace(go.Scatter(x=edges_x, y=edges_y, mode='lines',
                                line=dict(color=color, width=width),
                                hoverinfo='skip', showlegend=False))

    # 각 클러스터 내부 intra edge — 클러스터의 dominant signature 색 + 종류별 width
    for c in clusters:
        pts = all_pos[c['role']]
        k = 5 if c['role'] in ('user_abuse', 'review_promoter') else 4
        w = CUSTOM_W if c['edge_kind'] == 'custom' else BASE_W
        add_intra_edges(pts, c['edge'], k=k, width=w)

    # === 4) Inter-cluster 엣지 (의미있는 메시지패싱) — 6 edge type 모두 distinct color ===
    def add_inter_edges(role_a, role_b, color, n_edges, width=0.4):
        a = all_pos[role_a]; b = all_pos[role_b]
        if not a or not b:
            return
        ex, ey = [], []
        for _ in range(min(n_edges, len(a) * len(b))):
            i = rng.integers(0, len(a))
            j = rng.integers(0, len(b))
            ex.extend([a[i][0], b[j][0], None])
            ey.extend([a[i][1], b[j][1], None])
        fig.add_trace(go.Scatter(x=ex, y=ey, mode='lines',
                                line=dict(color=color, width=width),
                                hoverinfo='skip', showlegend=False))

    # ┌─────────────────────────────────────────────────────────────┐
    # │  기본 골격 (BASE) : 얇고 muted — backbone 느낌                │
    # └─────────────────────────────────────────────────────────────┘
    c_writes = EDGE_COLORS['writes'].format(a=0.25)
    add_inter_edges('user_normal', 'review_normal', c_writes, 110, width=BASE_W)
    add_inter_edges('user_other', 'review_normal', c_writes, 70, width=BASE_W)
    add_inter_edges('user_other', 'review_text_ext', c_writes, 25, width=BASE_W)
    if abuse_user_n > 5:
        n_w = int(80 + 110 * day_factor)
        add_inter_edges('user_abuse', 'review_promoter', c_writes, n_w, width=BASE_W)

    c_targets = EDGE_COLORS['targets'].format(a=0.30)
    add_inter_edges('review_normal', 'product', c_targets, 80, width=BASE_W)
    add_inter_edges('review_text_ext', 'product', c_targets, 25, width=BASE_W)
    if day >= 30:
        n_t = int(60 + 90 * day_factor)
        add_inter_edges('review_promoter', 'product', c_targets, n_t, width=BASE_W)
    add_inter_edges('review_terrorist', 'product', c_targets, 25, width=BASE_W)

    # ┌─────────────────────────────────────────────────────────────┐
    # │  커스텀 시그니처 (CUSTOM) : 두껍고 vivid — 눈에 띄게         │
    # └─────────────────────────────────────────────────────────────┘
    # --- rating_extreme_promoter (custom #1) : review-review 빨강 ---
    if day >= 45:
        ra = all_pos['review_promoter']
        if len(ra) >= 2:
            ex, ey = [], []
            n_pp = int(60 + 80 * day_factor)
            for _ in range(n_pp):
                i, j = rng.integers(0, len(ra), 2)
                if i == j: continue
                ex.extend([ra[i][0], ra[j][0], None])
                ey.extend([ra[i][1], ra[j][1], None])
            fig.add_trace(go.Scatter(x=ex, y=ey, mode='lines',
                                    line=dict(color=EDGE_COLORS['rating_extreme_promoter'].format(a=0.55),
                                             width=CUSTOM_W),
                                    hoverinfo='skip', showlegend=False))

    # --- rating_extreme_terrorist (custom #2) : review-review 노랑 ---
    rt = all_pos['review_terrorist']
    if len(rt) >= 2:
        ex, ey = [], []
        for _ in range(50):
            i, j = rng.integers(0, len(rt), 2)
            if i == j: continue
            ex.extend([rt[i][0], rt[j][0], None])
            ey.extend([rt[i][1], rt[j][1], None])
        fig.add_trace(go.Scatter(x=ex, y=ey, mode='lines',
                                line=dict(color=EDGE_COLORS['rating_extreme_terrorist'].format(a=0.70),
                                         width=CUSTOM_W),
                                hoverinfo='skip', showlegend=False))

    # --- text_extreme (custom #3) : review-review 보라 ---
    rte = all_pos['review_text_ext']
    if len(rte) >= 2:
        ex, ey = [], []
        for _ in range(55):
            i, j = rng.integers(0, len(rte), 2)
            if i == j: continue
            ex.extend([rte[i][0], rte[j][0], None])
            ey.extend([rte[i][1], rte[j][1], None])
        fig.add_trace(go.Scatter(x=ex, y=ey, mode='lines',
                                line=dict(color=EDGE_COLORS['text_extreme'].format(a=0.70),
                                         width=CUSTOM_W),
                                hoverinfo='skip', showlegend=False))

    # --- user_co_burst (custom #4) : user-user 핫핑크 (Day 60+) ---
    if day >= 60:
        ua = all_pos['user_abuse']
        if len(ua) >= 3:
            ex, ey = [], []
            n_cb = int(80 + 100 * day_factor)
            for _ in range(n_cb):
                i, j = rng.integers(0, len(ua), 2)
                if i == j: continue
                ex.extend([ua[i][0], ua[j][0], None])
                ey.extend([ua[i][1], ua[j][1], None])
            fig.add_trace(go.Scatter(x=ex, y=ey, mode='lines',
                                    line=dict(color=EDGE_COLORS['user_co_burst'].format(a=0.60),
                                             width=CUSTOM_W),
                                    hoverinfo='skip', showlegend=False))

    # --- Outlier 노드 → 간헐적 sparse 연결 (base writes, 얇게) ---
    for ux, uy in outlier_pos['user'][:30]:
        if rng.random() < 0.55:
            tgt_pool = all_pos['review_normal'] + all_pos['review_text_ext']
            tx, ty = tgt_pool[rng.integers(0, len(tgt_pool))]
            fig.add_trace(go.Scatter(x=[ux, tx], y=[uy, ty], mode='lines',
                                    line=dict(color=c_writes, width=BASE_W),
                                    hoverinfo='skip', showlegend=False))

    # === 5) Outlier 노드 그리기 (먼저, 가장 옅게) ===
    if outlier_pos['user']:
        xs, ys = zip(*outlier_pos['user'])
        fig.add_trace(go.Scatter(
            x=list(xs), y=list(ys), mode='markers',
            marker=dict(size=4, color='#5C6478',
                       line=dict(color='rgba(255,255,255,0.1)', width=0.3),
                       opacity=0.55),
            name=f'고립 사용자 outlier ({len(xs)})',
            hovertext=[f'isolated user #{i} (저활동/신규)' for i in range(len(xs))],
            hoverinfo='text',
        ))
    if outlier_pos['review']:
        xs, ys = zip(*outlier_pos['review'])
        fig.add_trace(go.Scatter(
            x=list(xs), y=list(ys), mode='markers',
            marker=dict(size=4, color='#8B96AB', symbol='diamond',
                       line=dict(color='rgba(255,255,255,0.1)', width=0.3),
                       opacity=0.55),
            name=f'단발 리뷰 outlier ({len(xs)})',
            hovertext=[f'isolated review #{i}' for i in range(len(xs))],
            hoverinfo='text',
        ))
    if outlier_pos['product']:
        xs, ys = zip(*outlier_pos['product'])
        fig.add_trace(go.Scatter(
            x=list(xs), y=list(ys), mode='markers',
            marker=dict(size=8, color='#C19660', symbol='square',
                       line=dict(color='rgba(255,255,255,0.25)', width=0.6),
                       opacity=0.7),
            name=f'인접 카테고리 식당 ({len(xs)})',
            hoverinfo='skip',
        ))

    # === 6) 노드 그리기 (각 클러스터별) ===
    for c in clusters:
        pts = all_pos[c['role']]
        if not pts:
            continue
        xs, ys = zip(*pts)
        is_abuse = c['role'] in ('user_abuse', 'review_promoter')
        is_product = c['role'] == 'product'
        marker_kw = dict(
            size=c['size'] + (2 if is_abuse else 0),
            color=c['color'],
            line=dict(color='rgba(255,255,255,0.6)' if is_abuse or is_product else 'rgba(255,255,255,0.18)',
                     width=1.2 if is_abuse or is_product else 0.5),
            opacity=0.95 if is_abuse else 0.85,
        )
        fig.add_trace(go.Scatter(
            x=list(xs), y=list(ys), mode='markers',
            marker=marker_kw,
            name=f'{c["name"]} ({len(pts)})',
            hovertext=[f'{c["name"]} #{i}' for i in range(len(pts))],
            hoverinfo='text',
        ))

    # === 7) 어뷰징 클러스터 강조 — 점선 타원 + 라벨 ===
    if day >= 30:
        theta = np.linspace(0, 2 * np.pi, 80)
        for cluster_role in ('user_abuse', 'review_promoter'):
            c = next(c for c in clusters if c['role'] == cluster_role)
            cx, cy, rx, ry = c['cx'], c['cy'], c['rx'] * 1.18, c['ry'] * 1.22
            fig.add_trace(go.Scatter(
                x=cx + rx * np.cos(theta), y=cy + ry * np.sin(theta),
                mode='lines',
                line=dict(color='rgba(255,59,48,0.55)', width=1.5, dash='dash'),
                hoverinfo='skip', showlegend=False))

        fig.add_annotation(x=-3.8, y=-3.05, text='<b>🚨 Workshop B (co_burst)</b>',
                          showarrow=False, font=dict(color='#FF3B30', size=10, family='Inter'),
                          bgcolor='rgba(255,59,48,0.15)', bordercolor='#FF3B30',
                          borderwidth=1, borderpad=4)
        fig.add_annotation(x=-0.4, y=-3.15, text='<b>Promoter 리뷰 군집</b>',
                          showarrow=False, font=dict(color='#FF3B30', size=10, family='Inter'),
                          bgcolor='rgba(255,59,48,0.12)', bordercolor='#FF3B30',
                          borderwidth=1, borderpad=4)

    # === 8) Day 75+ 단일 추론 박스 (Day 85 미만일 때만, 그 이후엔 dual-brand 강조로 대체) ===
    if 75 <= day < 85:
        ts_key = day if day in MILESTONES else 75
        fig.add_annotation(x=5.7, y=2.7,
                          text=f'<b style="color:#FF3B30;">HeteroSAGE 추론 중...</b><br>'
                               f'대상: <b>{abuse_b["name"]}</b><br>'
                               f'Trust Score: <b>{abuse_b["trust_series"][ts_key]}</b>/100<br>'
                               f'시그니처 3개 임계 초과',
                          showarrow=False, align='left',
                          font=dict(color='#FFFFFF', size=10, family='Inter'),
                          bgcolor='rgba(255,59,48,0.20)',
                          bordercolor='#FF3B30', borderwidth=1, borderpad=8)

    # === 8b) Day 85+ : 어뷰징 확정 2개 브랜드 — 그래프 위에 한눈에 강조 ===
    if day >= 85:
        abuse_brands = [b for b in brands if b['tier'] == 'abuse_confirmed'][:2]
        # 브랜드를 product hub 근처에 prominent 하게 배치
        # 하나는 위쪽 (review 군집 가까이), 하나는 아래쪽 (어뷰징 user 군집과 연결)
        brand_anchors = [
            dict(x=4.6, y=1.05, label_x=5.95, label_y=1.55, label_anchor='left'),
            dict(x=5.25, y=-0.25, label_x=5.95, label_y=-0.75, label_anchor='left'),
        ]

        # 먼저 evidence trail 엣지 (브랜드 → user_abuse / review_promoter)
        ua = all_pos['user_abuse']
        rp = all_pos['review_promoter']
        for anchor, brand in zip(brand_anchors, abuse_brands):
            bx, by = anchor['x'], anchor['y']
            # co_burst evidence : 브랜드 → Workshop B 사용자 (소수 sample, 핫핑크 점선)
            if len(ua) > 0:
                for _ in range(7):
                    i = rng.integers(0, len(ua))
                    fig.add_trace(go.Scatter(
                        x=[bx, ua[i][0]], y=[by, ua[i][1]], mode='lines',
                        line=dict(color='rgba(255,60,170,0.55)', width=1.4, dash='dot'),
                        hoverinfo='skip', showlegend=False))
            # promoter evidence : 브랜드 → Promoter 리뷰 (빨강 점선)
            if len(rp) > 0:
                for _ in range(10):
                    i = rng.integers(0, len(rp))
                    fig.add_trace(go.Scatter(
                        x=[bx, rp[i][0]], y=[by, rp[i][1]], mode='lines',
                        line=dict(color='rgba(255,59,48,0.55)', width=1.5, dash='dot'),
                        hoverinfo='skip', showlegend=False))

        # 브랜드 마커 + 라벨 (위에 덮어 그리기 — 가장 prominent)
        for anchor, brand in zip(brand_anchors, abuse_brands):
            bx, by = anchor['x'], anchor['y']
            # 외곽 glow ring (3겹)
            for ring_size, ring_alpha in [(70, 0.10), (54, 0.16), (40, 0.28)]:
                fig.add_trace(go.Scatter(
                    x=[bx], y=[by], mode='markers',
                    marker=dict(size=ring_size, color=f'rgba(255,59,48,{ring_alpha})',
                               symbol='circle', line=dict(width=0)),
                    hoverinfo='skip', showlegend=False))
            # 중심 별 마커
            fig.add_trace(go.Scatter(
                x=[bx], y=[by], mode='markers',
                marker=dict(size=30, color='#FF3B30', symbol='star',
                           line=dict(color='#FFFFFF', width=2.8)),
                hovertext=f"⛔ {brand['name']} ({brand['category']})<br>"
                          f"Trust {brand['final_trust']}/100 — 어뷰징 확정",
                hoverinfo='text',
                name=f"⛔ {brand['name']}",
                showlegend=True))

            # 브랜드 라벨 박스 + leader line
            lx, ly = anchor['label_x'], anchor['label_y']
            fig.add_annotation(
                x=lx, y=ly,
                ax=bx, ay=by, axref='x', ayref='y',
                text=f'<b style="color:#FF3B30;font-size:11px;">⛔ {brand["name"]}</b><br>'
                     f'<span style="color:#C8D0DE;font-size:9px;">{brand["category"]} · 경희대</span><br>'
                     f'<span style="color:#FF3B30;font-size:10px;">Trust <b>{brand["final_trust"]}</b>/100</span>',
                showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=1.5,
                arrowcolor='#FF3B30',
                align='left',
                font=dict(color='#FFFFFF', size=9, family='Inter'),
                bgcolor='rgba(15,19,32,0.96)', bordercolor='#FF3B30',
                borderwidth=2, borderpad=6,
                xanchor=anchor['label_anchor'], yanchor='middle')

        # 상단 callout — "Day 90 최종 판별"
        fig.add_annotation(
            x=0.5, y=1.0, xref='paper', yref='paper',
            text=f'<b style="color:#FF3B30;font-size:13px;">🚨 Day {day} 최종 판별: 어뷰징 확정 2개 식당</b> '
                 f'<span style="color:#C8D0DE;font-size:10px;">'
                 f'— {abuse_brands[0]["name"]} · {abuse_brands[1]["name"]}'
                 f'</span>',
            showarrow=False, align='center',
            font=dict(color='#FFFFFF', size=12, family='Inter'),
            bgcolor='rgba(255,59,48,0.22)', bordercolor='#FF3B30',
            borderwidth=2, borderpad=8,
            xanchor='center', yanchor='top')

    # === 9) 엣지 타입 범례 (좌상단) — base 그룹 vs custom 그룹 시각 분리 ===
    legend_text = (
        '<b>엣지 타입 (실측 50K)</b><br>'
        '<span style="color:#9AA9C8;">━</span> '
        '<span style="color:#9AA9C8;font-size:8px;">기본골격</span> '
        '<span style="color:#AABAD8;">writes</span> (50,000)<br>'
        '<span style="color:#9AA9C8;">━</span> '
        '<span style="color:#9AA9C8;font-size:8px;">기본골격</span> '
        '<span style="color:#78AADC;">targets</span> (50,000)<br>'
        '<span style="color:#8B96AB;">────────────</span><br>'
        '<span style="color:#FF3B30;font-weight:900;">━━</span> '
        '<span style="color:#FF8A80;font-size:8px;">커스텀</span> '
        '<span style="color:#FF3B30;">rating_extreme_promoter</span> (3,332)<br>'
        '<span style="color:#FFC800;font-weight:900;">━━</span> '
        '<span style="color:#FFD955;font-size:8px;">커스텀</span> '
        '<span style="color:#FFC800;">rating_extreme_terrorist</span> (334)<br>'
        '<span style="color:#D26EFF;font-weight:900;">━━</span> '
        '<span style="color:#E6A8FF;font-size:8px;">커스텀</span> '
        '<span style="color:#D26EFF;">text_extreme</span> (351)<br>'
        '<span style="color:#FF3CAA;font-weight:900;">━━</span> '
        '<span style="color:#FF8AD0;font-size:8px;">커스텀</span> '
        '<span style="color:#FF3CAA;">user_co_burst</span> (70,532)'
    )
    fig.add_annotation(x=-5.6, y=3.1, text=legend_text,
                      showarrow=False, align='left',
                      font=dict(color='#FFFFFF', size=9, family='Inter'),
                      bgcolor='rgba(15,19,32,0.88)', bordercolor='#FF3B30',
                      borderwidth=1, borderpad=7, xanchor='left', yanchor='top')

    # === 10) 통계 박스 (하단) ===
    total_cluster = sum(len(all_pos[c['role']]) for c in clusters)
    total_out = len(outlier_pos['user']) + len(outlier_pos['review']) + len(outlier_pos['product'])
    user_total = (len(all_pos['user_normal']) + len(all_pos['user_abuse']) +
                  len(all_pos['user_other']) + len(outlier_pos['user']))
    review_total = (len(all_pos['review_normal']) + len(all_pos['review_promoter']) +
                    len(all_pos['review_terrorist']) + len(all_pos['review_text_ext']) +
                    len(outlier_pos['review']))
    prod_total = len(all_pos['product']) + len(outlier_pos['product'])
    fig.add_annotation(x=0.5, y=-0.02,
                      text=f'<b>그래프 (Day {day} 부분 샘플)</b>: '
                           f'총 노드 {total_cluster + total_out} '
                           f'(사용자 {user_total} · 리뷰 {review_total} · 식당 {prod_total}, '
                           f'그중 outlier {total_out})   ·   '
                           f'실 50K: user 37,481 / review 50,000 / product 200',
                      showarrow=False, font=dict(color='#8B96AB', size=9),
                      xref='paper', yref='paper',
                      bgcolor='rgba(19,24,41,0.7)', borderpad=4)

    fig.update_layout(
        plot_bgcolor='#0F1320', paper_bgcolor='#0F1320',
        font=dict(family='Inter', color='#FFFFFF', size=10),
        height=400, margin=dict(l=10, r=10, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                  range=[-6.0, 6.4]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                  range=[-3.4, 3.4]),
        legend=dict(orientation='h', y=1.08, x=0.5, xanchor='center',
                   font=dict(color='#FFFFFF', size=9), bgcolor='rgba(0,0,0,0)',
                   itemsizing='constant'),
        title=dict(text=f'<b>🧠 HeteroSAGE 임베딩 공간 — Community Cluster View (Day {day})</b>',
                  font=dict(color='#FFFFFF', size=12, family='Inter'),
                  x=0.5, xanchor='center', y=0.99),
        hoverlabel=dict(bgcolor='#1C2235', font=dict(color='#FFFFFF')),
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def _render_decision_popup(items, groups):
    sorted_items = sorted(items, key=lambda x: -x['state']['trust'])

    st.markdown(f"""
<div class='decision-popup-v3'>
<div style='display:flex;justify-content:space-between;align-items:center;gap:14px;'>
<div style='color:#FF3B30;font-size:15px;font-weight:800;white-space:nowrap;'>🚨 Day 90 — 투자 결정의 순간</div>
<div style='color:#C8D0DE;font-size:11px;line-height:1.4;flex:1;'>
🟢 정상 <b style='color:#34C759'>{len(groups["normal"])}</b>
· 🟡 모니터링 <b style='color:#FFB800'>{len(groups["monitoring"])}</b>
· 🟠 위험 <b style='color:#FF8C00'>{len(groups["danger"])}</b>
· 🔴 <b style='color:#FF3B30'>어뷰징 확정 {len(groups["abuse"])} 자동 탈락</b>
</div>
<div style='color:#FFFFFF;font-size:10px;font-family:JetBrains Mono;
background:rgba(255,59,48,0.18);padding:2px 8px;border-radius:100px;
border:1px solid rgba(255,59,48,0.35);white-space:nowrap;'>
CJ Investment · 2026.07.30</div>
</div>
</div>
""", unsafe_allow_html=True)

    cols = st.columns(4)
    info = [
        ('normal', '🟢 정상 — 통상 투자', 'green', cols[0]),
        ('monitoring', '🟡 모니터링', 'yellow', cols[1]),
        ('danger', '🟠 위험 — 보류 권고', 'orange', cols[2]),
        ('abuse', '🔴 어뷰징 확정 — 탈락', 'red', cols[3]),
    ]
    for key, label, css, col in info:
        with col:
            members = groups[key]
            count = len(members)
            st.markdown(f"<div class='group-header {css}'>{label} ({count})</div>",
                        unsafe_allow_html=True)
            if not members:
                st.markdown("<div class='empty-slot'>— 해당 없음 —</div>", unsafe_allow_html=True)
            else:
                max_show = 4 if key in ('normal', 'monitoring') else 3
                for item in members[:max_show]:
                    st.markdown(render_card_compact(item['brand'], item['state'],
                                                    show_insight=True,
                                                    highlight=(key == 'abuse')),
                                unsafe_allow_html=True)
                    if key == 'abuse' and item['brand']['name'] in DEEP_INSIGHT_DATA:
                        if st.button(f"🔍 상세 분석 — {item['brand']['name']}",
                                     key=f"deep_{item['brand']['name']}",
                                     use_container_width=True):
                            st.session_state.detail_brand = item['brand']['name']
                            st.rerun()
                if count > max_show:
                    st.caption(f'+ {count - max_show}개 더')

    st.markdown(f"""
<div style='background:linear-gradient(90deg,rgba(52,199,89,0.10),rgba(255,59,48,0.10));
border:1px solid #34C759;border-radius:6px;padding:6px 12px;
margin-top:4px;display:flex;gap:14px;align-items:center;'>
<div style='color:#FFFFFF;font-size:11px;font-weight:700;'>💡 단순 어뷰징 탐지를 넘어선 의사결정 도구</div>
<div style='color:#C8D0DE;font-size:10px;'>
<b style='color:#FF3B30'>{len(groups["abuse"])}건 자동 탈락 → ~100억 손실 방지</b> +
<b style='color:#34C759'>최우수 ROI 3개 우선 선정</b> ·
어뷰징 카드 클릭 → <b style='color:#FFD700'>상세 분석</b>
</div>
</div>
""", unsafe_allow_html=True)
