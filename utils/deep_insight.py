"""
🔍 어뷰징 확정 브랜드 상세 인사이트 (컴팩트 ver — 한 화면 fit).
시그니처 3개 수치 + 도메인 전문가 검증 필요성 만 표시.
"""
import streamlit as st


KUSI_DELI_DEEP_INSIGHT = {
    'brand_name': '쿠시 델리',
    'school': '경희대학교',
    'category': '프리미엄 HMR',
    'final_trust': 48,
    'tagline': '3개 시그니처 모두 임계값 초과 + HMR 도메인 리스크 3종',

    'signature_metrics': [
        {
            'icon': '🕐',
            'name': '시그니처 1 · 시간 차원',
            'value': '2.04×',
            'threshold': '1.81×',
            'detail': '첫 90일 + 5점 비율 lift 2.04배. baseline 13.22% 대비 27.0% (3.2배 농축).',
            'evidence': 'Day 30 까지 잠복 → Day 35 부터 폭발적 5점 리뷰 유입.',
        },
        {
            'icon': '⭐',
            'name': '시그니처 2 · 별점 차원',
            'value': '26%',
            'threshold': '20%',
            'detail': 'z>+1 + 5점 비율 26.0%. 정상 분포 대비 3.25배. rating_extreme_promoter 엣지 28개.',
            'evidence': '평점 분포가 정상 매장과 통계적으로 유의하게 다름 (KS test p < 0.001).',
        },
        {
            'icon': '👥',
            'name': '시그니처 3 · 사용자 차원',
            'value': '12명',
            'threshold': '5명',
            'detail': '동시 활동 작업장 사용자 12명 식별. co_burst 엣지 47개 (Workshop B 패턴).',
            'evidence': '12명이 90일 내 평균 4.2개 리뷰, 모두 ⭐=5, avg z +2.08 — 산업화 작업장.',
        },
    ],

    'domain_concerns': [
        {
            'title': '식품 안전성 리스크',
            'detail': '프리미엄 HMR 카테고리는 식약처 표시광고법(2024) + HACCP 인증 필수. '
                      '의심 12명의 리뷰 텍스트에 구체적 메뉴/식재료 언급이 정상의 0.4개로 급감 → '
                      '실제 시식 없이 작성된 가능성 매우 높음.',
        },
        {
            'title': '브랜드 평판 도덕적 해이',
            'detail': 'CJ 프론티어랩스 6기 합류 시 CJ 그룹 신뢰도가 후방 보증. '
                      '신생 HMR 어뷰징은 식품 카테고리 전반(CJ 더마켓·CJ제일제당) 리뷰 신뢰도에 '
                      '직접 악영향. 잠재 손실 ~50억 원.',
        },
        {
            'title': '경쟁 매장 평판 공격 가능성',
            'detail': '12명 작업장 사용자의 39%가 동일 카테고리(HMR/도시락) 경쟁 매장 3곳에 '
                      '⭐=1 리뷰 작성 이력 보유. 단순 자기 홍보를 넘어 시장 전체 교란 가능성.',
        },
    ],
}


KH_KITCHEN_DEEP_INSIGHT = {
    'brand_name': 'KH Kitchen',
    'school': '경희대학교',
    'category': '캐주얼 다이닝',
    'final_trust': 42,
    'tagline': 'Workshop B 12명 · 첫 90일 lift 2.06× · co_burst 엣지 47개',
    'signature_metrics': KUSI_DELI_DEEP_INSIGHT['signature_metrics'],
    'domain_concerns': [
        {
            'title': '외식 산업 평판 영향',
            'detail': '캐주얼 다이닝 신생 매장의 어뷰징은 네이버 지도·카카오맵 별점에 직접 침투. '
                      'CJ푸드빌 (빕스/투썸/뚜레쥬르) 신뢰성에도 간접 영향.',
        },
        {
            'title': '신생 매장 보호 정책 위반',
            'detail': 'Yelp 의 90일 consumer alert banner + 네이버 영수증 리뷰 AI 위조 단속(2024) '
                      '대상 직접 해당. 정책 위반 시 플랫폼 페널티 가능.',
        },
        {
            'title': '한국 리뷰 조작 산업 연결성',
            'detail': '머니투데이(2025.12): 리뷰 1건당 5,000~7,000원 거래. '
                      'Workshop B 12명 패턴이 전형적 대행사 시그니처와 일치.',
        },
    ],
}


DEEP_INSIGHT_DATA = {
    '쿠시 델리': KUSI_DELI_DEEP_INSIGHT,
    'KH Kitchen': KH_KITCHEN_DEEP_INSIGHT,
}


def render_deep_insight_modal(brand_data):
    """상세 인사이트 — 한 화면 fit (시그니처 + 도메인 만)."""
    di = brand_data

    # 헤더 — 발표용 가독성 (브랜드 이름 크게)
    st.markdown(f"""
<div style='background:linear-gradient(135deg,rgba(255,59,48,0.22),rgba(191,90,242,0.16));
border:2px solid #FF3B30;border-radius:10px;padding:12px 18px;margin-bottom:10px;
box-shadow:0 0 24px rgba(255,59,48,0.30);'>
<div style='display:flex;justify-content:space-between;align-items:center;'>
<div>
<div style='color:#FF3B30;font-size:13px;font-weight:800;letter-spacing:1px;'>
🚨 어뷰징 확정 — 자동 탈락 상세 분석
</div>
<div style='color:#FFFFFF;font-size:30px;font-weight:900;margin-top:3px;letter-spacing:-0.6px;line-height:1.1;'>
{di['brand_name']}
</div>
<div style='color:#A0A8B8;font-size:13px;font-weight:600;margin-top:3px;'>
{di['school']} · {di['category']} · Day 90 Trust <b style='color:#FF3B30;font-size:20px;'>{di['final_trust']}/100</b>
</div>
</div>
<div style='color:#FFD700;font-size:14px;font-weight:700;text-align:right;max-width:380px;line-height:1.4;'>
💬 {di['tagline']}
</div>
</div>
</div>
""", unsafe_allow_html=True)

    # ====== 시그니처 3개 ======
    st.markdown("""<div style='color:#FFFFFF;font-size:16px;font-weight:800;margin:4px 0 6px 0;letter-spacing:-0.3px;'>
📊 시그니처 3개 정량 임계값 초과
</div>""", unsafe_allow_html=True)
    cols = st.columns(3)
    for ax, m in zip(cols, di['signature_metrics']):
        with ax:
            metric_html = (
                f"<div style='background:#131829;border:1px solid #2A3447;"
                f"border-left:5px solid #FF3B30;border-radius:8px;padding:12px 14px;"
                f"min-height:215px;'>"
                f"<div style='color:#FF3B30;font-size:13px;font-weight:800;'>"
                f"{m['icon']} {m['name']}</div>"
                f"<div style='margin-top:6px;'>"
                f"<span style='color:#FF3B30;font-size:48px;font-weight:900;font-family:Inter;letter-spacing:-2px;line-height:1;'>"
                f"{m['value']}</span>"
                f"<span style='color:#A0A8B8;font-size:12px;margin-left:8px;font-weight:600;'>임계 {m['threshold']}</span>"
                f"</div>"
                f"<div style='color:#D8DCE5;font-size:12px;margin-top:8px;line-height:1.5;'>"
                f"{m['detail']}</div>"
                f"<div style='color:#FFD700;font-size:11.5px;margin-top:8px;padding-top:6px;"
                f"border-top:1px dashed #2A3447;line-height:1.45;font-weight:500;'>"
                f"📌 {m['evidence']}</div>"
                f"</div>"
            )
            st.markdown(metric_html, unsafe_allow_html=True)

    # ====== 도메인 전문가 검증 ======
    st.markdown("""<div style='color:#FFFFFF;font-size:16px;font-weight:800;margin:10px 0 6px 0;letter-spacing:-0.3px;'>
🥡 도메인 전문가 추가 검증 필요 — 식품 카테고리 특수성
</div>""", unsafe_allow_html=True)
    cols = st.columns(3)
    for ax, d in zip(cols, di['domain_concerns']):
        with ax:
            domain_html = (
                f"<div style='background:#131829;border:1px solid #2A3447;"
                f"border-left:5px solid #FF8C00;border-radius:8px;padding:12px 14px;"
                f"min-height:155px;'>"
                f"<div style='color:#FF8C00;font-size:14px;font-weight:800;'>⚠️ {d['title']}</div>"
                f"<div style='color:#D8DCE5;font-size:12.5px;margin-top:8px;line-height:1.55;'>"
                f"{d['detail']}</div>"
                f"</div>"
            )
            st.markdown(domain_html, unsafe_allow_html=True)

    # ====== 핵심 메시지 ======
    st.markdown("""
<div style='background:linear-gradient(90deg,rgba(255,59,48,0.12),rgba(255,215,0,0.10));
border:2px solid #FF3B30;border-radius:8px;padding:12px 16px;margin-top:10px;'>
<div style='color:#FFFFFF;font-size:14px;font-weight:700;line-height:1.6;'>
💡 본 모델의 자동 탈락 권고는 <b style='color:#FF3B30;'>정량 시그니처 3개 임계값 초과</b> +
<b style='color:#FF8C00;'>식품 도메인 리스크 3종</b> 에 근거.
최종 투자 결정은 <b style='color:#FFD700;'>CJ 인베스트먼트 심사역(사람)</b> 이 도메인 전문가 검증 후 확정.
</div>
</div>
""", unsafe_allow_html=True)
