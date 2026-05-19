"""ON-Trust Shield — Plotly 차트 함수."""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DARK_LAYOUT = dict(
    plot_bgcolor='#131829',
    paper_bgcolor='#131829',
    font=dict(family='Inter, Pretendard, sans-serif', color='#FFFFFF', size=11),
    margin=dict(l=40, r=20, t=30, b=40),
    xaxis=dict(gridcolor='#1C2235', zerolinecolor='#2A3447', linecolor='#2A3447',
               tickfont=dict(color='#8B96AB', size=10)),
    yaxis=dict(gridcolor='#1C2235', zerolinecolor='#2A3447', linecolor='#2A3447',
               tickfont=dict(color='#8B96AB', size=10)),
    hoverlabel=dict(bgcolor='#1C2235', bordercolor='#FF3B30',
                   font=dict(color='#FFFFFF', family='JetBrains Mono')),
)


def make_trust_gauge(value, max_value=100):
    """Brand D 신뢰도 게이지 (67/100)."""
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': '<b>Trust Score</b>', 'font': {'size': 12, 'color': '#8B96AB'}},
        number={'font': {'size': 44, 'color': '#FF3B30', 'family': 'Inter'}, 'suffix': '/100'},
        delta={'reference': 89, 'decreasing': {'color': '#FF3B30'}, 'increasing': {'color': '#34C759'},
               'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#8B96AB',
                    'tickfont': {'color': '#8B96AB', 'size': 10}},
            'bar': {'color': '#FF3B30', 'thickness': 0.3},
            'bgcolor': '#1C2235',
            'borderwidth': 2,
            'bordercolor': '#2A3447',
            'steps': [
                {'range': [0, 60], 'color': 'rgba(255, 59, 48, 0.18)'},
                {'range': [60, 80], 'color': 'rgba(255, 184, 0, 0.15)'},
                {'range': [80, 100], 'color': 'rgba(52, 199, 89, 0.12)'},
            ],
            'threshold': {'line': {'color': '#FFB800', 'width': 3}, 'thickness': 0.85, 'value': 60},
        },
    ))
    fig.update_layout(**{**DARK_LAYOUT, 'height': 220, 'margin': dict(l=20, r=20, t=30, b=20)})
    return fig


def make_sig1_chart(ts_data, threshold=1.81):
    """시그니처 1: 첫 90일 + 5점 lift 시계열."""
    days = ts_data['days']
    sig1 = ts_data['sig1']

    # 색상 segment
    colors_arr = []
    for d in days:
        if d < 30: colors_arr.append('#8B96AB')
        elif d < 45: colors_arr.append('#FFB800')
        else: colors_arr.append('#FF3B30')

    fig = go.Figure()

    # Fill area
    fig.add_trace(go.Scatter(
        x=days, y=sig1, mode='lines',
        line=dict(color='rgba(255, 59, 48, 0.0)', width=0),
        fill='tozeroy', fillcolor='rgba(255, 59, 48, 0.08)',
        hoverinfo='skip', showlegend=False,
    ))

    # 3개 segment 라인
    for start, end, color, name in [(0, 30, '#8B96AB', '정상 (Day 1-29)'),
                                       (29, 45, '#FFB800', '침투 (Day 30-44)'),
                                       (44, 90, '#FF3B30', '경보 (Day 45+)')]:
        seg_days = days[start:end]
        seg_vals = sig1[start:end]
        fig.add_trace(go.Scatter(
            x=seg_days, y=seg_vals, mode='lines',
            line=dict(color=color, width=2.5, shape='spline'),
            name=name,
            hovertemplate='Day %{x}<br>lift: %{y:.2f}×<extra></extra>',
        ))

    # Baseline 1.0x
    fig.add_hline(y=1.0, line_dash='dot', line_color='#5B6478',
                  annotation_text='baseline 1.0×', annotation_position='right',
                  annotation_font=dict(color='#5B6478', size=10))

    # Warning threshold 1.81x
    fig.add_hline(y=threshold, line_dash='dash', line_color='#FF3B30',
                  annotation_text=f'§2.2.2 임계값 {threshold}×',
                  annotation_position='right',
                  annotation_font=dict(color='#FF3B30', size=10, family='JetBrains Mono'))

    # Day 45 marker
    fig.add_trace(go.Scatter(
        x=[45], y=[sig1[44]], mode='markers',
        marker=dict(color='#FF3B30', size=14, symbol='circle',
                   line=dict(color='#FFFFFF', width=2)),
        showlegend=False,
        hovertemplate='<b>🚨 Alert Triggered</b><br>Day 45<br>lift: %{y:.2f}×<extra></extra>',
    ))
    fig.add_annotation(
        x=45, y=sig1[44]+0.25, text='🚨 Alert',
        font=dict(color='#FF3B30', size=11, family='Inter'),
        showarrow=False,
    )

    fig.update_layout(**{**DARK_LAYOUT, 'height': 280, 'showlegend': False,
                         'xaxis': dict(**DARK_LAYOUT['xaxis'], title='Day', range=[0, 90]),
                         'yaxis': dict(**DARK_LAYOUT['yaxis'], title='lift (×baseline)', range=[0, 3.5])})
    return fig


def make_sig2_chart(ts_data):
    """시그니처 2: z 분포 + edge count 막대 (subplot 2개)."""
    fig = make_subplots(rows=2, cols=1, row_heights=[0.55, 0.45],
                        subplot_titles=('<b>z-score 분포 — 정상 vs Day 45</b>',
                                       '<b>rating_extreme_promoter 엣지 추이</b>'),
                        vertical_spacing=0.28)

    # ===== 상단: z 분포 =====
    z_normal = np.random.normal(0, 1, 5000)
    z_day45 = np.concatenate([
        np.random.normal(0, 1, 3500),
        np.random.normal(1.5, 0.5, 1300),
        np.random.normal(-1.8, 0.5, 200),
    ])

    fig.add_trace(go.Histogram(x=z_normal, name='정상 분포', histnorm='probability density',
                              nbinsx=60, marker=dict(color='rgba(139, 150, 171, 0.45)',
                              line=dict(color='#8B96AB', width=0.5)),
                              hovertemplate='z: %{x:.2f}<extra>정상</extra>'),
                 row=1, col=1)
    fig.add_trace(go.Histogram(x=z_day45, name='Day 45 분포', histnorm='probability density',
                              nbinsx=60, marker=dict(color='rgba(255, 59, 48, 0.55)',
                              line=dict(color='#FF3B30', width=0.5)),
                              hovertemplate='z: %{x:.2f}<extra>Day 45</extra>'),
                 row=1, col=1)

    # z > +1 영역 강조 (annotation 제거 - 글자 겹침 방지)
    fig.add_vrect(x0=1, x1=4, line_width=0,
                  fillcolor='rgba(255, 184, 0, 0.10)',
                  row=1, col=1)

    # 27.1% 박스를 차트 우측 안쪽으로 이동 (벗어나지 않게)
    fig.add_annotation(x=2.7, y=0.30, xref='x', yref='y',
                      text='<b>27.1%</b><br><span style="font-size:9px">3.39× 정상</span>',
                      font=dict(color='#FFFFFF', size=12, family='Inter'),
                      showarrow=False, align='center',
                      bgcolor='rgba(255, 59, 48, 0.85)', bordercolor='#FF3B30',
                      borderwidth=1, borderpad=6,
                      row=1, col=1)

    # ===== 하단: 엣지 카운트 =====
    sample_days = ts_data['edges_sample_days']
    counts = ts_data['edges_counts']
    bar_colors = []
    for d in sample_days:
        if d < 30: bar_colors.append('#5B6478')
        elif d < 44: bar_colors.append('#FFB800')
        else: bar_colors.append('#FF3B30')

    fig.add_trace(go.Bar(x=sample_days, y=counts,
                       marker=dict(color=bar_colors,
                                  line=dict(color='#0A0E1A', width=1)),
                       text=[f'<b>{c}</b>' for c in counts], textposition='outside',
                       textfont=dict(color='#FFFFFF', size=10, family='Inter'),
                       hovertemplate='Day %{x}<br>엣지 %{y}개<extra></extra>',
                       showlegend=False),
                 row=2, col=1)

    fig.update_xaxes(title='', gridcolor='#1C2235', tickfont=dict(color='#8B96AB', size=10),
                    range=[-4, 4.5], row=1, col=1)
    fig.update_yaxes(title='density', gridcolor='#1C2235', tickfont=dict(color='#8B96AB', size=10),
                    range=[0, 0.55], row=1, col=1)
    fig.update_xaxes(title='Day', gridcolor='#1C2235', tickfont=dict(color='#8B96AB', size=10), row=2, col=1)
    fig.update_yaxes(title='엣지 수', gridcolor='#1C2235', tickfont=dict(color='#8B96AB', size=10),
                    range=[0, 34], row=2, col=1)

    fig.update_layout(plot_bgcolor='#131829', paper_bgcolor='#131829',
                     font=dict(family='Inter', color='#FFFFFF', size=11),
                     height=460, margin=dict(l=40, r=20, t=55, b=40),
                     barmode='overlay',
                     legend=dict(orientation='h', y=-0.12, x=0.5, xanchor='center',
                                font=dict(color='#8B96AB', size=10),
                                bgcolor='rgba(0,0,0,0)'),
                     hoverlabel=dict(bgcolor='#1C2235', bordercolor='#FF3B30',
                                    font=dict(color='#FFFFFF')))
    # subplot title 색상
    for ann in fig['layout']['annotations'][:2]:  # subplot titles 만
        ann['font'] = dict(color='#FFFFFF', size=12, family='Inter')
    return fig


def make_sig3_chart(suspect_users):
    """시그니처 3: 작업장 사용자 산점도."""
    np.random.seed(123)
    # 정상 사용자 배경
    bg_x = np.random.uniform(-0.5, 2.0, 50)
    bg_y = np.random.uniform(-0.3, 1.5, 50)

    workshop = [u for u in suspect_users if u['cluster'] == 'Workshop_B']
    single = [u for u in suspect_users if u['cluster'] == 'Single']

    fig = go.Figure()

    # 배경 정상
    fig.add_trace(go.Scatter(x=bg_x, y=bg_y, mode='markers',
                            marker=dict(color='rgba(139, 150, 171, 0.18)', size=8,
                                       line=dict(width=0)),
                            name='정상 사용자', hoverinfo='skip', showlegend=True))

    # 단독 의심
    fig.add_trace(go.Scatter(
        x=[u['x'] for u in single], y=[u['y'] for u in single],
        mode='markers',
        marker=dict(color='#FFB800', size=11,
                   line=dict(color='#0A0E1A', width=1.5),
                   opacity=0.85),
        name=f'단독 의심 ({len(single)}명)',
        text=[f"{u['user_id']}<br>리뷰 {u['reviews']}개<br>avg_z {u['avg_z']}<br>co_burst {u['co_burst']}"
              for u in single],
        hovertemplate='%{text}<extra></extra>',
    ))

    # Workshop B (clustered)
    fig.add_trace(go.Scatter(
        x=[u['x'] for u in workshop], y=[u['y'] for u in workshop],
        mode='markers',
        marker=dict(color='#FF3B30', size=20,
                   line=dict(color='#FFFFFF', width=2),
                   opacity=0.95),
        name=f'Workshop B ({len(workshop)}명) ★',
        text=[f"<b>{u['user_id']}</b><br>리뷰 {u['reviews']}개<br>avg_z {u['avg_z']}<br>co_burst {u['co_burst']}"
              for u in workshop],
        hovertemplate='%{text}<extra></extra>',
    ))

    # co_burst 엣지 라인 (workshop 노드끼리)
    for i in range(len(workshop)):
        for j in range(i+1, len(workshop)):
            if np.random.random() > 0.6: continue
            fig.add_trace(go.Scatter(
                x=[workshop[i]['x'], workshop[j]['x']],
                y=[workshop[i]['y'], workshop[j]['y']],
                mode='lines',
                line=dict(color='rgba(255, 59, 48, 0.35)', width=0.8),
                hoverinfo='skip', showlegend=False,
            ))

    # 어노테이션
    fig.add_annotation(x=0.85, y=0.92, text='<b>Workshop B</b><br>12명 클러스터',
                      font=dict(color='#FF3B30', size=12, family='Inter'),
                      showarrow=True, arrowcolor='#FF3B30', arrowwidth=1.5,
                      ax=-50, ay=-30,
                      bgcolor='rgba(19, 24, 41, 0.85)', bordercolor='#FF3B30',
                      borderwidth=1, borderpad=4)
    fig.add_annotation(x=1.15, y=0.4, text='<b>단독 의심</b><br>35명',
                      font=dict(color='#FFB800', size=11, family='Inter'),
                      showarrow=False,
                      bgcolor='rgba(19, 24, 41, 0.85)', bordercolor='#FFB800',
                      borderwidth=1, borderpad=4)

    fig.update_layout(**{**DARK_LAYOUT, 'height': 360,
                         'xaxis': dict(**DARK_LAYOUT['xaxis'], title='임베딩 dim 1',
                                      showticklabels=False, range=[-0.6, 2.0]),
                         'yaxis': dict(**DARK_LAYOUT['yaxis'], title='임베딩 dim 2',
                                      showticklabels=False, range=[-0.4, 1.6]),
                         'legend': dict(orientation='h', y=-0.12, x=0.5, xanchor='center',
                                       font=dict(color='#8B96AB', size=10),
                                       bgcolor='rgba(0,0,0,0)')})
    return fig


def make_tsne_movement_chart(tsne_data):
    """t-SNE 임베딩 이동 - Brand D 궤적."""
    fig = go.Figure()

    # 정상 클러스터
    nx, ny = tsne_data['normal']
    fig.add_trace(go.Scatter(x=nx, y=ny, mode='markers',
                           marker=dict(color='rgba(139, 150, 171, 0.30)', size=8,
                                      line=dict(width=0)),
                           name='정상 클러스터 (100)', hoverinfo='skip'))
    # Promoter
    px, py = tsne_data['promoter']
    fig.add_trace(go.Scatter(x=px, y=py, mode='markers',
                           marker=dict(color='rgba(255, 59, 48, 0.45)', size=9,
                                      line=dict(width=0)),
                           name='Promoter 클러스터 (50)', hoverinfo='skip'))
    # Terrorist
    tx, ty = tsne_data['terrorist']
    fig.add_trace(go.Scatter(x=tx, y=ty, mode='markers',
                           marker=dict(color='rgba(10, 132, 255, 0.45)', size=9,
                                      line=dict(width=0)),
                           name='Terrorist 클러스터 (30)', hoverinfo='skip'))

    # Brand D 궤적
    traj_days, traj_x, traj_y = tsne_data['trajectory']
    fig.add_trace(go.Scatter(x=traj_x, y=traj_y, mode='lines+markers+text',
                           line=dict(color='#FFB800', width=2, dash='dot'),
                           marker=dict(color='#FFB800', size=14, symbol='star',
                                      line=dict(color='#FFFFFF', width=1.5)),
                           text=[f'D{d}' for d in traj_days],
                           textposition='top center',
                           textfont=dict(color='#FFFFFF', size=9, family='JetBrains Mono'),
                           name='Brand_D 궤적',
                           hovertemplate='Day %{text}<br>(%{x:.2f}, %{y:.2f})<extra></extra>'))

    # Day 45 마지막 위치 강조
    fig.add_trace(go.Scatter(x=[traj_x[-1]], y=[traj_y[-1]], mode='markers',
                           marker=dict(color='#FF3B30', size=24, symbol='star',
                                      line=dict(color='#FFFFFF', width=2.5),
                                      opacity=0.95),
                           name='Day 45 (현재)',
                           hovertemplate='<b>Brand_D Day 45</b><br>Promoter 클러스터 중심 +0.34 이동<extra></extra>'))

    fig.update_layout(**{**DARK_LAYOUT, 'height': 480,
                         'xaxis': dict(**DARK_LAYOUT['xaxis'], title='t-SNE dim 1',
                                      showticklabels=False),
                         'yaxis': dict(**DARK_LAYOUT['yaxis'], title='t-SNE dim 2',
                                      showticklabels=False),
                         'legend': dict(font=dict(color='#FFFFFF', size=11),
                                       bgcolor='rgba(19, 24, 41, 0.7)',
                                       bordercolor='#2A3447', borderwidth=1)})
    return fig


def make_sparkline(values, color='#34C759'):
    """KPI 카드용 미니 sparkline."""
    fig = go.Figure(go.Scatter(
        y=values, mode='lines',
        line=dict(color=color, width=2, shape='spline'),
        fill='tozeroy', fillcolor=f'rgba({",".join(str(int(int(color[i:i+2], 16))) for i in (1, 3, 5))}, 0.18)',
        hoverinfo='skip',
    ))
    fig.update_layout(
        height=40, margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig
