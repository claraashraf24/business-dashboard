import pandas as pd
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Your Google Sheet ID
SHEET_ID = "1Odr83oHcGiHdQzZVuefovB2rUQsgSDOjo6FMHGEq55c"
RANGE_NAME = "Sheet1"  # change if your sheet tab is named differently

def load_data():
    # ✅ Use the correct path to your credentials file
    creds_path = r"H:\upwork\business-dashboard\google_credentials.json"

    # Authenticate
    creds = service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    # Connect to Google Sheets API
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    # Read values from the sheet
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    values = result.get("values", [])

    if not values:
        raise ValueError("❌ No data found in the Google Sheet!")

    # Convert to DataFrame (first row is header)
    df = pd.DataFrame(values[1:], columns=values[0])

    # Ensure correct datatypes
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    numeric_cols = ["Visitors", "Sales", "Revenue", "Customers", "New_Customers", "Returning_Customers"]
    for col in numeric_cols:
        if col in df.columns:  # prevent crash if missing
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

if __name__ == "__main__":
    data = load_data()
    print(data.head())  # preview first rows
