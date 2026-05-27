"""
European Bank Customer Churn Analytics Dashboard
================================================
Run with: streamlit run streamlit_dashboard.py

Requirements:
    pip install streamlit pandas numpy plotly
    
Place your CSV file (European_Bank - European_Bank.csv) in the same folder,
OR the app will generate a realistic synthetic dataset automatically.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="European Bank Churn Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a3a5c;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #4a6fa5;
        margin-bottom: 1.5rem;
    }
    .kpi-box {
        background: linear-gradient(135deg, #1a3a5c, #2e6da4);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
    }
    .kpi-label {
        font-size: 0.8rem;
        opacity: 0.85;
        margin-top: 0.2rem;
    }
    .kpi-box-warn {
        background: linear-gradient(135deg, #b5451b, #e07b39);
    }
    .kpi-box-ok {
        background: linear-gradient(135deg, #1a6b3c, #2ea86e);
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a3a5c;
        border-left: 4px solid #2e6da4;
        padding-left: 0.6rem;
        margin: 1.5rem 0 0.8rem 0;
    }
    hr.divider {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING & FEATURE ENGINEERING
# ─────────────────────────────────────────────
@st.cache_data
def load_and_prepare(path: str = None) -> pd.DataFrame:
    """Load CSV or generate synthetic data, then engineer all features."""
    if path:
        try:
            df = pd.read_csv(path)
        except Exception:
            df = None
    else:
        df = None

    if df is None:
        # ── Synthetic dataset matching project schema ──
        np.random.seed(42)
        n = 10_000
        geo = np.random.choice(["France", "Germany", "Spain"],
                               n, p=[0.50, 0.25, 0.25])
        age = np.clip(np.random.normal(38, 11, n).astype(int), 18, 92)
        tenure = np.random.randint(0, 11, n)
        balance = np.where(
            np.random.rand(n) < 0.30, 0,
            np.abs(np.random.normal(90_000, 55_000, n))
        )
        credit = np.clip(np.random.normal(650, 100, n).astype(int), 350, 850)
        salary = np.abs(np.random.normal(100_000, 40_000, n))
        products = np.random.choice([1, 2, 3, 4], n, p=[0.46, 0.46, 0.05, 0.03])
        gender = np.random.choice(["Male", "Female"], n, p=[0.54, 0.46])
        active = np.random.choice([0, 1], n, p=[0.49, 0.51])
        has_card = np.random.choice([0, 1], n, p=[0.29, 0.71])

        # Churn with realistic probabilities
        p_churn = (
            0.10
            + (geo == "Germany") * 0.14
            + (age >= 46) * 0.18
            + (gender == "Female") * 0.07
            + (active == 0) * 0.12
            + (products >= 3) * 0.35
            + (balance > np.percentile(balance, 75)) * 0.05
        )
        p_churn = np.clip(p_churn, 0, 0.95)
        exited = (np.random.rand(n) < p_churn).astype(int)

        df = pd.DataFrame({
            "CustomerId": range(1, n + 1),
            "CreditScore": credit,
            "Geography": geo,
            "Gender": gender,
            "Age": age,
            "Tenure": tenure,
            "Balance": balance,
            "NumOfProducts": products,
            "HasCrCard": has_card,
            "IsActiveMember": active,
            "EstimatedSalary": salary,
            "Exited": exited,
        })

    # ── Feature Engineering ──
    # Age groups
    bins = [18, 30, 45, 60, 120]
    labels = ["18–30", "31–45", "46–60", "60+"]
    df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels,
                             include_lowest=True)

    # Credit band
    cond_c = [df["CreditScore"] < 580,
              df["CreditScore"].between(580, 739),
              df["CreditScore"] > 739]
    df["Credit_Band"] = np.select(cond_c, ["Low", "Medium", "High"], "Medium")

    # Tenure group
    cond_t = [df["Tenure"] <= 2,
              df["Tenure"].between(3, 7),
              df["Tenure"] > 7]
    df["Tenure_Group"] = np.select(cond_t, ["New", "Mid-term", "Long-term"], "Mid-term")

    # Balance segment
    med_bal = df[df["Balance"] > 0]["Balance"].median()
    cond_b = [df["Balance"] == 0,
              (df["Balance"] > 0) & (df["Balance"] <= med_bal),
              df["Balance"] > med_bal]
    df["Balance_Segment"] = np.select(cond_b,
                                      ["Zero-balance", "Low-balance", "High-balance"],
                                      "Low-balance")

    # Customer value (multi-criteria)
    bal_lim = df["Balance"].quantile(0.75)
    sal_lim = df["EstimatedSalary"].quantile(0.75)
    scr_lim = df["CreditScore"].quantile(0.75)
    score = (
        (df["Balance"] >= bal_lim).astype(int)
        + (df["EstimatedSalary"] >= sal_lim).astype(int)
        + (df["CreditScore"] >= scr_lim).astype(int)
    )
    df["Customer_Value"] = np.where(score >= 2, "High-Value", "Low-Value")

    return df


# ── Try to load user CSV, fall back to synthetic ──
import os
CSV_PATH = "European_Bank_Churn_Final.csv"
df = load_and_prepare(CSV_PATH if os.path.exists(CSV_PATH) else None)


# ─────────────────────────────────────────────
# SIDEBAR — FILTERS
# ─────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/"
    "Wikimedia_Foundation_RGB_logo_with_text.svg/200px-Wikimedia_Foundation_RGB_logo_with_text.svg.png",
    width=40,
)
st.sidebar.markdown("## 🏦 Filter Panel")

geo_opts = ["All"] + sorted(df["Geography"].unique().tolist())
gender_opts = ["All"] + sorted(df["Gender"].unique().tolist())
age_opts = ["All"] + list(df["Age_Group"].cat.categories)
value_opts = ["All", "High-Value", "Low-Value"]
tenure_opts = ["All", "New", "Mid-term", "Long-term"]

sel_geo = st.sidebar.multiselect("Geography", options=geo_opts[1:],
                                  default=geo_opts[1:])
sel_gender = st.sidebar.multiselect("Gender", options=gender_opts[1:],
                                     default=gender_opts[1:])
sel_age = st.sidebar.multiselect("Age Group", options=age_opts[1:],
                                  default=age_opts[1:])
sel_value = st.sidebar.selectbox("Customer Value", value_opts)
sel_tenure = st.sidebar.selectbox("Tenure Group", tenure_opts)

st.sidebar.markdown("---")
st.sidebar.caption("European Central Bank | Churn Analytics Dashboard")

# Apply filters
fdf = df.copy()
if sel_geo:
    fdf = fdf[fdf["Geography"].isin(sel_geo)]
if sel_gender:
    fdf = fdf[fdf["Gender"].isin(sel_gender)]
if sel_age:
    fdf = fdf[fdf["Age_Group"].isin(sel_age)]
if sel_value != "All":
    fdf = fdf[fdf["Customer_Value"] == sel_value]
if sel_tenure != "All":
    fdf = fdf[fdf["Tenure_Group"] == sel_tenure]


# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────
PALETTE = px.colors.qualitative.Set2
CHURN_COLORS = {"Churned": "#e05c2e", "Retained": "#2e6da4"}

def churn_rate(d: pd.DataFrame) -> float:
    return d["Exited"].mean() * 100 if len(d) else 0.0


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-header">🏦 European Bank Churn Analytics</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-header">Customer Segmentation & Churn Pattern Analytics · '
            'European Central Bank Internship Project</div>',
            unsafe_allow_html=True)

data_note = "🟡 Using synthetic data (CSV not found)" \
    if not os.path.exists(CSV_PATH) else "🟢 Live dataset loaded"
st.caption(data_note + f" · {len(fdf):,} customers in view")
st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MODULE 1 — KPI SUMMARY
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Overall Churn Summary</div>',
            unsafe_allow_html=True)

total = len(fdf)
churned = fdf["Exited"].sum()
retained = total - churned
overall_cr = churn_rate(fdf)
hv_cr = churn_rate(fdf[fdf["Customer_Value"] == "High-Value"])
inactive_cr = churn_rate(fdf[fdf["IsActiveMember"] == 0])

c1, c2, c3, c4, c5 = st.columns(5)

def kpi_html(value, label, variant=""):
    cls = f"kpi-box {variant}"
    return f"""
    <div class="{cls}">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>"""

c1.markdown(kpi_html(f"{total:,}", "Total Customers"), unsafe_allow_html=True)
c2.markdown(kpi_html(f"{churned:,}", "Churned Customers", "kpi-box-warn"),
            unsafe_allow_html=True)
c3.markdown(kpi_html(f"{overall_cr:.1f}%", "Overall Churn Rate",
                     "kpi-box-warn" if overall_cr > 20 else ""),
            unsafe_allow_html=True)
c4.markdown(kpi_html(f"{hv_cr:.1f}%", "High-Value Churn Rate",
                     "kpi-box-warn" if hv_cr > 20 else ""),
            unsafe_allow_html=True)
c5.markdown(kpi_html(f"{inactive_cr:.1f}%", "Inactive Member Churn",
                     "kpi-box-warn"), unsafe_allow_html=True)

# ── Financial Impact Calculations ──
bal_lost = fdf[fdf["Exited"] == 1]["Balance"].sum()
bal_retained = fdf[fdf["Exited"] == 0]["Balance"].sum()

def format_compact_euro(val: float) -> str:
    if val >= 1_000_000_000:
        return f"€{val / 1_000_000_000:.2f}B"
    elif val >= 1_000_000:
        return f"€{val / 1_000_000:.2f}M"
    elif val >= 1_000:
        return f"€{val / 1_000:.1f}K"
    else:
        return f"€{val:,.2f}"

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
cf1, cf2 = st.columns(2)

cf1.markdown(kpi_html(format_compact_euro(bal_retained), "Capital Retained (Active Balances)", "kpi-box-ok"), unsafe_allow_html=True)
cf2.markdown(kpi_html(format_compact_euro(bal_lost), "Capital Lost (Churn Outflow)", "kpi-box-warn"), unsafe_allow_html=True)

# Donut chart
st.markdown("")
col_a, col_b = st.columns([1, 2])
with col_a:
    fig_donut = go.Figure(go.Pie(
        labels=["Retained", "Churned"],
        values=[retained, churned],
        hole=0.6,
        marker_colors=["#2e6da4", "#e05c2e"],
        textinfo="percent+label",
    ))
    fig_donut.update_layout(
        title="Churn vs Retained", height=300,
        margin=dict(t=40, b=10, l=10, r=10),
        showlegend=False,
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_b:
    # Product count churn
    prod_churn = (
        fdf.groupby("NumOfProducts")["Exited"]
        .agg(["mean", "count"])
        .reset_index()
    )
    prod_churn.columns = ["Products", "Churn Rate", "Count"]
    prod_churn["Churn Rate %"] = prod_churn["Churn Rate"] * 100

    fig_prod = px.bar(
        prod_churn, x="Products", y="Churn Rate %",
        color="Churn Rate %",
        color_continuous_scale="Reds",
        text=prod_churn["Churn Rate %"].apply(lambda x: f"{x:.1f}%"),
        title="Churn Rate by Number of Products",
    )
    fig_prod.update_traces(textposition="outside")
    fig_prod.update_layout(height=300, margin=dict(t=40, b=10),
                           coloraxis_showscale=False)
    st.plotly_chart(fig_prod, use_container_width=True)


st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MODULE 2 — GEOGRAPHY-WISE CHURN
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🌍 Geography-Wise Churn Visualisation</div>',
            unsafe_allow_html=True)

geo_churn = (
    fdf.groupby("Geography")
    .agg(Total=("Exited", "count"), Churned=("Exited", "sum"))
    .reset_index()
)
geo_churn["Churn_Rate_%"] = geo_churn["Churned"] / geo_churn["Total"] * 100

col1, col2 = st.columns(2)

with col1:
    fig_geo_bar = px.bar(
        geo_churn, x="Geography", y="Churn_Rate_%",
        color="Geography", text=geo_churn["Churn_Rate_%"].apply(lambda x: f"{x:.1f}%"),
        title="Churn Rate by Country",
        color_discrete_sequence=PALETTE,
    )
    fig_geo_bar.update_traces(textposition="outside")
    fig_geo_bar.update_layout(showlegend=False, height=350,
                               yaxis_title="Churn Rate (%)")
    st.plotly_chart(fig_geo_bar, use_container_width=True)

with col2:
    geo_gender = (
        fdf.groupby(["Geography", "Gender"])["Exited"]
        .mean()
        .reset_index()
    )
    geo_gender["Churn_Rate_%"] = geo_gender["Exited"] * 100
    fig_geo_gender = px.bar(
        geo_gender, x="Geography", y="Churn_Rate_%",
        color="Gender", barmode="group",
        title="Churn Rate: Geography × Gender",
        color_discrete_sequence=["#2e6da4", "#e05c2e"],
        text=geo_gender["Churn_Rate_%"].apply(lambda x: f"{x:.1f}%"),
    )
    fig_geo_gender.update_traces(textposition="outside")
    fig_geo_gender.update_layout(height=350, yaxis_title="Churn Rate (%)")
    st.plotly_chart(fig_geo_gender, use_container_width=True)

# Risk index map (choropleth-style table)
geo_churn["Geographic Risk Index"] = geo_churn["Churn_Rate_%"].apply(
    lambda x: "🔴 High" if x >= 25 else ("🟡 Medium" if x >= 18 else "🟢 Low")
)
st.dataframe(
    geo_churn[["Geography", "Total", "Churned", "Churn_Rate_%",
               "Geographic Risk Index"]]
    .rename(columns={"Churn_Rate_%": "Churn Rate (%)"}),
    use_container_width=True, hide_index=True,
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MODULE 3 — AGE & TENURE CHURN
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">👥 Age & Tenure Churn Comparison</div>',
            unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    age_churn = (
        fdf.groupby("Age_Group", observed=True)["Exited"]
        .mean()
        .reset_index()
    )
    age_churn["Churn_Rate_%"] = age_churn["Exited"] * 100
    fig_age = px.bar(
        age_churn, x="Age_Group", y="Churn_Rate_%",
        color="Age_Group",
        text=age_churn["Churn_Rate_%"].apply(lambda x: f"{x:.1f}%"),
        title="Churn Rate by Age Group",
        color_discrete_sequence=px.colors.sequential.Viridis,
    )
    fig_age.update_traces(textposition="outside")
    fig_age.update_layout(showlegend=False, height=350,
                           yaxis_title="Churn Rate (%)")
    st.plotly_chart(fig_age, use_container_width=True)

with col4:
    tenure_churn = (
        fdf.groupby("Tenure_Group")["Exited"]
        .mean()
        .reset_index()
    )
    tenure_churn["Churn_Rate_%"] = tenure_churn["Exited"] * 100
    order = ["New", "Mid-term", "Long-term"]
    tenure_churn["Tenure_Group"] = pd.Categorical(
        tenure_churn["Tenure_Group"], categories=order, ordered=True
    )
    tenure_churn = tenure_churn.sort_values("Tenure_Group")
    fig_ten = px.bar(
        tenure_churn, x="Tenure_Group", y="Churn_Rate_%",
        color="Tenure_Group",
        text=tenure_churn["Churn_Rate_%"].apply(lambda x: f"{x:.1f}%"),
        title="Churn Rate by Tenure Group",
        color_discrete_sequence=PALETTE,
    )
    fig_ten.update_traces(textposition="outside")
    fig_ten.update_layout(showlegend=False, height=350,
                           yaxis_title="Churn Rate (%)")
    st.plotly_chart(fig_ten, use_container_width=True)

# Age × Geography heatmap
age_geo = (
    fdf.groupby(["Age_Group", "Geography"], observed=True)["Exited"]
    .mean()
    .reset_index()
)
age_geo["Churn_Rate_%"] = (age_geo["Exited"] * 100).round(1)
pivot = age_geo.pivot(index="Age_Group", columns="Geography",
                      values="Churn_Rate_%")

fig_heat = px.imshow(
    pivot,
    color_continuous_scale="RdYlGn_r",
    title="Churn Rate Heatmap: Age Group × Geography",
    text_auto=True,
    aspect="auto",
)
fig_heat.update_layout(height=320)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MODULE 4 — HIGH-VALUE CUSTOMER CHURN EXPLORER
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">💎 High-Value Customer Churn Explorer</div>',
            unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    val_churn = (
        fdf.groupby("Customer_Value")["Exited"]
        .agg(["mean", "count", "sum"])
        .reset_index()
    )
    val_churn.columns = ["Segment", "Churn Rate", "Total", "Churned"]
    val_churn["Churn Rate %"] = val_churn["Churn Rate"] * 100

    fig_val = px.bar(
        val_churn, x="Segment", y="Churn Rate %",
        color="Segment",
        text=val_churn["Churn Rate %"].apply(lambda x: f"{x:.1f}%"),
        title="Churn Rate: High-Value vs Low-Value",
        color_discrete_map={"High-Value": "#e05c2e", "Low-Value": "#2e6da4"},
    )
    fig_val.update_traces(textposition="outside")
    fig_val.update_layout(showlegend=False, height=350,
                           yaxis_title="Churn Rate (%)")
    st.plotly_chart(fig_val, use_container_width=True)

with col6:
    # Balance segment churn
    bal_churn = (
        fdf.groupby("Balance_Segment")["Exited"]
        .mean()
        .reset_index()
    )
    bal_churn["Churn_Rate_%"] = bal_churn["Exited"] * 100
    order_b = ["Zero-balance", "Low-balance", "High-balance"]
    bal_churn["Balance_Segment"] = pd.Categorical(
        bal_churn["Balance_Segment"], categories=order_b, ordered=True
    )
    bal_churn = bal_churn.sort_values("Balance_Segment")
    fig_bal = px.bar(
        bal_churn, x="Balance_Segment", y="Churn_Rate_%",
        color="Balance_Segment",
        text=bal_churn["Churn_Rate_%"].apply(lambda x: f"{x:.1f}%"),
        title="Churn Rate by Balance Segment",
        color_discrete_sequence=["#4a90d9", "#2e6da4", "#e05c2e"],
    )
    fig_bal.update_traces(textposition="outside")
    fig_bal.update_layout(showlegend=False, height=350,
                           yaxis_title="Churn Rate (%)")
    st.plotly_chart(fig_bal, use_container_width=True)

# Credit band churn
col7, col8 = st.columns(2)
with col7:
    credit_churn = (
        fdf.groupby("Credit_Band")["Exited"]
        .mean()
        .reset_index()
    )
    credit_churn["Churn_Rate_%"] = credit_churn["Exited"] * 100
    order_cr = ["Low", "Medium", "High"]
    credit_churn["Credit_Band"] = pd.Categorical(
        credit_churn["Credit_Band"], categories=order_cr, ordered=True
    )
    credit_churn = credit_churn.sort_values("Credit_Band")
    fig_cr = px.bar(
        credit_churn, x="Credit_Band", y="Churn_Rate_%",
        color="Credit_Band",
        text=credit_churn["Churn_Rate_%"].apply(lambda x: f"{x:.1f}%"),
        title="Churn Rate by Credit Band",
        color_discrete_sequence=PALETTE,
    )
    fig_cr.update_traces(textposition="outside")
    fig_cr.update_layout(showlegend=False, height=320,
                          yaxis_title="Churn Rate (%)")
    st.plotly_chart(fig_cr, use_container_width=True)

with col8:
    # Active vs Inactive churn
    act_churn = (
        fdf.groupby("IsActiveMember")["Exited"]
        .mean()
        .reset_index()
    )
    act_churn["Membership"] = act_churn["IsActiveMember"].map(
        {0: "Inactive", 1: "Active"}
    )
    act_churn["Churn_Rate_%"] = act_churn["Exited"] * 100
    fig_act = px.bar(
        act_churn, x="Membership", y="Churn_Rate_%",
        color="Membership",
        text=act_churn["Churn_Rate_%"].apply(lambda x: f"{x:.1f}%"),
        title="Churn Rate: Active vs Inactive Members",
        color_discrete_map={"Active": "#2e6da4", "Inactive": "#e05c2e"},
    )
    fig_act.update_traces(textposition="outside")
    fig_act.update_layout(showlegend=False, height=320,
                           yaxis_title="Churn Rate (%)")
    st.plotly_chart(fig_act, use_container_width=True)

# Scatter: Balance vs Salary colored by churn
st.markdown("#### Balance vs Estimated Salary — Churned vs Retained")
sample = fdf.sample(min(2000, len(fdf)), random_state=42)
sample["Status"] = sample["Exited"].map({0: "Retained", 1: "Churned"})
fig_scatter = px.scatter(
    sample, x="Balance", y="EstimatedSalary",
    color="Status",
    color_discrete_map=CHURN_COLORS,
    opacity=0.5,
    title="Balance vs Salary — Churned vs Retained",
    hover_data=["Age", "Geography", "NumOfProducts"],
)
fig_scatter.update_layout(height=400)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MODULE 5 — DRILL-DOWN TABLE
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🔍 Segment Drill-Down Table</div>',
            unsafe_allow_html=True)

group_col = st.selectbox(
    "Group by dimension:",
    ["Geography", "Age_Group", "Gender", "Tenure_Group",
     "Balance_Segment", "Credit_Band", "Customer_Value", "NumOfProducts"],
)

drill = (
    fdf.groupby(group_col, observed=True)
    .agg(
        Customers=("Exited", "count"),
        Churned=("Exited", "sum"),
        Avg_Balance=("Balance", "mean"),
        Avg_Salary=("EstimatedSalary", "mean"),
        Avg_CreditScore=("CreditScore", "mean"),
    )
    .reset_index()
)
drill["Churn Rate (%)"] = (drill["Churned"] / drill["Customers"] * 100).round(1)
drill["Avg_Balance"] = drill["Avg_Balance"].apply(lambda x: f"€{x:,.0f}")
drill["Avg_Salary"] = drill["Avg_Salary"].apply(lambda x: f"€{x:,.0f}")
drill["Avg_CreditScore"] = drill["Avg_CreditScore"].apply(lambda x: f"{x:.0f}")

st.dataframe(drill, use_container_width=True, hide_index=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#888; font-size:0.8rem; padding: 1rem 0;">
    European Bank Churn Analytics Dashboard &nbsp;·&nbsp;
    European Central Bank Internship Program &nbsp;·&nbsp;
    Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
