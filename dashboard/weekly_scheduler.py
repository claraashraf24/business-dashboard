import os
import pandas as pd
import plotly.express as px
from data_loader import load_data
from report_generator import create_pdf_report
from email_utils import send_email_alert

# Load data
df = load_data()

# --- Aggregate weekly data ---
df["Week"] = df["Date"].dt.isocalendar().week
weekly_summary = df.groupby("Week").agg({
    "Revenue": "sum",
    "Sales": "sum",
    "Customers": "sum",
    "Visitors": "sum"
}).reset_index()

# --- KPIs ---
total_revenue = int(weekly_summary["Revenue"].sum())
total_sales = int(weekly_summary["Sales"].sum())
aov = round(total_revenue / total_sales, 2) if total_sales > 0 else 0
conversion_rate = round(weekly_summary["Sales"].sum() / weekly_summary["Visitors"].sum() * 100, 2) if weekly_summary["Visitors"].sum() > 0 else 0
total_customers = int(weekly_summary["Customers"].sum())

# --- Detect anomalies (weekly changes > 20%) ---
weekly_summary["Revenue_Change"] = weekly_summary["Revenue"].pct_change() * 100
anomalies = weekly_summary[(weekly_summary["Revenue_Change"].abs() > 20)]

# --- Export charts ---
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
os.makedirs(data_dir, exist_ok=True)

chart_paths = []

# 1. Weekly Revenue Trend
fig_weekly_rev = px.line(weekly_summary, x="Week", y="Revenue", title="Weekly Revenue Trend")
path1 = os.path.join(data_dir, "weekly_revenue_trend.png")
fig_weekly_rev.write_image(path1)
chart_paths.append(path1)

# 2. Weekly Sales
fig_weekly_sales = px.bar(weekly_summary, x="Week", y="Sales", title="Weekly Sales")
path2 = os.path.join(data_dir, "weekly_sales.png")
fig_weekly_sales.write_image(path2)
chart_paths.append(path2)

# 3. Weekly Anomaly Chart (if anomalies exist)
if not anomalies.empty:
    fig_anomaly = px.line(weekly_summary, x="Week", y="Revenue", title="Weekly Revenue with Anomalies")
    fig_anomaly.add_scatter(
        x=anomalies["Week"], y=anomalies["Revenue"],
        mode="markers", marker=dict(color="red", size=12),
        name="Anomaly"
    )
    path3 = os.path.join(data_dir, "weekly_anomalies.png")
    fig_anomaly.write_image(path3)
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
    anomaly_msg = "<p>✅ No significant weekly anomalies detected.</p>"
else:
    anomaly_msg = f"""
    <p>⚠️ Weekly anomalies detected:</p>
    {anomalies.to_html(index=False, border=1, justify="center")}
    """

body = f"""
<h2>📊 Weekly Business Summary</h2>
<p>Hello,</p>
<p>Please find attached the automated <b>weekly</b> business report.</p>
{anomaly_msg}
<p style='color:gray;'>This is an automated email from your Business Dashboard.</p>
"""

# --- Send email ---
subject = "📊 Weekly Business Report with Anomaly Alerts"
success = send_email_alert(subject, body, "clarayoussef01@gmail.com", attachment_path=pdf_path, html=True)

if success:
    print("✅ Weekly report sent successfully!")
else:
    print("❌ Failed to send weekly report")
