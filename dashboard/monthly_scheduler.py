import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta

from data_loader import load_data
from report_generator import create_pdf_report
from email_utils import send_email_alert

# --- Load data ---
df = load_data()

# --- Get last full month ---
today = datetime.today()
first_day_this_month = today.replace(day=1)
last_month_end = first_day_this_month - pd.Timedelta(days=1)
last_month_start = last_month_end.replace(day=1)

df_month = df[(df["Date"] >= last_month_start) & (df["Date"] <= last_month_end)]

# --- KPIs ---
total_revenue = int(df_month["Revenue"].sum())
total_sales = int(df_month["Sales"].sum())
aov = round(total_revenue / total_sales, 2) if total_sales > 0 else 0
conversion_rate = round(
    df_month["Sales"].sum() / df_month["Visitors"].sum() * 100, 2
) if df_month["Visitors"].sum() > 0 else 0
total_customers = int(df_month["Customers"].sum())

# --- Export charts ---
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
os.makedirs(data_dir, exist_ok=True)
chart_paths = []

# 1. Revenue Trend (last month only)
revenue_trend = df_month.groupby("Date")["Revenue"].sum().reset_index()
fig_revenue = px.line(revenue_trend, x="Date", y="Revenue", title="Revenue Trend (Monthly)")
path1 = os.path.join(data_dir, "monthly_revenue_trend.png")
fig_revenue.write_image(path1)
chart_paths.append(path1)

# 2. Marketing Channel Breakdown
channel_sales = df_month.groupby("Marketing_Channel")["Sales"].sum().reset_index()
fig_channel = px.bar(channel_sales, x="Marketing_Channel", y="Sales", title="Sales by Channel (Monthly)")
path2 = os.path.join(data_dir, "monthly_channel_sales.png")
fig_channel.write_image(path2)
chart_paths.append(path2)

# 3. Region Breakdown
region_revenue = df_month.groupby("Region")["Revenue"].sum().reset_index()
fig_region = px.bar(region_revenue, x="Region", y="Revenue", title="Revenue by Region (Monthly)")
path3 = os.path.join(data_dir, "monthly_region_revenue.png")
fig_region.write_image(path3)
chart_paths.append(path3)

# --- Generate PDF ---
pdf_path = create_pdf_report(
    {
        "Period": f"{last_month_start.strftime('%B %Y')}",
        "Total Revenue": f"${total_revenue:,}",
        "Total Sales": f"{total_sales:,}",
        "AOV": f"${aov}",
        "Customers": f"{total_customers:,}",
        "Conversion Rate": f"{conversion_rate}%"
    },
    chart_paths
)

# --- Send email ---
subject = f"📊 Monthly Business Summary - {last_month_start.strftime('%B %Y')}"
body = f"""
<h2>📊 Monthly Business Summary</h2>
<p>Here’s your business performance for <b>{last_month_start.strftime('%B %Y')}</b>.</p>
<p>See attached PDF for full details and charts.</p>
<p style='color:gray;'>This is an automated monthly report.</p>
"""

success = send_email_alert(
    subject,
    body,
    "clarayoussef01@gmail.com",
    attachment_path=pdf_path,
    html=True
)

if success:
    print("✅ Monthly report sent successfully!")
else:
    print("❌ Failed to send monthly report")
