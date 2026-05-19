"""
ON-Trust Shield — CJ Frontier Labs Trust Monitoring Dashboard
ITDA 학술제 본선 시각화 대시보드 (Mission Control Center)

실행:
    streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.data_generator import (
    generate_brands, generate_brand_d_timeseries,
    generate_tsne_data, generate_suspect_users, generate_activity_feed,
    BASELINE_FAKE_RATE, BASELINE_50K, SIG1_THRESHOLD_LIFT,
    N_NODES, N_EDGES, STACKING_PR_AUC, STACKING_RECALL, RECALL_GAIN_PP,
    PR_AUC_HETEROSAGE, YELP_OPEN,
)
from utils.charts import (
    make_trust_gauge, make_sig1_chart, make_sig2_chart,
    make_sig3_chart, make_tsne_movement_chart, make_sparkline,
)
from utils.styles import GLOBAL_CSS
from utils.auto_demo import render_auto_demo

# ============================================
# Streamlit 설정
# ============================================
st.set_page_config(
    page_title='ON-Trust Shield',
    page_icon='🛡️',
    layout='wide',
    initial_sidebar_state='expanded',
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ============================================
# Sidebar — 본선 데모 vs 전체 분석
# ============================================
st.sidebar.markdown('# 🛡️ ON-Trust Shield')
st.sidebar.markdown('### luckycode · 본선 데모')
st.sidebar.markdown('---')

st.sidebar.caption('🎬 15개 브랜드 90일 시뮬레이션 (Play 버튼)')

# 본선 자동 재생 데모만 렌더하고 종료
render_auto_demo()
st.stop()


# ============================================
# Header (상세 분석 모드)
# ============================================
st.markdown("""
<div class='ots-header'>
    <div>
        <div class='ots-logo'>🛡️ ON-Trust Shield</div>
        <div class='ots-subtitle'>AI Agent for CJ Frontier Labs Trust Monitoring · powered by HeteroSAGE</div>
    </div>
    <div class='ots-live'>
        <span class='live-dot'></span>
        <span>LIVE · Day 45 · 2026.06.15 · 04:00 KST</span>
    </div>
    <div class='ots-user'>
        <span class='ots-bell'>🔔</span>
        <span class='ots-avatar'>김</span>
        <span>김OO · CJ Investment</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================
# Section 1: KPI Hero Strip
# ============================================
np.random.seed(42)
sparkline_data = [85, 87, 86, 88, 89, 87, 88]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class='kpi-card normal'>
        <div class='kpi-label'>모니터링 브랜드</div>
        <div class='kpi-value'>25</div>
        <div class='kpi-trend up'>↑ +6 vs 5기</div>
        <div class='kpi-detail'>프론티어랩스 6기 입주</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class='kpi-card normal'>
        <div class='kpi-label'>정상 (Trust ≥ 80)</div>
        <div class='kpi-value normal'>22</div>
        <div class='kpi-trend up'>안정 운영 · 88% 평균</div>
        <div class='kpi-detail'>지난 7일 변동 ±2</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class='kpi-card warning'>
        <div class='kpi-label'>모니터링 (Trust 60-79)</div>
        <div class='kpi-value warning'>2</div>
        <div class='kpi-trend down'>↓ 주의 관찰</div>
        <div class='kpi-detail'>Brand_W (76), Brand_X (72)</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <div class='kpi-card danger'>
        <div class='kpi-label'>위험 (Trust < 60) ⚠️</div>
        <div class='kpi-value danger'>1</div>
        <div class='kpi-trend down'>🚨 즉시 검토 권장</div>
        <div class='kpi-detail'>Brand_D · Day 45 · Trust 67</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# Section 2: Brand Grid (5x5)
# ============================================
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
st.markdown("""
<div class='section-title'>📊 25개 브랜드 실시간 모니터링</div>
<div class='section-subtitle'>각 카드 클릭 시 상세 분석 · 위험 카드는 자동 깜빡임</div>
""", unsafe_allow_html=True)

brands = generate_brands()

def render_brand_card(b):
    status_class = b['status']  # normal / monitoring / danger
    dot_class = status_class
    trust_class = '' if status_class == 'normal' else status_class
    change = b['trust_change']
    change_class = 'up' if change >= 0 else 'down'
    change_text = f"▲ +{change}" if change > 0 else (f"▼ {change}" if change < 0 else "—")
    warning_emoji = ' ⚠️' if b['status'] == 'danger' else ''
    sigs_class = 'danger' if b['status'] == 'danger' else ''
    progress_pct = min(b['day'] / 90 * 100, 100)
    progress_class = 'danger' if b['status'] == 'danger' else ''

    sigs_text = f"S1: {b['sig1_lift']:.2f}×  S2: {b['sig2_ratio']*100:.0f}%  S3: {b['sig3_users']}"

    return f"""
    <div class='brand-card {status_class}'>
        <div class='brand-row'>
            <div class='brand-name'>
                <span class='brand-status-dot {dot_class}'></span>{b['name']}{warning_emoji}
            </div>
            <div class='brand-day'>Day {b['day']}</div>
        </div>
        <div class='brand-trust {trust_class}'>{b['trust']}</div>
        <div class='brand-change {change_class}'>{change_text}</div>
        <div class='brand-sigs {sigs_class}'>{sigs_text}</div>
        <div class='brand-progress'>
            <div class='brand-progress-fill {progress_class}' style='width: {progress_pct}%;'></div>
        </div>
    </div>
    """

# 5 columns x 5 rows = 25
for row in range(5):
    cols = st.columns(5)
    for col_idx in range(5):
        idx = row * 5 + col_idx
        if idx >= len(brands): break
        with cols[col_idx]:
            st.markdown(render_brand_card(brands[idx]), unsafe_allow_html=True)


# ============================================
# Section 3: Brand_D Detail
# ============================================
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Brand_D 데이터
ts_data = generate_brand_d_timeseries()
tsne_data = generate_tsne_data()
suspect_users = generate_suspect_users()

# Detail Header (좌측 정보 + 우측 게이지)
col_info, col_gauge = st.columns([2, 1])
with col_info:
    st.markdown("""
    <div class='detail-header'>
        <div>
            <div class='detail-title'>🚨 Brand_D — 상세 분석</div>
            <div class='detail-subtitle'>Day 45 / 90 · 입주 2026.05.01 · Cosmetics·식품 기능성 카테고리 · 골든 타임 진행 중</div>
        </div>
        <div style='text-align: right;'>
            <div style='color: #FF3B30; font-size: 32px; font-weight: 800; font-family: Inter;'>67<span style='color: #8B96AB; font-size: 16px;'>/100</span></div>
            <div style='color: #FF3B30; font-size: 13px; font-family: JetBrains Mono;'>▼ -22 vs Day 30</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_gauge:
    st.plotly_chart(make_trust_gauge(67), use_container_width=True, config={'displayModeBar': False})

# Tabs
tab1, tab2, tab3 = st.tabs(['🔍 시그너처 분석', '📍 t-SNE 임베딩 이동', '📨 자동 검토 큐 (Slack)'])

# ============================================
# Tab 1: Signature Analysis
# ============================================
with tab1:
    col1, col2, col3 = st.columns(3)

    # 컬럼 1: 시그너처 1
    with col1:
        st.markdown("""
        <div class='sig-box'>
            <div class='sig-label'>시그너처 1 · 시간 차원</div>
            <div class='sig-title'>첫 90일 + 5점 농축도 추적</div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(make_sig1_chart(ts_data, threshold=SIG1_THRESHOLD_LIFT),
                       use_container_width=True, config={'displayModeBar': False})
        st.markdown("""
        <div class='sig-bottom'>
            <div class='sig-bottom-value'>현재 (Day 45): 2.06× baseline</div>
            <div class='sig-bottom-detail'>Baseline: 13.22% · 현재: 27.2%</div>
            <div class='sig-bottom-ref'>↑ 본 연구 §2.2.2 검증된 임계값 1.81× 초과</div>
        </div>
        """, unsafe_allow_html=True)

    # 컬럼 2: 시그너처 2
    with col2:
        st.markdown("""
        <div class='sig-box'>
            <div class='sig-label red'>시그너처 2 · 별점 차원</div>
            <div class='sig-title'>z > +1 + 5점 분포 비대칭</div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(make_sig2_chart(ts_data),
                       use_container_width=True, config={'displayModeBar': False})
        st.markdown("""
        <div class='sig-bottom'>
            <div class='sig-bottom-value'>27.1% (3.39× 정상)</div>
            <div class='sig-bottom-detail'>rating_extreme_promoter 엣지 28개 (시점 ↑)</div>
            <div class='sig-bottom-ref'>↑ 본 연구 §2.4.3 그래프 인코딩</div>
        </div>
        """, unsafe_allow_html=True)

    # 컬럼 3: 시그너처 3
    with col3:
        st.markdown("""
        <div class='sig-box'>
            <div class='sig-label purple'>시그너처 3 · 사용자 차원</div>
            <div class='sig-title'>Promoter 작업장 패턴</div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(make_sig3_chart(suspect_users),
                       use_container_width=True, config={'displayModeBar': False})
        st.markdown("""
        <div class='sig-bottom'>
            <div class='sig-bottom-value'>🚨 작업장 사용자: 12명 (임계값 5명)</div>
            <div class='sig-bottom-detail'>co_burst 엣지 47개 · Workshop B 패턴</div>
            <div class='sig-bottom-ref'>↑ 본 연구 §5.7 Yelp Open 107:1 비대칭</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# Tab 2: t-SNE Movement
# ============================================
with tab2:
    col_chart, col_info = st.columns([3, 1])
    with col_chart:
        st.plotly_chart(make_tsne_movement_chart(tsne_data),
                       use_container_width=True, config={'displayModeBar': False})
    with col_info:
        st.markdown("""
        <div class='sig-box'>
            <div class='sig-label purple'>이동 분석</div>
            <div class='sig-title'>Brand_D 궤적 14일</div>
            <div style='color: #C8D0DE; font-size: 13px; line-height: 1.8;'>
                <div>📍 <b style='color: #FFFFFF;'>이동 거리:</b> 0.34 단위</div>
                <div>⚡ <b style='color: #FFFFFF;'>일평균 속도:</b> 0.024</div>
                <div>📊 <b style='color: #FFFFFF;'>정상 속도:</b> &lt; 0.005</div>
                <div>🎯 <b style='color: #FFFFFF;'>목표 클러스터:</b> Promoter</div>
            </div>
            <div class='sig-bottom' style='margin-top: 14px;'>
                <div class='sig-bottom-value'>4.8× 정상 속도</div>
                <div class='sig-bottom-detail'>Day 30 침투 시점 가속화</div>
                <div class='sig-bottom-ref'>↑ §5.8 t-SNE 임베딩 시각화 §5.9 Suspect 클러스터</div>
            </div>
        </div>

        <div class='sig-box' style='margin-top: 14px;'>
            <div class='sig-label'>마일스톤</div>
            <div style='color: #C8D0DE; font-size: 12px; line-height: 1.8; font-family: JetBrains Mono;'>
                <div>Day  1 → (0.12, 0.08) <span style='color:#34C759;'>정상</span></div>
                <div>Day 14 → (0.18, 0.15) <span style='color:#34C759;'>정상</span></div>
                <div>Day 30 → (0.28, 0.22) <span style='color:#FFB800;'>침투</span></div>
                <div>Day 40 → (0.52, 0.45) <span style='color:#FFB800;'>가속</span></div>
                <div>Day 45 → (0.78, 0.65) <span style='color:#FF3B30;'>경보</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# Tab 3: Auto Review Queue (Slack Alert)
# ============================================
with tab3:
    col_slack, col_table = st.columns([1, 1])

    with col_slack:
        slack_html = """
<!DOCTYPE html>
<html><head><meta charset='utf-8'><style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
body { margin: 0; padding: 0; background: transparent; font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; }
.slack-card {
    background: #1A1D26;
    border: 1px solid #2A3447;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.5);
    color: #E8EDF5;
    max-width: 100%;
    box-sizing: border-box;
}
.slack-header { display: flex; align-items: center; gap: 12px; padding-bottom: 12px; border-bottom: 1px solid #2A3447; margin-bottom: 14px; }
.channel { color: #8B96AB; font-size: 14px; font-weight: 600; }
.timestamp { color: #8B96AB; font-size: 12px; margin-left: auto; font-family: 'JetBrains Mono', monospace; }
.bot-row { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.bot-icon { width: 32px; height: 32px; background: linear-gradient(135deg, #BF5AF2, #0A84FF); border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; font-size: 16px; }
.bot-name { font-weight: 700; color: #FFFFFF; font-size: 14px; }
.bot-tag { background: #2A3447; color: #8B96AB; padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; }
.alert-title { font-size: 16px; font-weight: 800; color: #FF3B30; margin: 8px 0 12px 0; letter-spacing: -0.3px; }
.row { color: #C8D0DE; font-size: 13px; margin: 6px 0; line-height: 1.55; }
.row b { color: #FFFFFF; font-weight: 600; }
.red { color: #FF3B30; font-weight: 700; }
.section-title { color: #FFB800; font-size: 12px; font-weight: 700; margin: 14px 0 6px 0; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px; }
.btn-row { display: flex; gap: 8px; margin-top: 14px; padding-top: 14px; border-top: 1px solid #2A3447; }
.btn { background: #2A3447; color: #FFFFFF; padding: 8px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; border: none; flex: 1; text-align: center; cursor: pointer; }
.btn.primary { background: linear-gradient(135deg, #0A84FF, #BF5AF2); }
.footer { color: #5B6478; font-size: 11px; margin-top: 12px; padding-top: 10px; border-top: 1px solid #2A3447; font-style: italic; }
</style></head><body>
<div class='slack-card'>
    <div class='slack-header'>
        <span class='channel'># cj-investment-alerts</span>
        <span class='timestamp'>2026.06.15 · 04:00 KST</span>
    </div>
    <div class='bot-row'>
        <span class='bot-icon'>🛡️</span>
        <span class='bot-name'>ON-Trust Shield Bot</span>
        <span class='bot-tag'>APP</span>
    </div>
    <div class='alert-title'>🚨 ALERT: Brand_D 위험 신호 감지</div>

    <div class='row'>📊 <b>Trust Score:</b> 67 / 100 (▼ 22 vs Day 30)</div>
    <div class='row'>📅 <b>Day 45 / 90</b> · 골든 타임 진행 중</div>

    <div class='section-title'>⚠️ 3개 시그너처 모두 임계값 초과</div>

    <div class='row'>🕐 <b>시그너처 1 (시간):</b></div>
    <div class='row'>&nbsp;&nbsp;└ 첫 90일+5점 lift <span class='red'>2.06×</span> (임계값 1.81×)</div>

    <div class='row'>⭐ <b>시그너처 2 (별점):</b></div>
    <div class='row'>&nbsp;&nbsp;└ z &gt;+1+5점 비율 <span class='red'>27.1%</span> (정상 대비 3.39×)</div>
    <div class='row'>&nbsp;&nbsp;└ rating_extreme_promoter 엣지 <span class='red'>28개</span></div>

    <div class='row'>👥 <b>시그너처 3 (사용자):</b></div>
    <div class='row'>&nbsp;&nbsp;└ 작업장 사용자 <span class='red'>12명</span> (임계값 5명)</div>
    <div class='row'>&nbsp;&nbsp;└ Workshop B 패턴 · co_burst 엣지 47개</div>

    <div class='row'>📍 <b>t-SNE 위치:</b></div>
    <div class='row'>&nbsp;&nbsp;└ Promoter 클러스터 +0.34 이동 (정상 대비 4.8×)</div>

    <div class='section-title'>🎯 자동 추천 조치</div>
    <div class='row'>✅ 의심 리뷰 <b>47건</b> 검토 큐 생성</div>
    <div class='row'>✅ Workshop B <b>12명</b> 우선 검토 권장</div>
    <div class='row'>✅ MD <b>7일 이내</b> 검토 권장</div>

    <div class='btn-row'>
        <div class='btn primary'>📋 검토 큐 열기</div>
        <div class='btn'>🚫 작업자 차단</div>
    </div>

    <div class='footer'>by Trust Sentinel Agent · 자동 발송 · 모델: HeteroSAGE PR-AUC 0.2385 ± 0.0217</div>
</div>
</body></html>
"""
        from streamlit.components.v1 import html as components_html
        components_html(slack_html, height=820, scrolling=False)

    with col_table:
        st.markdown("""
        <div class='sig-box'>
            <div class='sig-label red'>📋 검토 큐 (47명)</div>
            <div class='sig-title'>Workshop B 12명 우선 표시</div>
        </div>
        """, unsafe_allow_html=True)

        # Workshop B 표
        workshop = [u for u in suspect_users if u['cluster'] == 'Workshop_B']
        df_workshop = pd.DataFrame([{
            'User ID': u['user_id'],
            '리뷰': u['reviews'],
            '첫 90일%': f"{u['first_90d_pct']}%",
            'avg z': u['avg_z'],
            'co_burst': u['co_burst'],
            '위험도': min(60 + u['co_burst']*4 + int(u['avg_z']*10), 99),
        } for u in workshop])
        df_workshop = df_workshop.sort_values('위험도', ascending=False).reset_index(drop=True)

        st.dataframe(
            df_workshop,
            use_container_width=True, hide_index=True,
            column_config={
                '위험도': st.column_config.ProgressColumn(
                    '위험도', format='%d', min_value=0, max_value=100,
                ),
                'avg z': st.column_config.NumberColumn(format='%.2f'),
            },
        )

        # 단독 의심 요약
        single = [u for u in suspect_users if u['cluster'] == 'Single']
        st.markdown(f"""
        <div class='sig-bottom' style='margin-top: 12px;'>
            <div class='sig-bottom-detail' style='color: #FFB800;'>+ 단독 의심 사용자 {len(single)}명 (펼치기 →)</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"단독 의심 {len(single)}명 펼치기"):
            df_single = pd.DataFrame([{
                'User ID': u['user_id'],
                '리뷰': u['reviews'],
                '첫 90일%': f"{u['first_90d_pct']}%",
                'avg z': u['avg_z'],
                'co_burst': u['co_burst'],
            } for u in single])
            st.dataframe(df_single, use_container_width=True, hide_index=True)


# ============================================
# Section 4: Activity Feed
# ============================================
feed = generate_activity_feed()
feed_text = '  |  '.join(feed) + '  |  '
feed_text = feed_text * 3  # 무한 스크롤처럼 보이게 반복

st.markdown(f"""
<div class='activity-bar'>
    <div class='activity-label'>
        <span class='activity-dot'></span>
        Agent ACTIVE
    </div>
    <div style='flex: 1; overflow: hidden;'>
        <div class='activity-feed-text'>{feed_text}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================
# Footer (모델 정보)
# ============================================
col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    st.markdown(f"""
    <div style='background: #131829; border: 1px solid #2A3447; border-radius: 10px; padding: 14px;'>
        <div style='color: #8B96AB; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px;'>본 연구 모델</div>
        <div style='color: #FFFFFF; font-weight: 700; font-size: 14px; margin-top: 6px;'>HeteroSAGE (Hetero, 3 nodes × 6 edges)</div>
        <div style='color: #8B96AB; font-size: 11px; margin-top: 2px;'>Multi-seed PR-AUC {PR_AUC_HETEROSAGE[0]:.4f} ± {PR_AUC_HETEROSAGE[1]:.4f}</div>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    st.markdown(f"""
    <div style='background: #131829; border: 1px solid #2A3447; border-radius: 10px; padding: 14px;'>
        <div style='color: #8B96AB; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px;'>Stacking Ensemble</div>
        <div style='color: #FFFFFF; font-weight: 700; font-size: 14px; margin-top: 6px;'>PR-AUC {STACKING_PR_AUC:.4f} · Recall {STACKING_RECALL*100:.1f}%</div>
        <div style='color: #34C759; font-size: 11px; margin-top: 2px;'>↑ Recall +{RECALL_GAIN_PP}%p · 추가 탐지 fake 111건</div>
    </div>
    """, unsafe_allow_html=True)
with col_c:
    st.markdown(f"""
    <div style='background: #131829; border: 1px solid #2A3447; border-radius: 10px; padding: 14px;'>
        <div style='color: #8B96AB; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px;'>그래프 통계 (50K)</div>
        <div style='color: #FFFFFF; font-weight: 700; font-size: 14px; margin-top: 6px;'>{N_NODES['review']:,} 리뷰 · {N_NODES['user']:,} 사용자 · {N_NODES['product']} 식당</div>
        <div style='color: #8B96AB; font-size: 11px; margin-top: 2px;'>엣지 {sum(N_EDGES.values()):,}개 · co_burst {N_EDGES['user_co_burst']:,}</div>
    </div>
    """, unsafe_allow_html=True)
with col_d:
    st.markdown(f"""
    <div style='background: #131829; border: 1px solid #2A3447; border-radius: 10px; padding: 14px;'>
        <div style='color: #8B96AB; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px;'>외부 일반화</div>
        <div style='color: #FFFFFF; font-weight: 700; font-size: 14px; margin-top: 6px;'>YelpChi ROC 0.845 · Yelp Open 8년 갭</div>
        <div style='color: #8B96AB; font-size: 11px; margin-top: 2px;'>Promoter:Terrorist 비율 ~{YELP_OPEN['ratio']}:1</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
