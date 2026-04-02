"""
E-Commerce Analytics Dashboard — Ultimate Edition
Author: Nahom Worku | Financial Engineer & Data Scientist
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="E-Commerce Analytics | Nahom Worku",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080c14;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, #0d1f3c 0%, #080c14 50%),
                radial-gradient(ellipse at 80% 100%, #0a1628 0%, transparent 60%);
}

[data-testid="stSidebar"] {
    background: #060a10 !important;
    border-right: 1px solid #0e1825 !important;
}

[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif; }

.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 100% !important; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

.dash-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 2rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid #0e1825;
}
.dash-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    color: #f0f4ff;
    letter-spacing: -0.03em;
    margin: 0;
}
.dash-subtitle {
    font-size: 0.82rem;
    color: #3d5a80;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 500;
}

.kpi-card {
    background: linear-gradient(135deg, #0c1520 0%, #0a1219 100%);
    border: 1px solid #0e1f30;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    position: relative;
    overflow: hidden;
    margin-bottom: 0.5rem;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, #1e4080);
    border-radius: 12px 12px 0 0;
}
.kpi-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #3d5a80;
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: #e8f0ff;
    line-height: 1;
    margin-bottom: 0.4rem;
}
.kpi-delta-pos { font-size: 0.75rem; color: #22c55e; font-weight: 500; }
.kpi-delta-neg { font-size: 0.75rem; color: #ef4444; font-weight: 500; }
.kpi-delta-neu { font-size: 0.75rem; color: #64748b; font-weight: 500; }

.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #2563a8;
    margin: 1.5rem 0 0.75rem 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #0e1f30, transparent);
}

.insight {
    background: #080e18;
    border-left: 3px solid #1e4080;
    padding: 0.8rem 1rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.82rem;
    color: #5a7a9a;
    margin: 0.75rem 0;
    line-height: 1.5;
}
.insight strong { color: #7aa8d0; }

[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid #0e1825 !important;
    gap: 0 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #3d5a80 !important;
    padding: 0.6rem 1.2rem !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
    letter-spacing: 0.02em !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #7aa8d0 !important;
    border-bottom: 2px solid #2563a8 !important;
}

.sidebar-brand {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #7aa8d0;
    margin-bottom: 0.3rem;
    letter-spacing: -0.01em;
}
.sidebar-role {
    font-size: 0.72rem;
    color: #2563a8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1.5rem;
}
.sidebar-divider {
    height: 1px;
    background: #0e1825;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        orders    = pd.read_csv("orders.csv",    parse_dates=["order_date","delivery_date"])
        customers = pd.read_csv("customers.csv", parse_dates=["signup_date"])
    except FileNotFoundError:
        st.error("Run generate_data.py first to create the data files.")
        st.stop()
    df = orders.merge(customers, on="customer_id", how="left")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)
    return df, customers

df_raw, customers = load_data()

# ── PLOTLY THEME ──────────────────────────────────────────────
BG   = "rgba(0,0,0,0)"
GRID = "#0e1825"
TEXT = "#5a7a9a"
FONT = "DM Sans"
BLUES = ["#0d2a4a","#1a3f6f","#245591","#2d6bb5","#3a82d8","#5aa0f0","#7dbeff","#aad4ff"]
CAT10 = ["#3a82d8","#22c55e","#f59e0b","#8b5cf6","#ef4444",
         "#14b8a6","#f97316","#ec4899","#06b6d4","#84cc16"]

def BL(title="", h=380):
    return dict(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family=FONT, color=TEXT, size=11),
        title=dict(text=title, font=dict(family="Syne", color="#c8daf0", size=13), x=0.01, pad=dict(b=12)),
        margin=dict(l=12, r=12, t=44 if title else 20, b=12),
        height=h,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)", font=dict(color=TEXT, size=10)),
        xaxis=dict(gridcolor=GRID, linecolor=GRID, tickcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, linecolor=GRID, tickcolor=GRID, zerolinecolor=GRID),
    )

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">Nahom Worku</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-role">Financial Engineer · Data Scientist</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Filters**")
    min_d = df_raw["order_date"].min().date()
    max_d = df_raw["order_date"].max().date()
    dates  = st.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    cats   = st.multiselect("Category",     sorted(df_raw["category"].unique()),       default=sorted(df_raw["category"].unique()))
    states = st.multiselect("State",        sorted(df_raw["customer_state"].unique()), default=sorted(df_raw["customer_state"].unique()))
    stats  = st.multiselect("Order Status", sorted(df_raw["order_status"].unique()),   default=[s for s in df_raw["order_status"].unique() if s != "canceled"])
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.7rem;color:#1e3a5a;">Dataset: {len(df_raw):,} orders · 3 years</div>', unsafe_allow_html=True)

# ── FILTER ────────────────────────────────────────────────────
if len(dates) == 2:
    s, e = pd.Timestamp(dates[0]), pd.Timestamp(dates[1])
else:
    s, e = df_raw["order_date"].min(), df_raw["order_date"].max()

df = df_raw[
    (df_raw["order_date"] >= s) & (df_raw["order_date"] <= e) &
    df_raw["category"].isin(cats) &
    df_raw["customer_state"].isin(states) &
    df_raw["order_status"].isin(stats)
].copy()

# ── HEADER ────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
    <h1 class="dash-title">E-Commerce Analytics</h1>
    <span class="dash-subtitle">Revenue Intelligence Platform</span>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────
total_rev    = df["revenue"].sum()
total_orders = len(df)
aov          = df["total_value"].mean()
unique_custs = df["customer_id"].nunique()
avg_score    = df["review_score"].mean()
rev_2024 = df[df["year"]==2024]["revenue"].sum()
rev_2023 = df[df["year"]==2023]["revenue"].sum()
yoy      = (rev_2024-rev_2023)/rev_2023*100 if rev_2023>0 else 0
ord_2024 = df[df["year"]==2024].shape[0]
ord_2023 = df[df["year"]==2023].shape[0]
yoy_ord  = (ord_2024-ord_2023)/ord_2023*100 if ord_2023>0 else 0

kpis = [
    ("Total Revenue",    f"${total_rev/1e6:.2f}M",  f"{'▲' if yoy>=0 else '▼'} {abs(yoy):.1f}% YoY",         yoy>=0,    "#1e3a6e"),
    ("Total Orders",     f"{total_orders:,}",        f"{'▲' if yoy_ord>=0 else '▼'} {abs(yoy_ord):.1f}% YoY", yoy_ord>=0,"#1a3d2e"),
    ("Avg Order Value",  f"${aov:.2f}",              "Per transaction",                                          None,      "#2a2a1a"),
    ("Unique Customers", f"{unique_custs:,}",         "Active buyers",                                           None,      "#1e1a3d"),
    ("Avg Review",       f"{avg_score:.2f}★",        "Customer satisfaction",                                    None,      "#2a1a1a"),
]
cols = st.columns(5)
for col, (label, val, delta, pos, accent) in zip(cols, kpis):
    dc = "kpi-delta-pos" if pos is True else ("kpi-delta-neg" if pos is False else "kpi-delta-neu")
    col.markdown(f"""
    <div class="kpi-card" style="--accent:{accent};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{val}</div>
        <div class="{dc}">{delta}</div>
    </div>""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────
t1, t2, t3, t4, t5 = st.tabs(["Overview", "Products", "Customers", "Operations", "Anomalies"])

# ══════════════════════════
with t1:
    st.markdown('<div class="section-label">Revenue Trend</div>', unsafe_allow_html=True)
    monthly = (df.groupby("year_month").agg(revenue=("revenue","sum"), orders=("order_id","count"))
               .reset_index().sort_values("year_month"))
    monthly["ma3"] = monthly["revenue"].rolling(3, min_periods=1).mean()

    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(x=monthly["year_month"], y=monthly["revenue"], name="Revenue",
                         marker=dict(color=BLUES[4], opacity=0.7),
                         hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly["year_month"], y=monthly["ma3"], name="3M Avg",
                             line=dict(color="#22c55e", width=2.5),
                             hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly["year_month"], y=monthly["orders"], name="Orders",
                             line=dict(color="#f59e0b", width=1.5, dash="dot"),
                             hovertemplate="<b>%{x}</b><br>%{y:,}<extra></extra>"), secondary_y=True)
    fig.update_layout(**BL("Monthly Revenue & Order Volume", 360))
    fig.update_xaxes(gridcolor=GRID, linecolor=GRID)
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False, gridcolor=GRID, linecolor=GRID)
    fig.update_yaxes(title_text="Orders", secondary_y=True, gridcolor=GRID, showgrid=False)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-label">Revenue by Category</div>', unsafe_allow_html=True)
        cat_r = df.groupby("category")["revenue"].sum().sort_values().reset_index()
        fig2 = go.Figure(go.Bar(x=cat_r["revenue"], y=cat_r["category"], orientation="h",
                                marker=dict(color=cat_r["revenue"], colorscale="Blues", showscale=False),
                                text=cat_r["revenue"].map(lambda x: f"${x/1e3:.0f}K"),
                                textposition="outside", textfont=dict(color=TEXT, size=10),
                                hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>"))
        fig2.update_layout(**BL(h=300))
        fig2.update_xaxes(showgrid=False, showticklabels=False)
        fig2.update_yaxes(gridcolor=GRID, linecolor=GRID)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown('<div class="section-label">Payment Methods</div>', unsafe_allow_html=True)
        pay = df.groupby("payment_type")["revenue"].sum().reset_index()
        fig3 = go.Figure(go.Pie(labels=pay["payment_type"], values=pay["revenue"],
                                hole=0.55, marker=dict(colors=CAT10),
                                textinfo="percent+label", textfont=dict(color="#8ab0d0", size=10),
                                hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>"))
        fig3.update_layout(**BL(h=300))
        st.plotly_chart(fig3, use_container_width=True)

    yoy_str = f"+{yoy:.1f}%" if yoy >= 0 else f"{yoy:.1f}%"
    st.markdown(f"""<div class="insight">
    <strong>Key Insight:</strong> Revenue shows clear Q4 seasonality (Nov–Dec spikes).
    YoY growth: <strong>{yoy_str}</strong>. Electronics leads category revenue.
    Credit cards account for ~74% of GMV.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════
with t2:
    cat_p = df.groupby("category").agg(
        revenue=("revenue","sum"), orders=("order_id","count"),
        avg_price=("product_price","mean"), avg_score=("review_score","mean"),
    ).reset_index()
    cat_p["aov"]   = cat_p["revenue"] / cat_p["orders"]
    cat_p["share"] = cat_p["revenue"] / cat_p["revenue"].sum() * 100

    st.markdown('<div class="section-label">Category Performance Matrix</div>', unsafe_allow_html=True)
    fig_b = px.scatter(cat_p, x="avg_price", y="avg_score", size="revenue", color="category",
                       color_discrete_sequence=CAT10, size_max=55,
                       hover_data={"revenue":":.0f","orders":":,","share":":.1f"},
                       labels={"avg_price":"Avg Price ($)","avg_score":"Avg Review","revenue":"Revenue ($)"})
    fig_b.update_layout(**BL("Price vs Satisfaction vs Revenue (bubble = revenue)", 400))
    fig_b.update_xaxes(gridcolor=GRID); fig_b.update_yaxes(gridcolor=GRID, range=[3.5,5.2])
    st.plotly_chart(fig_b, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-label">Revenue Share</div>', unsafe_allow_html=True)
        cs = cat_p.sort_values("revenue", ascending=False)
        fig_s = go.Figure(go.Bar(x=cs["category"], y=cs["share"],
                                 marker=dict(color=cs["share"], colorscale="Blues", showscale=False),
                                 text=cs["share"].map(lambda x: f"{x:.1f}%"),
                                 textposition="outside", textfont=dict(color=TEXT, size=10),
                                 hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>"))
        fig_s.update_layout(**BL(h=300))
        fig_s.update_xaxes(tickangle=30, gridcolor=GRID); fig_s.update_yaxes(gridcolor=GRID)
        st.plotly_chart(fig_s, use_container_width=True)

    with c2:
        st.markdown('<div class="section-label">Average Order Value</div>', unsafe_allow_html=True)
        ca = cat_p.sort_values("aov", ascending=False)
        fig_a = go.Figure(go.Bar(x=ca["category"], y=ca["aov"],
                                 marker=dict(color=ca["aov"], colorscale="Greens", showscale=False),
                                 text=ca["aov"].map(lambda x: f"${x:.0f}"),
                                 textposition="outside", textfont=dict(color=TEXT, size=10),
                                 hovertemplate="<b>%{x}</b><br>$%{y:.2f}<extra></extra>"))
        fig_a.update_layout(**BL(h=300))
        fig_a.update_xaxes(tickangle=30, gridcolor=GRID); fig_a.update_yaxes(gridcolor=GRID)
        st.plotly_chart(fig_a, use_container_width=True)

    st.markdown('<div class="section-label">Summary Table</div>', unsafe_allow_html=True)
    disp = cat_p[["category","revenue","orders","aov","avg_score","share"]].copy()
    disp.columns = ["Category","Revenue ($)","Orders","AOV ($)","Avg Score","Share (%)"]
    disp = disp.sort_values("Revenue ($)", ascending=False)
    disp["Revenue ($)"] = disp["Revenue ($)"].map("${:,.0f}".format)
    disp["AOV ($)"]     = disp["AOV ($)"].map("${:.2f}".format)
    disp["Avg Score"]   = disp["Avg Score"].map("{:.2f}".format)
    disp["Share (%)"]   = disp["Share (%)"].map("{:.1f}%".format)
    st.dataframe(disp, use_container_width=True, hide_index=True)

# ══════════════════════════
with t3:
    st.markdown('<div class="section-label">RFM Segmentation</div>', unsafe_allow_html=True)
    st.markdown("""<div class="insight">
    <strong>RFM Analysis</strong> segments customers by <strong>Recency</strong>,
    <strong>Frequency</strong>, and <strong>Monetary</strong> value.
    Industry standard for e-commerce customer analytics.
    </div>""", unsafe_allow_html=True)

    snap = df["order_date"].max()
    rfm  = df.groupby("customer_id").agg(
        recency=("order_date", lambda x: (snap-x.max()).days),
        frequency=("order_id","count"),
        monetary=("revenue","sum"),
    ).reset_index()
    rfm["R"] = pd.qcut(rfm["recency"],   5, labels=[5,4,3,2,1]).astype(int)
    rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M"] = pd.qcut(rfm["monetary"],  5, labels=[1,2,3,4,5]).astype(int)
    rfm["score"] = rfm["R"] + rfm["F"] + rfm["M"]

    def seg(r):
        if r["score"] >= 13:   return "Champions"
        elif r["R"] >= 4:      return "Loyal"
        elif r["R"] >= 3 and r["F"] >= 3: return "Potential Loyalists"
        elif r["R"] >= 4 and r["F"] <= 2: return "Recent"
        elif r["R"] <= 2 and r["score"] >= 9: return "At-Risk"
        elif r["R"] <= 2 and r["M"] >= 4: return "Cant Lose"
        elif r["R"] <= 2:      return "Lost"
        else:                  return "Needs Attention"
    rfm["Segment"] = rfm.apply(seg, axis=1)

    seg_s = rfm.groupby("Segment").agg(
        Customers=("customer_id","count"),
        Avg_Monetary=("monetary","mean"),
    ).reset_index()
    seg_s["Rev_Share"] = (seg_s["Customers"]*seg_s["Avg_Monetary"] /
                          (seg_s["Customers"]*seg_s["Avg_Monetary"]).sum()*100)

    c1, c2 = st.columns(2)
    with c1:
        fig_p = go.Figure(go.Pie(labels=seg_s["Segment"], values=seg_s["Customers"],
                                 hole=0.5, marker=dict(colors=CAT10),
                                 textinfo="percent+label", textfont=dict(color="#8ab0d0", size=10)))
        fig_p.update_layout(**BL("Customer Distribution by Segment", 360))
        st.plotly_chart(fig_p, use_container_width=True)

    with c2:
        ss = seg_s.sort_values("Rev_Share", ascending=False)
        fig_rs = go.Figure(go.Bar(x=ss["Segment"], y=ss["Rev_Share"],
                                  marker=dict(color=CAT10[:len(ss)]),
                                  text=ss["Rev_Share"].map(lambda x: f"{x:.0f}%"),
                                  textposition="outside", textfont=dict(color=TEXT, size=10),
                                  hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>"))
        fig_rs.update_layout(**BL("Revenue Share by Segment", 360))
        fig_rs.update_xaxes(tickangle=20, gridcolor=GRID); fig_rs.update_yaxes(gridcolor=GRID)
        st.plotly_chart(fig_rs, use_container_width=True)

    st.markdown('<div class="section-label">RFM Scatter</div>', unsafe_allow_html=True)
    samp = rfm.sample(min(2000, len(rfm)), random_state=42)
    fig_sc = px.scatter(samp, x="frequency", y="monetary", color="Segment",
                        size="score", color_discrete_sequence=CAT10, opacity=0.65, size_max=14,
                        labels={"frequency":"Order Frequency","monetary":"Total Spend ($)"})
    fig_sc.update_layout(**BL("Customer Scatter: Frequency vs Lifetime Value", 380))
    fig_sc.update_xaxes(gridcolor=GRID); fig_sc.update_yaxes(gridcolor=GRID)
    st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown('<div class="section-label">Revenue by State</div>', unsafe_allow_html=True)
    geo = df.groupby("customer_state").agg(revenue=("revenue","sum")).reset_index().sort_values("revenue", ascending=False)
    fig_g = go.Figure(go.Bar(x=geo["customer_state"], y=geo["revenue"],
                             marker=dict(color=geo["revenue"], colorscale="Blues", showscale=False),
                             hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"))
    fig_g.update_layout(**BL("Revenue by State", 280))
    fig_g.update_xaxes(gridcolor=GRID); fig_g.update_yaxes(gridcolor=GRID)
    st.plotly_chart(fig_g, use_container_width=True)

# ══════════════════════════
with t4:
    delivered   = df[df["order_status"]=="delivered"]
    avg_del     = delivered["delivery_days"].mean()
    on_time     = (delivered["delivery_days"] <= 10).mean()*100
    cancel_rate = (df["order_status"]=="canceled").mean()*100
    avg_freight = df["freight_value"].mean()

    ops = [
        ("Avg Delivery",  f"{avg_del:.1f} days", "Target: 10 days",  None,  "#1e3a6e"),
        ("On-Time Rate",  f"{on_time:.1f}%",      "Within 10 days",   True,  "#1a3d2e"),
        ("Cancel Rate",   f"{cancel_rate:.1f}%",  "Orders canceled",  False, "#3d1a1a"),
        ("Avg Freight",   f"${avg_freight:.2f}",  "Per order",        None,  "#2a2a1a"),
    ]
    cols = st.columns(4)
    for col, (label, val, note, pos, accent) in zip(cols, ops):
        dc = "kpi-delta-pos" if pos is True else ("kpi-delta-neg" if pos is False else "kpi-delta-neu")
        col.markdown(f"""
        <div class="kpi-card" style="--accent:{accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <div class="{dc}">{note}</div>
        </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-label">Delivery Time Distribution</div>', unsafe_allow_html=True)
        fig_d = go.Figure(go.Histogram(x=delivered["delivery_days"], nbinsx=30,
                                       marker=dict(color=BLUES[4], opacity=0.8),
                                       hovertemplate="Days: %{x}<br>Count: %{y}<extra></extra>"))
        fig_d.add_vline(x=avg_del, line_dash="dash", line_color="#22c55e",
                        annotation_text=f"Avg {avg_del:.1f}d",
                        annotation_font_color="#22c55e", annotation_font_size=11)
        fig_d.update_layout(**BL("Distribution of Delivery Times", 300))
        fig_d.update_xaxes(gridcolor=GRID); fig_d.update_yaxes(gridcolor=GRID)
        st.plotly_chart(fig_d, use_container_width=True)

    with c2:
        st.markdown('<div class="section-label">Delivery by Category</div>', unsafe_allow_html=True)
        dc_df = delivered.groupby("category")["delivery_days"].mean().sort_values().reset_index()
        fig_dc = go.Figure(go.Bar(x=dc_df["delivery_days"], y=dc_df["category"], orientation="h",
                                  marker=dict(color=dc_df["delivery_days"], colorscale="RdYlGn_r", showscale=False),
                                  text=dc_df["delivery_days"].map(lambda x: f"{x:.1f}d"),
                                  textposition="outside", textfont=dict(color=TEXT, size=10),
                                  hovertemplate="<b>%{y}</b><br>%{x:.1f} days<extra></extra>"))
        fig_dc.update_layout(**BL("Avg Delivery Days by Category", 300))
        fig_dc.update_xaxes(showgrid=False, showticklabels=False)
        fig_dc.update_yaxes(gridcolor=GRID)
        st.plotly_chart(fig_dc, use_container_width=True)

    st.markdown('<div class="section-label">Review Score Distribution</div>', unsafe_allow_html=True)
    sc_d = df["review_score"].value_counts().sort_index().reset_index()
    sc_d.columns = ["Score","Count"]
    colors_sc = {1:"#ef4444",2:"#f97316",3:"#94a3b8",4:"#86efac",5:"#22c55e"}
    fig_sc2 = go.Figure(go.Bar(x=sc_d["Score"], y=sc_d["Count"],
                                marker_color=[colors_sc[s] for s in sc_d["Score"]],
                                text=sc_d["Count"].map(lambda x: f"{x:,}"),
                                textposition="outside", textfont=dict(color=TEXT, size=10),
                                hovertemplate="Score %{x}★<br>%{y:,} reviews<extra></extra>"))
    fig_sc2.update_layout(**BL("Customer Review Scores", 280))
    fig_sc2.update_xaxes(tickmode="linear", gridcolor=GRID)
    fig_sc2.update_yaxes(gridcolor=GRID)
    st.plotly_chart(fig_sc2, use_container_width=True)

# ══════════════════════════
with t5:
    st.markdown('<div class="section-label">Revenue Anomaly Detection — Z-Score Method</div>', unsafe_allow_html=True)
    st.markdown("""<div class="insight">
    Flags days where revenue deviates more than <strong>±2 standard deviations</strong>
    from the 30-day rolling mean. <strong>Green triangles</strong> = revenue spikes.
    <strong>Red triangles</strong> = drops worth investigating.
    </div>""", unsafe_allow_html=True)

    daily = df.groupby("order_date")["revenue"].sum().reset_index().sort_values("order_date")
    daily["mean30"] = daily["revenue"].rolling(30, min_periods=7).mean()
    daily["std30"]  = daily["revenue"].rolling(30, min_periods=7).std()
    daily["z"]      = (daily["revenue"] - daily["mean30"]) / daily["std30"]
    daily["flag"]   = daily["z"].abs() > 2
    daily["type"]   = np.where(daily["z"]>2,"Spike",np.where(daily["z"]<-2,"Drop","Normal"))

    pos_a = daily[daily["type"]=="Spike"]
    neg_a = daily[daily["type"]=="Drop"]

    fig_an = go.Figure()
    fig_an.add_trace(go.Scatter(x=daily["order_date"], y=daily["revenue"], mode="lines",
                                name="Daily Revenue", line=dict(color=BLUES[4], width=1.2), opacity=0.7,
                                hovertemplate="<b>%{x|%b %d %Y}</b><br>$%{y:,.0f}<extra></extra>"))
    fig_an.add_trace(go.Scatter(x=daily["order_date"], y=daily["mean30"], mode="lines",
                                name="30-Day Mean", line=dict(color="#22c55e", width=2, dash="dash")))
    fig_an.add_trace(go.Scatter(x=daily["order_date"], y=daily["mean30"]+2*daily["std30"],
                                mode="lines", name="+2 Sigma",
                                line=dict(color="#f59e0b", width=1, dash="dot")))
    fig_an.add_trace(go.Scatter(x=daily["order_date"], y=daily["mean30"]-2*daily["std30"],
                                mode="lines", name="-2 Sigma",
                                line=dict(color="#ef4444", width=1, dash="dot"),
                                fill="tonexty", fillcolor="rgba(239,68,68,0.04)"))
    fig_an.add_trace(go.Scatter(x=pos_a["order_date"], y=pos_a["revenue"], mode="markers",
                                name="Spike", marker=dict(color="#22c55e", size=9, symbol="triangle-up"),
                                hovertemplate="<b>SPIKE</b><br>%{x|%b %d}<br>$%{y:,.0f}<extra></extra>"))
    fig_an.add_trace(go.Scatter(x=neg_a["order_date"], y=neg_a["revenue"], mode="markers",
                                name="Drop", marker=dict(color="#ef4444", size=9, symbol="triangle-down"),
                                hovertemplate="<b>DROP</b><br>%{x|%b %d}<br>$%{y:,.0f}<extra></extra>"))
    fig_an.update_layout(**BL("Daily Revenue with Anomaly Detection Bands", 420))
    fig_an.update_xaxes(gridcolor=GRID); fig_an.update_yaxes(gridcolor=GRID)
    st.plotly_chart(fig_an, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        total_a = len(daily[daily["flag"]])
        st.markdown(f"""<div class="insight">
        <strong>{total_a} anomalies detected</strong><br>
        Green spikes: <strong>{len(pos_a)}</strong> &nbsp;|&nbsp;
        Red drops: <strong>{len(neg_a)}</strong>
        </div>""", unsafe_allow_html=True)
        if total_a > 0:
            top_a = daily[daily["flag"]].sort_values("z", key=abs, ascending=False).head(8)
            disp_a = top_a[["order_date","revenue","z","type"]].copy()
            disp_a.columns = ["Date","Revenue ($)","Z-Score","Type"]
            disp_a["Revenue ($)"] = disp_a["Revenue ($)"].map("${:,.0f}".format)
            disp_a["Z-Score"]     = disp_a["Z-Score"].map("{:+.2f}".format)
            disp_a["Date"]        = disp_a["Date"].dt.strftime("%Y-%m-%d")
            st.dataframe(disp_a, use_container_width=True, hide_index=True)

    with c2:
        st.markdown('<div class="section-label">Monthly Heatmap</div>', unsafe_allow_html=True)
        hm = df.groupby(["year","month"])["revenue"].sum().reset_index()
        pv = hm.pivot(index="year", columns="month", values="revenue").fillna(0)
        mn = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        pv.columns = [mn[m-1] for m in pv.columns]
        fig_h = px.imshow(pv, color_continuous_scale="Blues",
                          labels=dict(x="Month",y="Year",color="Revenue ($)"), aspect="auto")
        fig_h.update_layout(**BL("Revenue Heatmap by Year and Month", 260))
        st.plotly_chart(fig_h, use_container_width=True)

st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;border-top:1px solid #0e1825;margin-top:2rem;">
    <span style="font-family:Syne,sans-serif;font-size:0.8rem;color:#1e3a5a;letter-spacing:0.1em;">
    NAHOM WORKU &nbsp;·&nbsp; FINANCIAL ENGINEER &amp; DATA SCIENTIST &nbsp;·&nbsp; E-COMMERCE ANALYTICS v2.0
    </span>
</div>""", unsafe_allow_html=True)
