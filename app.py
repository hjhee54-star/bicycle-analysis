import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ───────────────────────────────────────────────
# 페이지 설정
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="따릉이 생존 분석 | 기후동행카드 시대",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────────────────────────────
# 커스텀 CSS
# ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
    color: #e6edf3;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
    border-right: 1px solid #30363d;
}

.hero-banner {
    background: linear-gradient(90deg, #1a3a5c 0%, #0d2137 40%, #1a1a2e 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: "🚲";
    position: absolute;
    right: 2rem; top: 50%;
    transform: translateY(-50%);
    font-size: 6rem;
    opacity: 0.08;
}
.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #58a6ff;
    margin: 0;
}
.hero-sub { color: #8b949e; font-size: 0.9rem; margin-top: 0.4rem; }

.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #58a6ff; }
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #58a6ff;
}
.metric-label { font-size: 0.78rem; color: #8b949e; margin-top: 0.3rem; }

.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #30363d;
}
.section-number {
    background: #1f6feb;
    color: white;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
}
.section-title { font-size: 1.05rem; font-weight: 600; color: #e6edf3; margin: 0; }

.sql-box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-left: 3px solid #58a6ff;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #79c0ff;
    white-space: pre-wrap;
    line-height: 1.7;
    margin: 0.5rem 0;
}
.insight-box {
    background: linear-gradient(135deg, #0e2a20 0%, #0d1117 100%);
    border: 1px solid #238636;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    color: #3fb950;
    line-height: 1.7;
    margin-top: 0.8rem;
}
.insight-box strong { color: #56d364; }

.error-box {
    background: #2d1215;
    border: 1px solid #f85149;
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
    color: #f85149;
}
</style>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────
# DB 연결
# ───────────────────────────────────────────────
DB_PATH = "bicycle.db"

@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql_query(sql, conn)

# DB 파일 존재 확인
if not os.path.exists(DB_PATH):
    st.markdown(f"""
    <div class="error-box">
        <h2>🚨 bicycle.db 파일을 찾을 수 없어요!</h2>
        <p style="color:#8b949e; margin-top:1rem;">
            <b>해결 방법</b><br><br>
            1. <code>bicycle.db</code> 파일을 이 <code>app.py</code>와 <b>같은 폴더</b>에 넣어주세요.<br>
            2. 터미널에서 <code>streamlit run app.py</code>를 다시 실행해주세요.<br><br>
            📁 현재 작업 폴더: <code>{os.getcwd()}</code>
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ───────────────────────────────────────────────
# 사이드바
# ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚲 따릉이 생존 분석")
    st.markdown("**기후동행카드 시대, 따릉이는 어디서 살아남고 있는가?**")
    st.markdown("---")

    # 기간 필터
    try:
        period_df = run_query(
            "SELECT DISTINCT 기준년월 FROM 대여소별이용정보 ORDER BY 기준년월"
        )
        periods = period_df["기준년월"].astype(str).tolist()
    except Exception:
        periods = []

    if periods:
        st.markdown("### 📅 분석 기간 선택")
        selected_periods = st.multiselect(
            "기준년월(YYYYMM) 필터",
            options=periods,
            default=periods,
            help="선택한 월만 포함해 차트를 그립니다."
        )
        if not selected_periods:
            selected_periods = periods
    else:
        selected_periods = periods

    st.markdown("---")
    st.markdown("### 📌 대주제")
    st.info("기후동행카드 확대 이후\n따릉이 이용 패턴 변화 분석")
    st.markdown("### 📋 소주제")
    st.markdown("① 자치구별 대여소 효율 랭킹")
    st.markdown("② 이용량 하위 구 식별")
    st.markdown("③ 월별 이용량 추이")
    st.markdown("---")
    st.caption("데이터: 서울시 공공자전거 이용정보 (2025.07~12)")


# ───────────────────────────────────────────────
# 기간 IN 절 생성 헬퍼
# ───────────────────────────────────────────────
def period_in(col="기준년월"):
    if selected_periods:
        vals = ", ".join(f"'{p}'" for p in selected_periods)
        return f"AND {col} IN ({vals})"
    return ""


# ───────────────────────────────────────────────
# 히어로 배너
# ───────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">기후동행카드 시대, 따릉이는 어디서 살아남고 있는가?</div>
    <div class="hero-sub">자치구별 대여소 효율 · 유휴 대여소 · 월별 이용 추이 분석 대시보드 | 2025년 7~12월</div>
</div>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────
# KPI 카드
# ───────────────────────────────────────────────
try:
    kpi_sql = f"""
    SELECT
        COUNT(DISTINCT 대여소명)              AS 활성대여소수,
        SUM(대여건수)                          AS 총이용건수,
        COUNT(DISTINCT 자치구)                 AS 분석구수,
        ROUND(SUM(대여건수)*1.0 / COUNT(DISTINCT 대여소명), 1) AS 대여소당평균이용건수
    FROM 대여소별이용정보
    WHERE 자치구 IS NOT NULL
    {period_in()}
    """
    kpi = run_query(kpi_sql).iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, f"{int(kpi['활성대여소수']):,}", "활성 대여소 수"),
        (c2, f"{int(kpi['총이용건수']):,}", "총 이용건수"),
        (c3, f"{int(kpi['분석구수'])}", "분석 자치구 수"),
        (c4, f"{kpi['대여소당평균이용건수']:,.1f}", "대여소당 평균 이용건수"),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"KPI 데이터 로드 실패: {e}")

st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# 소주제 ①  자치구별 대여소당 평균 이용량 효율 랭킹
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <span class="section-number">01</span>
    <span class="section-title">자치구별 대여소당 평균 이용량 — 효율 랭킹</span>
</div>
""", unsafe_allow_html=True)

SQL_01 = f"""
SELECT
    자치구,
    COUNT(DISTINCT 대여소명)                                        AS 대여소수,
    SUM(대여건수)                                                   AS 총이용건수,
    ROUND(SUM(대여건수) * 1.0 / COUNT(DISTINCT 대여소명), 1)        AS 대여소당평균이용건수
FROM 대여소별이용정보
WHERE 자치구 IS NOT NULL
{period_in()}
GROUP BY 자치구
ORDER BY 대여소당평균이용건수 DESC
"""

try:
    df01 = run_query(SQL_01)

    fig01 = px.bar(
        df01,
        x="대여소당평균이용건수",
        y="자치구",
        orientation="h",
        text="대여소당평균이용건수",
        color="대여소당평균이용건수",
        color_continuous_scale=["#1f2d3d", "#1a56db", "#58a6ff"],
        labels={"대여소당평균이용건수": "대여소당 평균 이용건수", "자치구": ""},
    )
    fig01.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig01.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3",
        yaxis=dict(autorange="reversed", gridcolor="#21262d"),
        xaxis=dict(gridcolor="#21262d"),
        coloraxis_showscale=False,
        margin=dict(l=0, r=80, t=20, b=20),
        height=560,
    )
    st.plotly_chart(fig01, use_container_width=True)

    col_s, col_i = st.columns([1, 1])
    with col_s:
        st.markdown("**🗄️ 사용 SQL**")
        st.markdown(f'<div class="sql-box">{SQL_01.strip()}</div>', unsafe_allow_html=True)
    with col_i:
        top3 = df01.head(3)["자치구"].tolist()
        bot3 = df01.tail(3)["자치구"].tolist()
        st.markdown(f"""
        <div class="insight-box">
        💡 <strong>인사이트</strong><br><br>
        대여소당 이용건수 상위 구는 <strong>{", ".join(top3)}</strong>으로,
        한강 접근성이 좋거나 직장인·환승 수요가 높은 지역에서
        인프라 대비 실제 활용도가 높게 나타납니다.<br><br>
        반면 하위 구인 <strong>{", ".join(bot3)}</strong>은 대여소 수 대비
        이용건수가 적어, 기후동행카드로 대중교통이 무제한화된 환경에서
        따릉이 수요가 줄어든 영향이 의심됩니다.<br><br>
        <strong>대여소 수 = 서비스 수준</strong>이 아니라
        <strong>이용률 = 실제 필요도</strong>라는 관점 전환이 필요합니다.
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📊 전체 자치구 상세 데이터 보기"):
        st.dataframe(
            df01.style.format({
                "대여소수": "{:,}",
                "총이용건수": "{:,}",
                "대여소당평균이용건수": "{:,.1f}",
            }).background_gradient(subset=["대여소당평균이용건수"], cmap="Blues"),
            use_container_width=True,
        )

except Exception as e:
    st.error(f"소주제 ① 오류: {e}")


# ═══════════════════════════════════════════════
# 소주제 ②  이용량 하위 구 식별 (유휴 대여소 밀집)
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <span class="section-number">02</span>
    <span class="section-title">이용량 하위 구 식별 — 유휴 대여소 밀집 지역</span>
</div>
""", unsafe_allow_html=True)

SQL_02 = f"""
SELECT
    자치구,
    COUNT(DISTINCT 대여소명)                                        AS 대여소수,
    SUM(대여건수)                                                   AS 총이용건수,
    ROUND(SUM(대여건수) * 1.0 / COUNT(DISTINCT 대여소명), 1)        AS 대여소당이용건수
FROM 대여소별이용정보
WHERE 자치구 IS NOT NULL
{period_in()}
GROUP BY 자치구
ORDER BY 대여소당이용건수 ASC
LIMIT 10
"""

try:
    df02 = run_query(SQL_02)

    fig02 = px.scatter(
        df02,
        x="대여소수",
        y="총이용건수",
        size="대여소당이용건수",
        color="대여소당이용건수",
        text="자치구",
        color_continuous_scale=["#f85149", "#e3b341", "#3fb950"],
        labels={
            "대여소수": "대여소 수 (개)",
            "총이용건수": "총 이용건수 (건)",
            "대여소당이용건수": "대여소당 이용건수",
        },
        size_max=50,
    )
    fig02.update_traces(
        textposition="top center",
        textfont_size=11,
        textfont_color="#e6edf3",
    )
    fig02.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3",
        xaxis=dict(gridcolor="#21262d"),
        yaxis=dict(gridcolor="#21262d"),
        coloraxis_colorbar=dict(title="대여소당<br>이용건수", tickfont=dict(color="#8b949e")),
        margin=dict(l=0, r=0, t=20, b=20),
        height=420,
    )

    # 전체 평균 기준선
    try:
        avg_df = run_query(SQL_01)
        fig02.add_vline(x=avg_df["대여소수"].mean(), line_dash="dot",
                        line_color="#58a6ff", opacity=0.5,
                        annotation_text="전체 평균 대여소수",
                        annotation_font_color="#58a6ff")
        fig02.add_hline(y=avg_df["총이용건수"].mean(), line_dash="dot",
                        line_color="#e3b341", opacity=0.5,
                        annotation_text="전체 평균 이용건수",
                        annotation_font_color="#e3b341")
    except Exception:
        pass

    st.plotly_chart(fig02, use_container_width=True)

    col_s2, col_i2 = st.columns([1, 1])
    with col_s2:
        st.markdown("**🗄️ 사용 SQL**")
        st.markdown(f'<div class="sql-box">{SQL_02.strip()}</div>', unsafe_allow_html=True)
    with col_i2:
        worst = df02.head(3)["자치구"].tolist()
        st.markdown(f"""
        <div class="insight-box">
        💡 <strong>인사이트</strong><br><br>
        버블이 오른쪽(대여소 많음)·아래쪽(이용건수 적음)에 위치한 구,
        특히 <strong>{", ".join(worst)}</strong>는 수요 예측 없이 공급이 이루어진
        인프라 과잉 투자 가능성을 시사합니다.<br><br>
        이러한 구에서는 대여소 통폐합 또는 수요 밀집 지역으로의
        <strong>재배치 정책</strong> 논의 근거로 이 데이터를 활용할 수 있습니다.<br><br>
        기후동행카드 이후 수요가 재편된 만큼,
        <strong>이용률 기반 운영 전략</strong>으로의 전환이 시급합니다.
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📊 하위 10개 구 상세 데이터 보기"):
        st.dataframe(
            df02.style.format({
                "대여소수": "{:,}",
                "총이용건수": "{:,}",
                "대여소당이용건수": "{:,.1f}",
            }).background_gradient(subset=["대여소당이용건수"], cmap="RdYlGn"),
            use_container_width=True,
        )

except Exception as e:
    st.error(f"소주제 ② 오류: {e}")


# ═══════════════════════════════════════════════
# 소주제 ③  월별 이용량 추이 (기후동행카드 연관성)
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <span class="section-number">03</span>
    <span class="section-title">월별 이용량 추이 — 기후동행카드 확대 시점과의 연관성</span>
</div>
""", unsafe_allow_html=True)

SQL_03 = f"""
SELECT
    기준년월        AS 년월,
    자치구,
    SUM(대여건수)   AS 이용건수
FROM 대여소별이용정보
WHERE 자치구 IS NOT NULL
{period_in()}
GROUP BY 기준년월, 자치구
ORDER BY 기준년월, 자치구
"""

try:
    df03 = run_query(SQL_03)
    df03["년월"] = df03["년월"].astype(str)

    # 전체 이용건수 기준 상위 5개 구 하이라이트
    top_gu = (
        df03.groupby("자치구")["이용건수"].sum()
            .nlargest(5).index.tolist()
    )

    # 전체 월별 합계
    total_monthly = df03.groupby("년월")["이용건수"].sum().reset_index()

    # 월 레이블 변환 (202507 → 25년 7월)
    def fmt_month(ym):
        return f"{ym[2:4]}년 {int(ym[4:6])}월"

    fig03 = go.Figure()

    for gu in df03["자치구"].unique():
        gu_df = df03[df03["자치구"] == gu].copy()
        gu_df["월라벨"] = gu_df["년월"].apply(fmt_month)
        is_top = gu in top_gu
        fig03.add_trace(go.Scatter(
            x=gu_df["월라벨"],
            y=gu_df["이용건수"],
            mode="lines",
            name=gu,
            line=dict(width=2.5 if is_top else 0.8),
            opacity=1.0 if is_top else 0.3,
            hovertemplate=f"<b>{gu}</b><br>%{{x}}<br>이용건수: %{{y:,}}<extra></extra>",
        ))

    total_monthly["월라벨"] = total_monthly["년월"].apply(fmt_month)
    fig03.add_trace(go.Scatter(
        x=total_monthly["월라벨"],
        y=total_monthly["이용건수"],
        mode="lines+markers",
        name="📍 전체 합계",
        line=dict(color="#f0e68c", width=3, dash="dot"),
        marker=dict(size=8, color="#f0e68c"),
        hovertemplate="<b>전체 합계</b><br>%{x}<br>이용건수: %{y:,}<extra></extra>",
    ))

    # 기후동행카드 확대 시점 표시 (9월)
    months_labels = [fmt_month(m) for m in sorted(df03["년월"].unique())]
    if "25년 9월" in months_labels:
        fig03.add_vline(
            x="25년 9월",
            line_dash="dash",
            line_color="#f85149",
            annotation_text="🔴 기후동행카드 확대",
            annotation_font_color="#f85149",
            annotation_position="top left",
        )

    fig03.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3",
        xaxis=dict(gridcolor="#21262d", title="년월"),
        yaxis=dict(gridcolor="#21262d", title="이용건수 (건)"),
        legend=dict(
            bgcolor="rgba(22,27,34,0.8)",
            bordercolor="#30363d",
            font=dict(size=11),
        ),
        margin=dict(l=0, r=0, t=20, b=20),
        height=500,
        hovermode="x unified",
    )
    st.plotly_chart(fig03, use_container_width=True)

    col_s3, col_i3 = st.columns([1, 1])
    with col_s3:
        st.markdown("**🗄️ 사용 SQL**")
        st.markdown(f'<div class="sql-box">{SQL_03.strip()}</div>', unsafe_allow_html=True)
    with col_i3:
        st.markdown(f"""
        <div class="insight-box">
        💡 <strong>인사이트</strong><br><br>
        기후동행카드 이용 범위가 확대된 2025년 9월 전후로
        도심권 구에서 이용량 변화 패턴을 확인하세요.
        진한 색 상위 5개 구(<strong>{", ".join(top_gu)}</strong>)는
        따릉이 이용이 집중된 핵심 지역입니다.<br><br>
        감소세가 두드러진 구는 대중교통 접근성이 좋은 도심권일 가능성이 높고,
        반대로 <strong>외곽 지역</strong>은 라스트마일 기능을
        유지하고 있을 것으로 예상됩니다.<br><br>
        따릉이의 역할이 <strong>레저·여가 수단</strong>에서
        <strong>교통 사각지대 보완 수단</strong>으로 재편되고 있음을
        수치로 뒷받침할 수 있습니다.
        </div>
        """, unsafe_allow_html=True)

    # 전월 대비 증감률 테이블
    with st.expander("📊 자치구별 전월 대비 이용량 증감률 보기"):
        pivot = df03.pivot_table(
            index="자치구", columns="년월", values="이용건수", aggfunc="sum"
        )
        pct = pivot.pct_change(axis=1) * 100
        st.dataframe(
            pct.style.format("{:.1f}%", na_rep="-")
               .background_gradient(cmap="RdYlGn", axis=None, vmin=-30, vmax=30),
            use_container_width=True,
        )

except Exception as e:
    st.error(f"소주제 ③ 오류: {e}")


# ───────────────────────────────────────────────
# 푸터
# ───────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#484f58; font-size:0.78rem; padding:1rem;
            border-top:1px solid #21262d;">
    🚲 따릉이 생존 분석 대시보드 &nbsp;|&nbsp;
    데이터: 서울시 공공자전거 이용정보 2025.07~12 &nbsp;|&nbsp;
    분석 주제: 기후동행카드 시대의 따릉이 이용 패턴 변화
</div>
""", unsafe_allow_html=True)
