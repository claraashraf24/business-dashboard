import os
import pandas as pd
import plotly.express as px
from data_loader import load_data
from report_generator import create_pdf_report
from email_utils import send_email_alert

# Load data
df = load_data()

# --- KPIs ---
total_revenue = int(df["Revenue"].sum())
total_sales = int(df["Sales"].sum())
aov = round(total_revenue / total_sales, 2) if total_sales > 0 else 0
conversion_rate = round(df["Sales"].sum() / df["Visitors"].sum() * 100, 2) if df["Visitors"].sum() > 0 else 0
total_customers = int(df["Customers"].sum())

# --- Detect anomalies ---
df["Revenue_Change"] = df["Revenue"].pct_change() * 100
anomalies = df[(df["Revenue_Change"].abs() > 20)]  # flag ±20% changes

# --- Export charts ---
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
os.makedirs(data_dir, exist_ok=True)

chart_paths = []

# 1. Revenue Trend
trend_export = df.groupby("Date")["Revenue"].sum().reset_index()
fig_revenue_export = px.line(trend_export, x="Date", y="Revenue", title="Revenue Trend")
path1 = os.path.join(data_dir, "revenue_trend.png")
fig_revenue_export.write_image(path1)
chart_paths.append(path1)

# 2. Customers Breakdown
fig_customers_export = px.area(df, x="Date", y=["New_Customers", "Returning_Customers"], title="Customers Over Time")
path2 = os.path.join(data_dir, "customer_breakdown.png")
fig_customers_export.write_image(path2)
chart_paths.append(path2)

# 3. Anomalies Chart (if any)
if not anomalies.empty:
    fig_anomaly_export = px.line(df, x="Date", y="Revenue", title="Revenue with Anomalies")
    fig_anomaly_export.add_scatter(
        x=anomalies["Date"], y=anomalies["Revenue"],
        mode="markers", marker=dict(color="red", size=10),
        name="Anomaly"
    )
    path3 = os.path.join(data_dir, "anomaly_chart.png")
    fig_anomaly_export.write_image(path3)
    chart_paths.append(path3)

# --- Generate PDF ---
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

# --- Build email body ---
if anomalies.empty:
    anomaly_msg = "<p>✅ No significant anomalies detected in revenue.</p>"
else:
    anomaly_msg = f"""
    <p>⚠️ Anomalies detected in revenue:</p>
    {anomalies.to_html(index=False, border=1, justify="center")}
    """

body = f"""
<h2>📊 Daily Business Report</h2>
<p>Hello,</p>
<p>Please find attached the automated daily business report.</p>
{anomaly_msg}
<p style='color:gray;'>This is an automated email from your Business Dashboard.</p>
"""

# --- Send email ---
subject = "📊 Daily Business Report with Anomaly Alerts"
success = send_email_alert(subject, body, "clarayoussef01@gmail.com", attachment_path=pdf_path, html=True)

if success:
    print("✅ Report with anomalies sent successfully!")
else:
    print("❌ Failed to send report")
