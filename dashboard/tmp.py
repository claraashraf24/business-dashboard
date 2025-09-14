import streamlit as st
import pandas as pd
import os
import plotly.express as px
from report_generator import create_pdf_report
import plotly.io as pio
import kaleido  # ensure kaleido engine is registered

# Reuse our data loader
from data_loader import load_data

# Load data
df = load_data()

# --- Dashboard Layout ---
st.set_page_config(page_title="Business Dashboard", layout="wide")

st.title("📊 Business Dashboard")
st.markdown("This dashboard shows **Sales, Traffic, and Customer Insights** from our business dataset.")

# --- Sidebar filters ---
st.sidebar.header("Filters")
selected_region = st.sidebar.multiselect(
    "Select Region:",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)
selected_product = st.sidebar.multiselect(
    "Select Product:",
    options=df["Product"].unique(),
    default=df["Product"].unique()
)

# --- Date Range Filter ---
st.sidebar.subheader("Date Range")
min_date = df["Date"].min()
max_date = df["Date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range:",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply filters
df_filtered = df[
    (df["Region"].isin(selected_region)) &
    (df["Product"].isin(selected_product))
]

if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[
        (df_filtered["Date"] >= pd.to_datetime(start_date)) &
        (df_filtered["Date"] <= pd.to_datetime(end_date))
    ]

# --- Export Data ---
st.sidebar.subheader("Export")
csv = df_filtered.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    "📥 Download CSV",
    data=csv,
    file_name="business_data_filtered.csv",
    mime="text/csv"
)

# --- KPI Section ---
st.subheader("Key Performance Indicators")

total_revenue = int(df_filtered["Revenue"].sum())
total_sales = int(df_filtered["Sales"].sum())
aov = round(total_revenue / total_sales, 2) if total_sales > 0 else 0
conversion_rate = round(
    df_filtered["Sales"].sum() / df_filtered["Visitors"].sum() * 100, 2
) if df_filtered["Visitors"].sum() > 0 else 0
total_customers = int(df_filtered["Customers"].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${total_revenue:,}")
col2.metric("🛒 Total Sales", f"{total_sales:,}")
col3.metric("📊 AOV", f"${aov}")
col4.metric("👥 Customers", f"{total_customers:,}")

st.metric("⚡ Conversion Rate", f"{conversion_rate}%")

# --- Weekly / Monthly Change Comparisons ---

st.subheader("📊 Weekly Performance Change")

weekly = df_filtered.groupby(df_filtered["Date"].dt.isocalendar().week).agg({
    "Revenue": "sum",
    "Sales": "sum",
    "Customers": "sum",
    "Visitors": "sum"
})

if len(weekly) >= 2:
    last_week = weekly.iloc[-2]
    this_week = weekly.iloc[-1]

    # Revenue
    rev_change = ((this_week["Revenue"] - last_week["Revenue"]) / last_week["Revenue"] * 100
                  if last_week["Revenue"] > 0 else 0)

    # Sales
    sales_change = ((this_week["Sales"] - last_week["Sales"]) / last_week["Sales"] * 100
                    if last_week["Sales"] > 0 else 0)

    # Customers
    cust_change = ((this_week["Customers"] - last_week["Customers"]) / last_week["Customers"] * 100
                   if last_week["Customers"] > 0 else 0)

    # Conversion Rate
    conv_last = (last_week["Sales"] / last_week["Visitors"] * 100) if last_week["Visitors"] > 0 else 0
    conv_this = (this_week["Sales"] / this_week["Visitors"] * 100) if this_week["Visitors"] > 0 else 0
    conv_change = conv_this - conv_last

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenue", f"${this_week['Revenue']:,}", f"{rev_change:.2f}% vs last week")
    col2.metric("Sales", f"{int(this_week['Sales']):,}", f"{sales_change:.2f}% vs last week")
    col3.metric("Customers", f"{int(this_week['Customers']):,}", f"{cust_change:.2f}% vs last week")
    col4.metric("Conversion Rate", f"{conv_this:.2f}%", f"{conv_change:.2f} pts vs last week")


st.subheader("📊 Monthly Performance Change")

monthly = df_filtered.groupby(df_filtered["Date"].dt.to_period("M")).agg({
    "Revenue": "sum",
    "Sales": "sum",
    "Customers": "sum",
    "Visitors": "sum"
})

if len(monthly) >= 2:
    last_month = monthly.iloc[-2]
    this_month = monthly.iloc[-1]

    # Revenue
    rev_change_m = ((this_month["Revenue"] - last_month["Revenue"]) / last_month["Revenue"] * 100
                    if last_month["Revenue"] > 0 else 0)

    # Sales
    sales_change_m = ((this_month["Sales"] - last_month["Sales"]) / last_month["Sales"] * 100
                      if last_month["Sales"] > 0 else 0)

    # Customers
    cust_change_m = ((this_month["Customers"] - last_month["Customers"]) / last_month["Customers"] * 100
                     if last_month["Customers"] > 0 else 0)

    # Conversion Rate
    conv_last_m = (last_month["Sales"] / last_month["Visitors"] * 100) if last_month["Visitors"] > 0 else 0
    conv_this_m = (this_month["Sales"] / this_month["Visitors"] * 100) if this_month["Visitors"] > 0 else 0
    conv_change_m = conv_this_m - conv_last_m

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenue", f"${this_month['Revenue']:,}", f"{rev_change_m:.2f}% vs last month")
    col2.metric("Sales", f"{int(this_month['Sales']):,}", f"{sales_change_m:.2f}% vs last month")
    col3.metric("Customers", f"{int(this_month['Customers']):,}", f"{cust_change_m:.2f}% vs last month")
    col4.metric("Conversion Rate", f"{conv_this_m:.2f}%", f"{conv_change_m:.2f} pts vs last month")



# --- Revenue Trend with Granularity Toggle ---
st.subheader("Revenue Trend Over Time")

# Add a toggle for granularity
granularity = st.radio(
    "Select Date Granularity:",
    ["Daily", "Weekly", "Monthly"],
    horizontal=True
)

df_trend = df_filtered.copy()

if granularity == "Weekly":
    df_trend = df_trend.groupby(df_trend["Date"].dt.isocalendar().week).agg(
        {"Revenue": "sum"}
    ).reset_index().rename(columns={"week": "Period"})
    x_col = "Period"   # ✅ FIXED here
elif granularity == "Monthly":
    df_trend = df_trend.groupby(df_trend["Date"].dt.to_period("M")).agg(
        {"Revenue": "sum"}
    ).reset_index().rename(columns={"Date": "Period"})
    df_trend["Period"] = df_trend["Period"].astype(str)
    x_col = "Period"
else:  # Daily
    df_trend["Period"] = df_trend["Date"]
    x_col = "Period"

fig_revenue = px.line(
    df_trend, x=x_col, y="Revenue",
    title=f"Revenue Over Time ({granularity})", markers=True
)
st.plotly_chart(fig_revenue, use_container_width=True)



# --- Weekly Revenue Comparison ---
df_filtered["Week"] = df_filtered["Date"].dt.isocalendar().week
weekly_revenue = df_filtered.groupby("Week")["Revenue"].sum().reset_index()

st.subheader("Weekly Revenue Comparison")
fig_weekly = px.bar(
    weekly_revenue, x="Week", y="Revenue",
    title="Weekly Revenue", text_auto=True
)
st.plotly_chart(fig_weekly, use_container_width=True)

# --- Customer Insights ---
st.subheader("Customer Breakdown (New vs Returning)")
fig_customers = px.area(
    df_filtered, x="Date", y=["New_Customers", "Returning_Customers"],
    title="New vs Returning Customers Over Time"
)
st.plotly_chart(fig_customers, use_container_width=True)

# --- Marketing Channel Analysis ---
st.subheader("Sales by Marketing Channel")
channel_sales = df_filtered.groupby("Marketing_Channel")["Sales"].sum().reset_index()
fig_channel = px.bar(
    channel_sales, x="Marketing_Channel", y="Sales",
    title="Sales by Channel", text_auto=True
)
st.plotly_chart(fig_channel, use_container_width=True)

# --- Regional Revenue ---
st.subheader("Revenue by Region")
region_revenue = df_filtered.groupby("Region")["Revenue"].sum().reset_index()
fig_region = px.bar(
    region_revenue, x="Region", y="Revenue",
    title="Revenue by Region", text_auto=True
)
st.plotly_chart(fig_region, use_container_width=True)

# --- PDF Export Section ---
st.subheader("📄 Export Report as PDF")

# Make sure data folder exists
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(data_dir, exist_ok=True)

chart_paths = []

try:
    fig_revenue.write_image(os.path.join(data_dir, "revenue_trend.png"))
    chart_paths.append(os.path.join(data_dir, "revenue_trend.png"))

    fig_weekly.write_image(os.path.join(data_dir, "weekly_revenue.png"))
    chart_paths.append(os.path.join(data_dir, "weekly_revenue.png"))

    fig_customers.write_image(os.path.join(data_dir, "customer_breakdown.png"))
    chart_paths.append(os.path.join(data_dir, "customer_breakdown.png"))

    fig_channel.write_image(os.path.join(data_dir, "channel_sales.png"))
    chart_paths.append(os.path.join(data_dir, "channel_sales.png"))

    fig_region.write_image(os.path.join(data_dir, "region_revenue.png"))
    chart_paths.append(os.path.join(data_dir, "region_revenue.png"))
except Exception as e:
    st.error(f"Chart export failed: {e}")

# KPI summary
kpi_data = {
    "Total Revenue": f"${total_revenue:,}",
    "Total Sales": f"{total_sales:,}",
    "AOV": f"${aov}",
    "Customers": f"{total_customers:,}",
    "Conversion Rate": f"{conversion_rate}%"
}

if st.button("Generate PDF Report"):
    if chart_paths:
        pdf_path = create_pdf_report(kpi_data, chart_paths)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download PDF Report", f, file_name="business_report.pdf")
    else:
        st.warning("No charts exported — PDF will not include visuals.")

# --- Anomaly Detection ---
st.subheader("⚠️ Anomaly Highlights (Spikes/Drops in Revenue)")
df_filtered["Revenue_Change"] = df_filtered["Revenue"].pct_change() * 100
anomalies = df_filtered[(df_filtered["Revenue_Change"].abs() > 20)]
if anomalies.empty:
    st.success("No significant anomalies detected ✅")
else:
    st.warning("Significant spikes/drops detected:")
    st.dataframe(anomalies[["Date", "Revenue", "Revenue_Change"]])

# --- Data Preview ---
st.subheader("Data Preview")
st.dataframe(df_filtered.head(10))
