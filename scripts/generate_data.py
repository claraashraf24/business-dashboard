import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Make sure data folder exists
os.makedirs("../data", exist_ok=True)

# Configuration
num_days = 60
start_date = datetime(2025, 7, 1)

products = ["Product A", "Product B", "Product C"]
regions = ["Canada", "USA", "UK", "Germany", "Egypt"]
channels = ["Google Ads", "Instagram", "Organic Search", "Facebook Ads", "Email"]

# Generate data
dates = [start_date + timedelta(days=i) for i in range(num_days)]
rows = []

for date in dates:
    visitors = np.random.randint(800, 2000)
    sales = np.random.randint(50, 150)
    revenue = sales * np.random.randint(40, 80)  # avg order value
    product = random.choice(products)
    region = random.choice(regions)
    channel = random.choice(channels)
    customers = sales - np.random.randint(0, 10)  # some sales may be multiple items
    new_customers = int(customers * random.uniform(0.4, 0.7))
    returning_customers = customers - new_customers

    rows.append([
        date.strftime("%Y-%m-%d"),
        visitors,
        sales,
        revenue,
        product,
        region,
        channel,
        customers,
        new_customers,
        returning_customers
    ])

# Create DataFrame
df = pd.DataFrame(rows, columns=[
    "Date",
    "Visitors",
    "Sales",
    "Revenue",
    "Product",
    "Region",
    "Marketing_Channel",
    "Customers",
    "New_Customers",
    "Returning_Customers"
])

# Save Excel file
output_path = "../data/business_data.xlsx"
df.to_excel(output_path, index=False)

print(f"✅ Dataset generated and saved to {output_path}")
