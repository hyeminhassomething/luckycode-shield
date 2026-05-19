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
                max_show = 5 if key in ('normal', 'monitoring') else 3
                for item in members[:max_show]:
                    highlight = (key == 'abuse')
                    st.markdown(render_card_compact(item['brand'], item['state'],
                                                    highlight=highlight),
                                unsafe_allow_html=True)
                if count > max_show:
                    st.markdown(f"<div class='empty-slot'>+ {count - max_show}개 (스택)</div>",
                                unsafe_allow_html=True)


def _render_signature_timeline(brands, day):
    abuse_b = next(b for b in brands if b['tier'] == 'abuse_confirmed')
    danger_b = next(b for b in brands if b['tier'] == 'danger')
    top_b = next(b for b in brands if b['tier'] == 'top_roi')

    fig = make_subplots(rows=1, cols=3,
                        subplot_titles=('🕐 S1 lift', '⭐ S2 z>+1 %', '👥 S3 작업장'),
                        horizontal_spacing=0.06)
    days_shown = [m for m in MILESTONES if m <= day] or [1]
    for b, color, name in [(abuse_b, '#FF3B30', abuse_b['name']),
                            (danger_b, '#FF8C00', danger_b['name']),
                            (top_b, '#34C759', top_b['name'])]:
        s1 = [b['sig1_series'][d] for d in days_shown]
        s2 = [b['sig2_series'][d]*100 for d in days_shown]
        s3 = [b['sig3_series'][d] for d in days_shown]
        for col_i, vals in enumerate([s1, s2, s3], 1):
            fig.add_trace(go.Scatter(x=days_shown, y=vals, mode='lines+markers',
                                    line=dict(color=color, width=2, shape='spline'),
                                    marker=dict(size=6),
                                    name=name, legendgroup=name,
                                    showlegend=(col_i == 1)),
                         row=1, col=col_i)
    fig.add_hline(y=1.81, line_dash='dash', line_color='#FF3B30', line_width=1, row=1, col=1)
    fig.add_hline(y=20, line_dash='dash', line_color='#FF3B30', line_width=1, row=1, col=2)
    fig.add_hline(y=5, line_dash='dash', line_color='#FF3B30', line_width=1, row=1, col=3)
    fig.update_layout(
        plot_bgcolor='#131829', paper_bgcolor='#131829',
        font=dict(family='Inter', color='#FFFFFF', size=8),
        height=140, margin=dict(l=28, r=10, t=22, b=14),
        legend=dict(orientation='h', y=-0.22, x=0.5, xanchor='center',
                   font=dict(color='#FFFFFF', size=8), bgcolor='rgba(0,0,0,0)'),
        hoverlabel=dict(bgcolor='#1C2235', font=dict(color='#FFFFFF')),
    )
    fig.update_xaxes(gridcolor='#1C2235', tickfont=dict(color='#8B96AB', size=8))
    fig.update_yaxes(gridcolor='#1C2235', tickfont=dict(color='#8B96AB', size=8))
    for ann in fig['layout']['annotations'][:3]:
        ann['font'] = dict(color='#FFFFFF', size=10, family='Inter')
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
