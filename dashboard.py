"""
E-Commerce Analytics Dashboard
Author: Nahom Worku — Financial Engineer & Data Scientist
Portfolio project: upwork.com/freelancers/nahomworku
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Analytics | Nahom Worku",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3a);
        border: 1px solid #2e3347;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.5rem;
    }
    .metric-label { color: #8892a4; font-size: 0.78rem; font-weight: 600;
                    text-transform: uppercase; letter-spacing: 0.08em; }
    .metric-value { color: #ffffff; font-size: 1.9rem; font-weight: 700;
                    line-height: 1.2; margin-top: 0.2rem; }
    .metric-delta-pos { color: #22c55e; font-size: 0.82rem; font-weight: 500; }
    .metric-delta-neg { color: #ef4444; font-size: 0.82rem; font-weight: 500; }
    .section-header {
        color: #e2e8f0; font-size: 1.1rem; font-weight: 700;
        margin: 1.5rem 0 0.8rem 0; padding-bottom: 0.4rem;
        border-bottom: 2px solid #3b82f6;
    }
    .insight-box {
        background: #1a2035; border-left: 4px solid #3b82f6;
        padding: 0.9rem 1.2rem; border-radius: 0 8px 8px 0;
        margin: 0.5rem 0; color: #cbd5e1; font-size: 0.88rem;
    }
    .stSelectbox label, .stMultiselect label { color: #94a3b8 !important; }
    div[data-testid="stSidebarContent"] { background-color: #151823; }
</style>
""", unsafe_allow_html=True)

# ── Color palette ──────────────────────────────────────────────
COLORS = {
    "primary":   "#3b82f6",
    "success":   "#22c55e",
    "warning":   "#f59e0b",
    "danger":    "#ef4444",
    "purple":    "#8b5cf6",
    "teal":      "#14b8a6",
    "chart_seq": px.colors.sequential.Blues_r,
    "chart_cat": ["#3b82f6","#22c55e","#f59e0b","#8b5cf6","#ef4444",
                  "#14b8a6","#f97316","#ec4899","#06b6d4","#84cc16"],
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="Inter, sans-serif", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
)

AXIS_STYLE = dict(
    gridcolor="#1e2535",
    linecolor="#2e3347",
    tickcolor="#2e3347",
    zerolinecolor="#2e3347",
)

# ── Data loader ────────────────────────────────────────────────
@st.cache_data
def load_data():
    orders    = pd.read_csv("orders.csv", parse_dates=["order_date", "delivery_date"])
    customers = pd.read_csv("customers.csv", parse_dates=["signup_date"])
    df = orders.merge(customers, on="customer_id", how="left")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)
    return df, customers

try:
    df_raw, customers = load_data()
except FileNotFoundError:
    st.error("⚠️  Data files not found. Run **generate_data.py** first, then restart.")
    st.code("python generate_data.py", language="bash")
    st.stop()

# ── Sidebar filters ────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔧 Filters")
    st.markdown("---")

    min_date = df_raw["order_date"].min().date()
    max_date = df_raw["order_date"].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    all_cats = sorted(df_raw["category"].unique())
    sel_cats = st.multiselect("Categories", all_cats, default=all_cats)

    all_states = sorted(df_raw["customer_state"].dropna().unique())
    sel_states = st.multiselect("States", all_states, default=all_states)

    all_statuses = sorted(df_raw["order_status"].unique())
    sel_status   = st.multiselect("Order Status", all_statuses,
                                  default=[s for s in all_statuses if s != "canceled"])

    st.markdown("---")
    st.markdown("**Built by Nahom Worku**")
    st.markdown("Financial Engineer & Data Scientist")

# ── Apply filters ──────────────────────────────────────────────
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = df_raw["order_date"].min(), df_raw["order_date"].max()

df = df_raw[
    (df_raw["order_date"] >= start) &
    (df_raw["order_date"] <= end)   &
    (df_raw["category"].isin(sel_cats)) &
    (df_raw["customer_state"].isin(sel_states)) &
    (df_raw["order_status"].isin(sel_status))
].copy()

# ── Navigation tabs ────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview",
    "🛒 Products",
    "👥 Customers",
    "📦 Operations",
    "🔍 Anomalies",
])

# ══════════════════════════════════════════════════════════════
#  TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Executive KPIs</div>', unsafe_allow_html=True)

    total_rev   = df["revenue"].sum()
    total_gmv   = df["total_value"].sum()
    total_orders = len(df)
    aov         = total_gmv / total_orders if total_orders > 0 else 0
    unique_custs = df["customer_id"].nunique()
    avg_score   = df["review_score"].mean()

    # YoY comparison (2024 vs 2023)
    rev_2024 = df[df["year"]==2024]["revenue"].sum()
    rev_2023 = df[df["year"]==2023]["revenue"].sum()
    yoy = (rev_2024 - rev_2023) / rev_2023 * 100 if rev_2023 > 0 else 0

    ord_2024 = df[df["year"]==2024].shape[0]
    ord_2023 = df[df["year"]==2023].shape[0]
    yoy_ord  = (ord_2024 - ord_2023) / ord_2023 * 100 if ord_2023 > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        (c1, "Total Revenue",   f"${total_rev/1e6:.2f}M", f"{'▲' if yoy>=0 else '▼'} {abs(yoy):.1f}% YoY", yoy>=0),
        (c2, "Total Orders",    f"{total_orders:,}",      f"{'▲' if yoy_ord>=0 else '▼'} {abs(yoy_ord):.1f}% YoY", yoy_ord>=0),
        (c3, "Avg Order Value", f"${aov:.2f}",            "Per transaction", True),
        (c4, "Unique Customers",f"{unique_custs:,}",      "Active buyers", True),
        (c5, "Avg Review",      f"{avg_score:.2f} / 5",   "⭐ Customer satisfaction", True),
    ]
    for col, label, val, delta, pos in kpis:
        dclass = "metric-delta-pos" if pos else "metric-delta-neg"
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            <div class="{dclass}">{delta}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Revenue Trend</div>', unsafe_allow_html=True)

    monthly = (
        df.groupby("year_month")
          .agg(revenue=("revenue", "sum"), orders=("order_id", "count"))
          .reset_index()
          .sort_values("year_month")
    )
    monthly["revenue_ma3"] = monthly["revenue"].rolling(3, min_periods=1).mean()

    fig_rev = make_subplots(specs=[[{"secondary_y": True}]])
    fig_rev.add_trace(go.Bar(
        x=monthly["year_month"], y=monthly["revenue"],
        name="Monthly Revenue", marker_color=COLORS["primary"],
        opacity=0.7,
    ), secondary_y=False)
    fig_rev.add_trace(go.Scatter(
        x=monthly["year_month"], y=monthly["revenue_ma3"],
        name="3M Moving Avg", line=dict(color=COLORS["success"], width=2.5),
        mode="lines",
    ), secondary_y=False)
    fig_rev.add_trace(go.Scatter(
        x=monthly["year_month"], y=monthly["orders"],
        name="Order Count", line=dict(color=COLORS["warning"], width=1.5, dash="dot"),
        mode="lines",
    ), secondary_y=True)

    fig_rev.update_layout(**PLOT_LAYOUT, height=340,
                          title_text="Monthly Revenue & Order Volume",
                          title_font=dict(color="#e2e8f0", size=14))
    fig_rev.update_xaxes(**AXIS_STYLE)
    fig_rev.update_yaxes(title_text="Revenue ($)", secondary_y=False, **AXIS_STYLE)
    fig_rev.update_yaxes(title_text="Orders",      secondary_y=True,  **AXIS_STYLE)
    st.plotly_chart(fig_rev, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">Revenue by Category</div>', unsafe_allow_html=True)
        cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=True).reset_index()
        fig_cat = px.bar(cat_rev, x="revenue", y="category", orientation="h",
                         color="revenue", color_continuous_scale="Blues",
                         labels={"revenue":"Revenue ($)", "category":""})
        fig_cat.update_layout(**PLOT_LAYOUT, height=320, coloraxis_showscale=False)
        fig_cat.update_xaxes(**AXIS_STYLE)
        fig_cat.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Revenue by Payment Type</div>', unsafe_allow_html=True)
        pay_rev = df.groupby("payment_type")["revenue"].sum().reset_index()
        fig_pay = px.pie(pay_rev, values="revenue", names="payment_type",
                         color_discrete_sequence=COLORS["chart_cat"],
                         hole=0.45)
        fig_pay.update_layout(**PLOT_LAYOUT, height=320)
        fig_pay.update_traces(textposition="outside", textinfo="percent+label",
                              textfont_color="#e2e8f0")
        st.plotly_chart(fig_pay, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
    💡 <strong>Key Insight:</strong> Revenue shows clear seasonality with Q4 spikes (Nov–Dec),
    consistent with Black Friday and holiday shopping patterns.
    Credit cards dominate at ~74% of GMV. Top category: <strong>Electronics</strong>.
    YoY revenue growth: <strong>{yoy:+.1f}%</strong>.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TAB 2 — PRODUCTS
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Category Performance Matrix</div>', unsafe_allow_html=True)

    cat_perf = df.groupby("category").agg(
        revenue     = ("revenue",      "sum"),
        orders      = ("order_id",     "count"),
        avg_price   = ("product_price","mean"),
        avg_score   = ("review_score", "mean"),
        avg_freight = ("freight_value","mean"),
    ).reset_index()
    cat_perf["revenue_share"] = cat_perf["revenue"] / cat_perf["revenue"].sum() * 100
    cat_perf["aov"] = cat_perf["revenue"] / cat_perf["orders"]

    fig_bubble = px.scatter(
        cat_perf,
        x="avg_price", y="avg_score",
        size="revenue", color="category",
        color_discrete_sequence=COLORS["chart_cat"],
        hover_data={"revenue": ":$,.0f", "orders": ":,", "revenue_share": ":.1f"},
        labels={"avg_price": "Average Price ($)", "avg_score": "Avg Review Score",
                "revenue": "Revenue"},
        size_max=55,
        title="Category Bubble Chart: Price vs Satisfaction vs Revenue",
    )
    fig_bubble.update_layout(**PLOT_LAYOUT, height=400)
    fig_bubble.update_xaxes(**AXIS_STYLE)
    fig_bubble.update_yaxes(**AXIS_STYLE, range=[3.5, 5.2])
    st.plotly_chart(fig_bubble, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">Revenue Share by Category</div>', unsafe_allow_html=True)
        cat_sorted = cat_perf.sort_values("revenue", ascending=False)
        fig_share = px.bar(cat_sorted, x="category", y="revenue_share",
                           color="revenue_share",
                           color_continuous_scale="Blues",
                           labels={"revenue_share":"Revenue Share (%)", "category":""},
                           title="% of Total Revenue")
        fig_share.update_layout(**PLOT_LAYOUT, height=300, coloraxis_showscale=False)
        fig_share.update_xaxes(**AXIS_STYLE, tickangle=30)
        fig_share.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_share, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Average Order Value by Category</div>', unsafe_allow_html=True)
        fig_aov = px.bar(cat_perf.sort_values("aov", ascending=False),
                         x="category", y="aov",
                         color="aov",
                         color_continuous_scale="Greens",
                         labels={"aov":"Avg Order Value ($)", "category":""},
                         title="AOV by Category")
        fig_aov.update_layout(**PLOT_LAYOUT, height=300, coloraxis_showscale=False)
        fig_aov.update_xaxes(**AXIS_STYLE, tickangle=30)
        fig_aov.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_aov, use_container_width=True)

    st.markdown('<div class="section-header">Category Summary Table</div>', unsafe_allow_html=True)
    display_df = cat_perf[["category","revenue","orders","aov","avg_score","revenue_share"]].copy()
    display_df.columns = ["Category","Revenue ($)","Orders","AOV ($)","Avg Score","Share (%)"]
    display_df = display_df.sort_values("Revenue ($)", ascending=False)
    display_df["Revenue ($)"] = display_df["Revenue ($)"].map("${:,.0f}".format)
    display_df["AOV ($)"]     = display_df["AOV ($)"].map("${:.2f}".format)
    display_df["Avg Score"]   = display_df["Avg Score"].map("{:.2f}".format)
    display_df["Share (%)"]   = display_df["Share (%)"].map("{:.1f}%".format)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
#  TAB 3 — CUSTOMERS (RFM Segmentation)
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">RFM Customer Segmentation</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
    📌 <strong>RFM Analysis</strong> segments customers by <strong>Recency</strong> (days since last order),
    <strong>Frequency</strong> (number of orders), and <strong>Monetary</strong> (total spend).
    This is the industry standard for e-commerce customer analytics.
    </div>""", unsafe_allow_html=True)

    snapshot = df["order_date"].max()
    rfm = df.groupby("customer_id").agg(
        recency   = ("order_date",  lambda x: (snapshot - x.max()).days),
        frequency = ("order_id",    "count"),
        monetary  = ("revenue",     "sum"),
    ).reset_index()

    # Score 1-5
    rfm["R_score"] = pd.qcut(rfm["recency"],   5, labels=[5,4,3,2,1]).astype(int)
    rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["monetary"],  5, labels=[1,2,3,4,5]).astype(int)
    rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

    def segment(row):
        if row["RFM_score"] >= 13:   return "Champions"
        elif row["R_score"] >= 4:    return "Loyal Customers"
        elif row["R_score"] >= 3 and row["F_score"] >= 3: return "Potential Loyalists"
        elif row["R_score"] >= 4 and row["F_score"] <= 2: return "Recent Customers"
        elif row["R_score"] <= 2 and row["RFM_score"] >= 9: return "At-Risk"
        elif row["R_score"] <= 2 and row["M_score"] >= 4: return "Can't Lose Them"
        elif row["R_score"] <= 2:    return "Lost"
        else:                        return "Needs Attention"

    rfm["Segment"] = rfm.apply(segment, axis=1)

    seg_summary = rfm.groupby("Segment").agg(
        Customers  = ("customer_id", "count"),
        Avg_Recency   = ("recency",   "mean"),
        Avg_Frequency = ("frequency", "mean"),
        Avg_Monetary  = ("monetary",  "mean"),
    ).reset_index()
    seg_summary["Revenue_Share"] = (
        seg_summary["Customers"] * seg_summary["Avg_Monetary"]
        / (seg_summary["Customers"] * seg_summary["Avg_Monetary"]).sum() * 100
    )

    col_l, col_r = st.columns(2)
    with col_l:
        fig_seg = px.pie(seg_summary, values="Customers", names="Segment",
                         color_discrete_sequence=COLORS["chart_cat"],
                         hole=0.4, title="Customer Distribution by Segment")
        fig_seg.update_layout(**PLOT_LAYOUT, height=360)
        fig_seg.update_traces(textposition="outside", textinfo="percent+label",
                              textfont_color="#e2e8f0")
        st.plotly_chart(fig_seg, use_container_width=True)

    with col_r:
        fig_rev_seg = px.bar(
            seg_summary.sort_values("Revenue_Share", ascending=False),
            x="Segment", y="Revenue_Share",
            color="Segment", color_discrete_sequence=COLORS["chart_cat"],
            labels={"Revenue_Share":"Revenue Share (%)", "Segment":""},
            title="Revenue Share by Segment",
        )
        fig_rev_seg.update_layout(**PLOT_LAYOUT, height=360, showlegend=False)
        fig_rev_seg.update_xaxes(**AXIS_STYLE, tickangle=25)
        fig_rev_seg.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_rev_seg, use_container_width=True)

    st.markdown('<div class="section-header">RFM Scatter — Frequency vs Monetary</div>', unsafe_allow_html=True)
    rfm_sample = rfm.sample(min(2000, len(rfm)), random_state=42)
    fig_rfm_scatter = px.scatter(
        rfm_sample, x="frequency", y="monetary",
        color="Segment", size="RFM_score",
        color_discrete_sequence=COLORS["chart_cat"],
        opacity=0.7, size_max=15,
        labels={"frequency":"Order Frequency", "monetary":"Total Spend ($)"},
        title="Customer Scatter: Frequency vs Spend",
    )
    fig_rfm_scatter.update_layout(**PLOT_LAYOUT, height=380)
    fig_rfm_scatter.update_xaxes(**AXIS_STYLE)
    fig_rfm_scatter.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig_rfm_scatter, use_container_width=True)

    st.markdown('<div class="section-header">Geographic Distribution</div>', unsafe_allow_html=True)
    geo = df.groupby("customer_state").agg(
        revenue=("revenue","sum"), orders=("order_id","count")
    ).reset_index().sort_values("revenue", ascending=False)
    fig_geo = px.bar(geo, x="customer_state", y="revenue",
                     color="revenue", color_continuous_scale="Blues",
                     labels={"revenue":"Revenue ($)","customer_state":"State"},
                     title="Revenue by State")
    fig_geo.update_layout(**PLOT_LAYOUT, height=320, coloraxis_showscale=False)
    fig_geo.update_xaxes(**AXIS_STYLE)
    fig_geo.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig_geo, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  TAB 4 — OPERATIONS
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Delivery Performance</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    delivered = df[df["order_status"]=="delivered"]
    avg_del   = delivered["delivery_days"].mean()
    on_time   = (delivered["delivery_days"] <= 10).mean() * 100
    canceled  = (df["order_status"]=="canceled").mean() * 100
    avg_freight = df["freight_value"].mean()

    ops_kpis = [
        (col1, "Avg Delivery Time", f"{avg_del:.1f} days", "Target: ≤10 days"),
        (col2, "On-Time Rate",      f"{on_time:.1f}%",     "Delivered within 10 days"),
        (col3, "Cancellation Rate", f"{canceled:.1f}%",    "Orders canceled"),
        (col4, "Avg Freight Cost",  f"${avg_freight:.2f}", "Per order"),
    ]
    for col, label, val, note in ops_kpis:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-delta-pos">{note}</div>
        </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">Delivery Time Distribution</div>', unsafe_allow_html=True)
        fig_del = px.histogram(
            delivered, x="delivery_days", nbins=30,
            color_discrete_sequence=[COLORS["primary"]],
            labels={"delivery_days":"Delivery Days", "count":"Orders"},
            title="Distribution of Delivery Times",
        )
        fig_del.add_vline(x=avg_del, line_dash="dash",
                          line_color=COLORS["success"],
                          annotation_text=f"Avg: {avg_del:.1f}d",
                          annotation_font_color=COLORS["success"])
        fig_del.update_layout(**PLOT_LAYOUT, height=320)
        fig_del.update_xaxes(**AXIS_STYLE)
        fig_del.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_del, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Delivery Time by Category</div>', unsafe_allow_html=True)
        del_cat = delivered.groupby("category")["delivery_days"].mean().sort_values().reset_index()
        fig_del_cat = px.bar(del_cat, x="delivery_days", y="category",
                             orientation="h", color="delivery_days",
                             color_continuous_scale="RdYlGn_r",
                             labels={"delivery_days":"Avg Days","category":""},
                             title="Average Delivery Days by Category")
        fig_del_cat.update_layout(**PLOT_LAYOUT, height=320, coloraxis_showscale=False)
        fig_del_cat.update_xaxes(**AXIS_STYLE)
        fig_del_cat.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_del_cat, use_container_width=True)

    st.markdown('<div class="section-header">Review Score Distribution</div>', unsafe_allow_html=True)
    score_dist = df["review_score"].value_counts().sort_index().reset_index()
    score_dist.columns = ["Score","Count"]
    score_dist["Color"] = score_dist["Score"].map({
        1: COLORS["danger"], 2: COLORS["warning"], 3: "#a3a3a3",
        4: "#86efac", 5: COLORS["success"]
    })
    fig_scores = px.bar(score_dist, x="Score", y="Count",
                        color="Score",
                        color_discrete_map={s: c for s, c in
                                            zip(score_dist["Score"], score_dist["Color"])},
                        title="Customer Review Scores (1–5 Stars)",
                        labels={"Count":"Number of Reviews"})
    fig_scores.update_layout(**PLOT_LAYOUT, height=300, showlegend=False)
    fig_scores.update_xaxes(**AXIS_STYLE)
    fig_scores.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig_scores, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  TAB 5 — ANOMALY DETECTION
# ══════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Revenue Anomaly Detection (Z-Score Method)</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    🔍 <strong>Method:</strong> Z-score anomaly detection flags days where revenue
    deviates more than <strong>2 standard deviations</strong> from the rolling 30-day mean.
    Positive anomalies = sales spikes. Negative = revenue drops worth investigating.
    </div>""", unsafe_allow_html=True)

    daily = df.groupby("order_date")["revenue"].sum().reset_index()
    daily = daily.sort_values("order_date")
    daily["rolling_mean"] = daily["revenue"].rolling(30, min_periods=7).mean()
    daily["rolling_std"]  = daily["revenue"].rolling(30, min_periods=7).std()
    daily["z_score"] = (daily["revenue"] - daily["rolling_mean"]) / daily["rolling_std"]
    daily["anomaly"] = daily["z_score"].abs() > 2
    daily["anomaly_type"] = np.where(
        daily["z_score"] > 2, "Positive Spike",
        np.where(daily["z_score"] < -2, "Negative Drop", "Normal")
    )

    anomalies = daily[daily["anomaly"]]

    fig_anomaly = go.Figure()
    fig_anomaly.add_trace(go.Scatter(
        x=daily["order_date"], y=daily["revenue"],
        mode="lines", name="Daily Revenue",
        line=dict(color=COLORS["primary"], width=1.2), opacity=0.7,
    ))
    fig_anomaly.add_trace(go.Scatter(
        x=daily["order_date"], y=daily["rolling_mean"],
        mode="lines", name="30-Day Rolling Mean",
        line=dict(color=COLORS["success"], width=2, dash="dash"),
    ))
    fig_anomaly.add_trace(go.Scatter(
        x=daily["order_date"],
        y=daily["rolling_mean"] + 2 * daily["rolling_std"],
        mode="lines", name="Upper Band (+2σ)",
        line=dict(color=COLORS["warning"], width=1, dash="dot"),
    ))
    fig_anomaly.add_trace(go.Scatter(
        x=daily["order_date"],
        y=daily["rolling_mean"] - 2 * daily["rolling_std"],
        mode="lines", name="Lower Band (-2σ)",
        line=dict(color=COLORS["danger"], width=1, dash="dot"),
        fill="tonexty", fillcolor="rgba(239,68,68,0.04)",
    ))
    pos_anom = anomalies[anomalies["anomaly_type"]=="Positive Spike"]
    neg_anom = anomalies[anomalies["anomaly_type"]=="Negative Drop"]
    fig_anomaly.add_trace(go.Scatter(
        x=pos_anom["order_date"], y=pos_anom["revenue"],
        mode="markers", name="Positive Spike",
        marker=dict(color=COLORS["success"], size=10, symbol="triangle-up"),
    ))
    fig_anomaly.add_trace(go.Scatter(
        x=neg_anom["order_date"], y=neg_anom["revenue"],
        mode="markers", name="Negative Drop",
        marker=dict(color=COLORS["danger"], size=10, symbol="triangle-down"),
    ))
    fig_anomaly.update_layout(**PLOT_LAYOUT, height=420,
                              title="Daily Revenue with Anomaly Detection Bands")
    fig_anomaly.update_xaxes(**AXIS_STYLE)
    fig_anomaly.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig_anomaly, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(f"**🚨 {len(anomalies)} anomalies detected**")
        st.markdown(f"- 🟢 Positive spikes: **{len(pos_anom)}**")
        st.markdown(f"- 🔴 Negative drops: **{len(neg_anom)}**")

        if len(anomalies) > 0:
            top_anom = anomalies.sort_values("z_score", key=abs, ascending=False).head(8)
            display = top_anom[["order_date","revenue","z_score","anomaly_type"]].copy()
            display.columns = ["Date","Revenue ($)","Z-Score","Type"]
            display["Revenue ($)"] = display["Revenue ($)"].map("${:,.0f}".format)
            display["Z-Score"]     = display["Z-Score"].map("{:+.2f}".format)
            st.dataframe(display, use_container_width=True, hide_index=True)

    with col_r:
        st.markdown('<div class="section-header">Monthly Revenue Heatmap</div>', unsafe_allow_html=True)
        heatmap_data = df.groupby(["year","month"])["revenue"].sum().reset_index()
        heatmap_pivot = heatmap_data.pivot(index="year", columns="month", values="revenue").fillna(0)
        month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        heatmap_pivot.columns = [month_names[m-1] for m in heatmap_pivot.columns]

        fig_heat = px.imshow(
            heatmap_pivot,
            color_continuous_scale="Blues",
            labels=dict(x="Month", y="Year", color="Revenue ($)"),
            title="Revenue Heatmap by Year & Month",
        )
        fig_heat.update_layout(**PLOT_LAYOUT, height=260)
        st.plotly_chart(fig_heat, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#4b5563; font-size:0.8rem;'>"
    "Built by <strong style='color:#3b82f6'>Nahom Worku</strong> · "
    "Financial Engineer & Data Scientist · "
    "E-Commerce Analytics Dashboard v1.0"
    "</div>",
    unsafe_allow_html=True,
)
