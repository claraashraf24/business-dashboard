import streamlit as st
import pandas as pd
import os
import plotly.express as px
from report_generator import create_pdf_report
import kaleido  # ensure kaleido engine is registered
from email_utils import send_email_alert
import base64
from auth import login

if not login():
    st.stop()
# Reuse our data loader
from data_loader import load_data



# Load data
df = load_data()

# --- Dashboard Layout ---
st.set_page_config(page_title="Business Dashboard", layout="wide")

# 🔄 Auto-refresh every 5 minutes (300,000 ms)
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

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

# NEW: Marketing Channel filter
if "Marketing_Channel" in df.columns:
    selected_channel = st.sidebar.multiselect(
        "Select Marketing Channel:",
        options=df["Marketing_Channel"].unique(),
        default=df["Marketing_Channel"].unique()
    )
else:
    selected_channel = df["Marketing_Channel"].unique() if "Marketing_Channel" in df.columns else []

# NEW: Customer Type filter
customer_type = st.sidebar.radio(
    "Select Customer Type:",
    ["All", "New_Customers", "Returning_Customers"]
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

# --- Apply filters ---
df_filtered = df[
    (df["Region"].isin(selected_region)) &
    (df["Product"].isin(selected_product))
]

if len(selected_channel) > 0 and "Marketing_Channel" in df.columns:
    df_filtered = df_filtered[df_filtered["Marketing_Channel"].isin(selected_channel)]

if customer_type == "New_Customers":
    df_filtered = df_filtered[df_filtered["New_Customers"] > 0]
elif customer_type == "Returning_Customers":
    df_filtered = df_filtered[df_filtered["Returning_Customers"] > 0]

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

# =========================
#       TAB LAYOUT
# =========================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📌 KPIs", "📈 Trends", "👥 Customers", "📊 Marketing & Regions", "📄 Reports", "⚠️ Anomalies"]
)
# --- TAB 1: KPIs ---
with tab1:
    st.subheader("Key Performance Indicators")

    total_revenue = int(df_filtered["Revenue"].sum())
    total_sales = int(df_filtered["Sales"].sum())
    aov = round(total_revenue / total_sales, 2) if total_sales > 0 else 0
    conversion_rate = round(
        df_filtered["Sales"].sum() / df_filtered["Visitors"].sum() * 100, 2
    ) if df_filtered["Visitors"].sum() > 0 else 0

    # ✅ Adjusted Customers KPI
    if customer_type == "New_Customers":
        total_customers = int(df_filtered["New_Customers"].sum())
    elif customer_type == "Returning_Customers":
        total_customers = int(df_filtered["Returning_Customers"].sum())
    else:
        total_customers = int(df_filtered["Customers"].sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue", f"${total_revenue:,}")
    col2.metric("🛒 Total Sales", f"{total_sales:,}")
    col3.metric("📊 AOV", f"${aov}")
    col4.metric("👥 Customers", f"{total_customers:,}")
    st.metric("⚡ Conversion Rate", f"{conversion_rate}%")


# --- TAB 2: Trends ---
with tab2:
    st.subheader("📈 Forecast Trends")

    # Granularity selection
    granularity = st.radio(
        "Select Date Granularity:",
        ["Daily", "Weekly", "Monthly"],
        horizontal=True
    )

    df_trend = df_filtered.copy()

    if granularity == "Weekly":
        df_trend = df_trend.groupby(df_trend["Date"].dt.isocalendar().week).agg(
            {"Revenue": "sum", "Sales": "sum", "Customers": "sum"}
        ).reset_index()
        df_trend.rename(columns={"week": "Period"}, inplace=True)
        df_trend["ds"] = pd.to_datetime(
            df_filtered["Date"].dt.to_period("W").dt.start_time.unique()
        )
    elif granularity == "Monthly":
        df_trend = df_trend.groupby(df_trend["Date"].dt.to_period("M")).agg(
            {"Revenue": "sum", "Sales": "sum", "Customers": "sum"}
        ).reset_index()
        df_trend.rename(columns={"Date": "Period"}, inplace=True)
        df_trend["Period"] = df_trend["Period"].astype(str)
        df_trend["ds"] = pd.to_datetime(df_trend["Period"])
    else:  # Daily
        df_trend["Period"] = df_trend["Date"]
        df_trend["ds"] = df_trend["Date"]

    # Helper function to build forecast charts
    def forecast_and_plot(df, target_col, title):
        from prophet import Prophet
        temp_df = df[["ds", target_col]].rename(columns={target_col: "y"}).dropna()
        if temp_df.empty:
            st.warning(f"No data available for {target_col}")
            return None

        model = Prophet()
        model.fit(temp_df)
        future = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)

        fig = px.line(forecast, x="ds", y="yhat", title=title)
        fig.add_scatter(
            x=temp_df["ds"], y=temp_df["y"],
            mode="lines+markers", name="Actual"
        )
        fig.add_scatter(
            x=forecast["ds"], y=forecast["yhat_upper"],
            mode="lines", line=dict(dash="dot"), name="Upper Bound"
        )
        fig.add_scatter(
            x=forecast["ds"], y=forecast["yhat_lower"],
            mode="lines", line=dict(dash="dot"), name="Lower Bound"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Forecast charts
    forecast_and_plot(df_trend, "Revenue", f"Revenue Forecast ({granularity})")
    forecast_and_plot(df_trend, "Sales", f"Sales Forecast ({granularity})")
    forecast_and_plot(df_trend, "Customers", f"Customers Forecast ({granularity})")

    # --- Weekly Revenue Comparison ---
    st.subheader("Weekly Revenue Comparison")
    df_filtered["Week"] = df_filtered["Date"].dt.isocalendar().week
    weekly_revenue = df_filtered.groupby("Week")["Revenue"].sum().reset_index()
    fig_weekly = px.bar(
        weekly_revenue, x="Week", y="Revenue",
        title="Weekly Revenue", text_auto=True
    )
    st.plotly_chart(fig_weekly, use_container_width=True)



# --- TAB 3: Customers ---
with tab3:
    st.subheader("Customer Breakdown (New vs Returning)")

    if customer_type == "All":
        # Show both curves
        fig_customers = px.area(
            df_filtered, x="Date", y=["New_Customers", "Returning_Customers"],
            title="New vs Returning Customers Over Time"
        )
    elif customer_type == "New_Customers":
        # Show only new customers
        fig_customers = px.area(
            df_filtered, x="Date", y="New_Customers",
            title="New Customers Over Time"
        )
    else:  # Returning_Customers
        fig_customers = px.area(
            df_filtered, x="Date", y="Returning_Customers",
            title="Returning Customers Over Time"
        )

    st.plotly_chart(fig_customers, use_container_width=True)


# --- TAB 4: Marketing & Regions ---
with tab4:
    st.subheader("Sales by Marketing Channel")
    channel_sales = df_filtered.groupby("Marketing_Channel")["Sales"].sum().reset_index()
    fig_channel = px.bar(channel_sales, x="Marketing_Channel", y="Sales", title="Sales by Channel", text_auto=True)
    st.plotly_chart(fig_channel, use_container_width=True)

    st.subheader("Revenue by Region")
    region_revenue = df_filtered.groupby("Region")["Revenue"].sum().reset_index()
    fig_region = px.bar(region_revenue, x="Region", y="Revenue", title="Revenue by Region", text_auto=True)
    st.plotly_chart(fig_region, use_container_width=True)

# --- TAB 5: Reports ---
with tab5:
    st.subheader("📄 Export Report as PDF")

    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)

    chart_paths = []

    try:
        # 1. Revenue Trend (Daily)
        trend_export = df_filtered.groupby("Date")["Revenue"].sum().reset_index()
        fig_revenue_export = px.line(trend_export, x="Date", y="Revenue", title="Revenue Trend")
        fig_revenue_export.write_image(os.path.join(data_dir, "revenue_trend.png"))
        chart_paths.append(os.path.join(data_dir, "revenue_trend.png"))

        # 2. Weekly Revenue
        weekly_export = df_filtered.copy()
        weekly_export["Week"] = weekly_export["Date"].dt.isocalendar().week
        weekly_revenue_export = weekly_export.groupby("Week")["Revenue"].sum().reset_index()
        fig_weekly_export = px.bar(weekly_revenue_export, x="Week", y="Revenue", title="Weekly Revenue")
        fig_weekly_export.write_image(os.path.join(data_dir, "weekly_revenue.png"))
        chart_paths.append(os.path.join(data_dir, "weekly_revenue.png"))

        # 3. Customers Breakdown
        fig_customers_export = px.area(
            df_filtered, x="Date", y=["New_Customers", "Returning_Customers"],
            title="New vs Returning Customers Over Time"
        )
        fig_customers_export.write_image(os.path.join(data_dir, "customer_breakdown.png"))
        chart_paths.append(os.path.join(data_dir, "customer_breakdown.png"))

        # 4. Marketing Channels
        channel_sales_export = df_filtered.groupby("Marketing_Channel")["Sales"].sum().reset_index()
        fig_channel_export = px.bar(channel_sales_export, x="Marketing_Channel", y="Sales", title="Sales by Channel")
        fig_channel_export.write_image(os.path.join(data_dir, "channel_sales.png"))
        chart_paths.append(os.path.join(data_dir, "channel_sales.png"))

        # 5. Regions
        region_revenue_export = df_filtered.groupby("Region")["Revenue"].sum().reset_index()
        fig_region_export = px.bar(region_revenue_export, x="Region", y="Revenue", title="Revenue by Region")
        fig_region_export.write_image(os.path.join(data_dir, "region_revenue.png"))
        chart_paths.append(os.path.join(data_dir, "region_revenue.png"))

    except Exception as e:
        st.error(f"Chart export failed: {e}")

    # KPI Summary for PDF
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


# --- TAB 6: Anomaly Detection ---
with tab6:
    st.subheader("⚠️ Anomaly Highlights (Spikes/Drops in Revenue)")

    df_filtered["Revenue_Change"] = df_filtered["Revenue"].pct_change() * 100
    anomalies = df_filtered[(df_filtered["Revenue_Change"].abs() > 20)]

    if anomalies.empty:
        st.success("No significant anomalies detected ✅")
    else:
        st.warning("Significant spikes/drops detected:")
        st.dataframe(anomalies[["Date", "Revenue", "Revenue_Change"]])

        # Plot anomalies
        fig_anomaly = px.line(df_filtered, x="Date", y="Revenue", title="Revenue with Anomalies")
        fig_anomaly.add_scatter(
            x=anomalies["Date"], y=anomalies["Revenue"],
            mode="markers", marker=dict(color="red", size=10),
            name="Anomaly"
        )
        st.plotly_chart(fig_anomaly, use_container_width=True)

if st.button("📧 Send Anomaly Alert Email"):
    subject = "⚠️ Business Dashboard Alert: Revenue Anomaly Detected"

    # Convert anomalies DataFrame to HTML
    anomalies_html = anomalies.to_html(index=False, border=1, justify="center")

    body = f"""
    <h2>⚠️ Business Dashboard Alert</h2>
    <p>The system detected anomalies in revenue data. Details below:</p>
    {anomalies_html}
    <p style='color:gray;'>This is an automated alert from your Business Dashboard.</p>
    """

    # --- Generate charts to attach in PDF ---
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    chart_paths = []

    try:
        # 1. Revenue Trend
        trend_export = df_filtered.groupby("Date")["Revenue"].sum().reset_index()
        fig_revenue_export = px.line(trend_export, x="Date", y="Revenue", title="Revenue Trend")
        path1 = os.path.join(data_dir, "revenue_trend.png")
        fig_revenue_export.write_image(path1)
        chart_paths.append(path1)

        # 2. Weekly Revenue
        weekly_export = df_filtered.copy()
        weekly_export["Week"] = weekly_export["Date"].dt.isocalendar().week
        weekly_revenue_export = weekly_export.groupby("Week")["Revenue"].sum().reset_index()
        fig_weekly_export = px.bar(weekly_revenue_export, x="Week", y="Revenue", title="Weekly Revenue")
        path2 = os.path.join(data_dir, "weekly_revenue.png")
        fig_weekly_export.write_image(path2)
        chart_paths.append(path2)

        # 3. Customers Breakdown
        fig_customers_export = px.area(
            df_filtered, x="Date", y=["New_Customers", "Returning_Customers"],
            title="New vs Returning Customers Over Time"
        )
        path3 = os.path.join(data_dir, "customer_breakdown.png")
        fig_customers_export.write_image(path3)
        chart_paths.append(path3)

        # 4. Marketing Channels
        channel_sales_export = df_filtered.groupby("Marketing_Channel")["Sales"].sum().reset_index()
        fig_channel_export = px.bar(channel_sales_export, x="Marketing_Channel", y="Sales", title="Sales by Channel")
        path4 = os.path.join(data_dir, "channel_sales.png")
        fig_channel_export.write_image(path4)
        chart_paths.append(path4)

        # 5. Regions
        region_revenue_export = df_filtered.groupby("Region")["Revenue"].sum().reset_index()
        fig_region_export = px.bar(region_revenue_export, x="Region", y="Revenue", title="Revenue by Region")
        path5 = os.path.join(data_dir, "region_revenue.png")
        fig_region_export.write_image(path5)
        chart_paths.append(path5)
        
        # 6. Anomaly Chart
        fig_anomaly_export = px.line(df_filtered, x="Date", y="Revenue", title="Revenue with Anomalies")
        fig_anomaly_export.add_scatter(
            x=anomalies["Date"], y=anomalies["Revenue"],
            mode="markers", marker=dict(color="red", size=10),
            name="Anomaly"
        )
        path6 = os.path.join(data_dir, "anomaly_chart.png")
        fig_anomaly_export.write_image(path6)
        chart_paths.append(path6)
        
        # Encode anomaly chart as Base64 to embed in email
        with open(path6, "rb") as f:
            anomaly_img_base64 = base64.b64encode(f.read()).decode("utf-8")

        # Update email body with inline chart preview
        body = f"""
        <h2>⚠️ Business Dashboard Alert</h2>
        <p>The system detected anomalies in revenue data. Details below:</p>
        {anomalies_html}
        <p><b>Preview of anomalies chart:</b></p>
        <img src="data:image/png;base64,{anomaly_img_base64}" alt="Anomaly Chart" style="max-width:600px; border:1px solid #ccc;" />
        <p style='color:gray;'>This is an automated alert from your Business Dashboard.</p>
        """

    except Exception as e:
        st.error(f"Chart export failed: {e}")

    # --- Generate PDF with KPIs + charts ---
    pdf_path = create_pdf_report(
        {
            "Total Revenue": f"${total_revenue:,}",
            "Total Sales": f"{total_sales:,}",
            "AOV": f"${aov}",
            "Customers": f"{total_customers:,}",
            "Conversion Rate": f"{conversion_rate}%"
        },
        chart_paths
    )

    success = send_email_alert(
        subject,
        body,
        "clarayoussef01@gmail.com",
        attachment_path=pdf_path,
        html=True
    )

    if success:
        st.success("✅ Alert email sent successfully with HTML table + PDF + charts!")
    else:
        st.error("❌ Failed to send email alert")


