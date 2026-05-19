"""ON-Trust Shield — 커스텀 CSS."""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

:root {
    --bg-primary: #0A0E1A;
    --bg-secondary: #131829;
    --bg-tertiary: #1C2235;
    --border-color: #2A3447;
    --accent-red: #FF3B30;
    --accent-amber: #FFB800;
    --accent-green: #34C759;
    --accent-blue: #0A84FF;
    --accent-purple: #BF5AF2;
    --text-primary: #FFFFFF;
    --text-secondary: #8B96AB;
}

.stApp {
    background: #0A0E1A !important;
    font-family: 'Inter', 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #FFFFFF !important;
}

#MainMenu, footer, header { visibility: hidden; height: 0; }
.block-container { padding-top: 0.5rem !important; max-width: 100% !important; }

[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div, [data-testid="stMarkdownContainer"] li {
    color: #E8EDF5 !important;
}

[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4 {
    color: #FFFFFF !important;
    font-family: 'Inter', 'Pretendard', sans-serif !important;
}

/* ================= Header ================= */
.ots-header {
    background: linear-gradient(180deg, #131829 0%, #0A0E1A 100%);
    padding: 14px 28px;
    border-bottom: 1px solid #2A3447;
    display: flex; align-items: center; justify-content: space-between;
    border-radius: 12px;
    margin-bottom: 18px;
}
.ots-logo {
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    font-size: 22px;
    color: #FFFFFF;
    letter-spacing: -0.5px;
}
.ots-subtitle {
    color: #8B96AB;
    font-size: 12px;
    font-weight: 500;
    margin-top: 2px;
}
.ots-live {
    display: flex; align-items: center; gap: 10px;
    background: rgba(255, 59, 48, 0.08);
    padding: 6px 14px;
    border-radius: 100px;
    border: 1px solid rgba(255, 59, 48, 0.25);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #FFFFFF;
    font-weight: 500;
}
.live-dot {
    display: inline-block; width: 8px; height: 8px;
    background: #FF3B30; border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
    box-shadow: 0 0 12px rgba(255, 59, 48, 0.8);
}
.ots-user {
    display: flex; align-items: center; gap: 12px;
    color: #8B96AB; font-size: 13px;
}
.ots-bell {
    position: relative;
    font-size: 18px;
    cursor: pointer;
}
.ots-bell::after {
    content: '1';
    position: absolute;
    top: -6px; right: -8px;
    background: #FF3B30;
    color: white;
    border-radius: 50%;
    width: 16px; height: 16px;
    font-size: 10px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700;
    box-shadow: 0 0 8px rgba(255, 59, 48, 0.6);
}
.ots-avatar {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #FF3B30, #BF5AF2);
    border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-weight: 700;
    color: white;
    font-size: 14px;
}

/* ================= KPI Cards ================= */
.kpi-row { display: flex; gap: 12px; margin-bottom: 24px; }
.kpi-card {
    background: linear-gradient(135deg, #131829 0%, #1C2235 100%);
    border: 1px solid #2A3447;
    border-radius: 14px;
    padding: 22px 24px;
    flex: 1;
    position: relative;
    transition: all 0.25s ease;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 4px; height: 100%;
    background: var(--border-color);
}
.kpi-card.normal::before { background: #34C759; }
.kpi-card.warning::before { background: #FFB800; }
.kpi-card.danger::before { background: #FF3B30; }
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
.kpi-label {
    color: #8B96AB; font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.kpi-value {
    font-size: 44px;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.1;
    margin: 6px 0;
    font-family: 'Inter', sans-serif;
    letter-spacing: -1.5px;
}
.kpi-value.danger {
    color: #FF3B30;
    animation: danger-blink 1.5s ease-in-out infinite;
    text-shadow: 0 0 20px rgba(255, 59, 48, 0.5);
}
.kpi-value.warning { color: #FFB800; }
.kpi-value.normal { color: #34C759; }
.kpi-trend {
    font-size: 12px;
    color: #8B96AB;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
}
.kpi-trend.up { color: #34C759; }
.kpi-trend.down { color: #FF3B30; }
.kpi-detail {
    color: #8B96AB; font-size: 12px;
    margin-top: 4px;
}

/* ================= Brand Grid ================= */
.brand-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}
.brand-card {
    background: #131829;
    border: 1px solid #2A3447;
    border-left: 4px solid #34C759;
    border-radius: 10px;
    padding: 14px 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    min-height: 140px;
}
.brand-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(0,0,0,0.5);
    border-color: #3A4458;
}
.brand-card.monitoring {
    border-left-color: #FFB800;
    animation: monitoring-pulse 2.5s ease-in-out infinite;
}
.brand-card.danger {
    border-left-color: #FF3B30;
    animation: danger-glow 1.8s ease-in-out infinite;
}
.brand-row {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 6px;
}
.brand-name {
    font-weight: 700; color: #FFFFFF; font-size: 13px;
    display: flex; align-items: center; gap: 6px;
}
.brand-status-dot {
    display: inline-block; width: 7px; height: 7px;
    border-radius: 50%;
    background: #34C759;
}
.brand-status-dot.monitoring { background: #FFB800; }
.brand-status-dot.danger {
    background: #FF3B30;
    box-shadow: 0 0 10px rgba(255, 59, 48, 0.8);
    animation: pulse 1.5s ease-in-out infinite;
}
.brand-day {
    color: #8B96AB; font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
}
.brand-trust {
    font-size: 30px; font-weight: 800;
    color: #FFFFFF; line-height: 1;
    margin: 8px 0 2px 0;
    font-family: 'Inter', sans-serif;
    letter-spacing: -1px;
    text-align: center;
}
.brand-trust.danger {
    color: #FF3B30;
    text-shadow: 0 0 15px rgba(255, 59, 48, 0.6);
}
.brand-trust.monitoring { color: #FFB800; }
.brand-change {
    text-align: center; font-size: 11px;
    color: #34C759;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 8px;
}
.brand-change.down { color: #FF3B30; }
.brand-sigs {
    color: #8B96AB; font-size: 10px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 6px;
    letter-spacing: 0;
}
.brand-sigs.danger { color: #FF3B30; }
.brand-progress {
    width: 100%; height: 3px;
    background: #1C2235;
    border-radius: 2px;
    overflow: hidden;
}
.brand-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #34C759, #0A84FF);
    transition: width 0.5s ease;
}
.brand-progress-fill.danger {
    background: linear-gradient(90deg, #FFB800, #FF3B30);
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.55; transform: scale(1.25); }
}
@keyframes danger-blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}
@keyframes danger-glow {
    0%, 100% {
        box-shadow: 0 0 18px rgba(255, 59, 48, 0.3);
        border-left-color: #FF3B30;
    }
    50% {
        box-shadow: 0 0 36px rgba(255, 59, 48, 0.6);
        border-left-color: #FF6B5C;
    }
}
@keyframes monitoring-pulse {
    0%, 100% { box-shadow: 0 0 0 rgba(255, 184, 0, 0); }
    50% { box-shadow: 0 0 18px rgba(255, 184, 0, 0.25); }
}

/* ================= Section Headers ================= */
.section-title {
    font-size: 18px;
    font-weight: 700;
    color: #FFFFFF;
    margin: 12px 0 14px 0;
    display: flex; align-items: center; gap: 10px;
    letter-spacing: -0.3px;
}
.section-subtitle {
    color: #8B96AB; font-size: 12px;
    font-weight: 500;
    margin-bottom: 16px;
}
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #2A3447, transparent);
    margin: 28px 0 20px 0;
}

/* ================= Brand D Detail Header ================= */
.detail-header {
    background: linear-gradient(135deg, rgba(255, 59, 48, 0.10) 0%, #131829 60%);
    border: 1px solid rgba(255, 59, 48, 0.35);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
    display: flex; justify-content: space-between; align-items: center;
}
.detail-title {
    font-size: 24px; font-weight: 800; color: #FFFFFF;
    letter-spacing: -0.5px;
}
.detail-subtitle {
    color: #8B96AB; font-size: 13px;
    margin-top: 4px;
}

/* ================= Signature Box ================= */
.sig-box {
    background: #131829;
    border: 1px solid #2A3447;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 14px;
}
.sig-label {
    color: #FFB800;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace;
}
.sig-label.red { color: #FF3B30; }
.sig-label.purple { color: #BF5AF2; }
.sig-title {
    font-size: 16px; font-weight: 700; color: #FFFFFF;
    margin-bottom: 12px;
}
.sig-bottom {
    background: rgba(255, 59, 48, 0.08);
    border-left: 3px solid #FF3B30;
    padding: 10px 14px;
    margin-top: 10px;
    border-radius: 0 8px 8px 0;
}
.sig-bottom-value {
    color: #FF3B30; font-size: 20px; font-weight: 800;
    font-family: 'Inter', sans-serif;
    letter-spacing: -0.5px;
}
.sig-bottom-detail {
    color: #8B96AB; font-size: 11px;
    margin-top: 2px;
}
.sig-bottom-ref {
    color: #BF5AF2; font-size: 11px;
    font-weight: 600;
    margin-top: 4px;
}

/* ================= Slack Card ================= */
.slack-card {
    background: #1A1D26;
    border: 1px solid #2A3447;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.5);
    font-family: 'Pretendard', -apple-system, sans-serif;
    color: #E8EDF5;
}
.slack-header {
    display: flex; align-items: center; gap: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #2A3447;
    margin-bottom: 14px;
}
.slack-channel {
    color: #8B96AB; font-size: 13px; font-weight: 500;
}
.slack-time {
    color: #8B96AB; font-size: 12px;
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
}
.slack-bot {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 12px;
}
.slack-bot-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #BF5AF2, #0A84FF);
    border-radius: 6px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 16px;
}
.slack-bot-name {
    font-weight: 700; color: #FFFFFF; font-size: 14px;
}
.slack-bot-tag {
    background: #2A3447;
    color: #8B96AB;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 10px;
    font-weight: 600;
}
.slack-alert-title {
    font-size: 16px;
    font-weight: 800;
    color: #FF3B30;
    margin: 8px 0 12px 0;
    letter-spacing: -0.3px;
}
.slack-row {
    color: #C8D0DE;
    font-size: 13px;
    margin: 6px 0;
    line-height: 1.5;
}
.slack-row-strong {
    color: #FFFFFF;
    font-weight: 600;
}
.slack-section-title {
    color: #FFB800;
    font-size: 12px;
    font-weight: 700;
    margin: 14px 0 4px 0;
    font-family: 'JetBrains Mono', monospace;
}
.slack-button-row {
    display: flex; gap: 8px;
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid #2A3447;
}
.slack-btn {
    background: #2A3447;
    color: #FFFFFF;
    padding: 7px 14px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    flex: 1;
}
.slack-btn.primary { background: linear-gradient(135deg, #0A84FF, #BF5AF2); }
.slack-footer {
    color: #5B6478; font-size: 11px;
    margin-top: 12px; padding-top: 10px;
    border-top: 1px solid #2A3447;
    font-style: italic;
}

/* ================= Activity Feed ================= */
.activity-bar {
    background: #131829;
    border: 1px solid #2A3447;
    border-radius: 10px;
    padding: 14px 20px;
    margin-top: 24px;
    margin-bottom: 12px;
    display: flex; align-items: center; gap: 16px;
    overflow: hidden;
    position: relative;
}
.activity-label {
    display: flex; align-items: center; gap: 8px;
    color: #34C759;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 12px;
    white-space: nowrap;
    flex-shrink: 0;
    border-right: 1px solid #2A3447;
    padding-right: 16px;
}
.activity-dot {
    width: 7px; height: 7px;
    background: #34C759;
    border-radius: 50%;
    box-shadow: 0 0 10px rgba(52, 199, 89, 0.8);
    animation: pulse 1.2s ease-in-out infinite;
}
.activity-feed-text {
    color: #B5BEC8;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    white-space: nowrap;
    animation: scroll-feed 45s linear infinite;
    padding-left: 100%;
}
@keyframes scroll-feed {
    0% { transform: translateX(0); }
    100% { transform: translateX(-100%); }
}

/* ================= Streamlit overrides ================= */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: #131829;
    border: 1px solid #2A3447;
    border-radius: 8px;
    color: #8B96AB;
    font-weight: 600;
    padding: 10px 18px;
    font-size: 13px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1C2235, #131829);
    color: #FFFFFF !important;
    border-color: #FF3B30 !important;
    box-shadow: 0 0 16px rgba(255, 59, 48, 0.2);
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 18px;
}

[data-testid="stMetric"] {
    background: #131829;
    border: 1px solid #2A3447;
    border-radius: 10px;
    padding: 14px;
}
[data-testid="stMetricLabel"] {
    color: #8B96AB !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 28px !important;
    font-weight: 800 !important;
}

.stDataFrame {
    background: #131829 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #131829 !important;
    border-right: 1px solid #2A3447;
}
section[data-testid="stSidebar"] * {
    color: #E8EDF5 !important;
}

/* Caption */
.caption {
    color: #5B6478;
    font-size: 11px;
    font-style: italic;
    margin-top: 4px;
}
</style>
"""
