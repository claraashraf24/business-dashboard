<<<<<<< HEAD
# 📊 Business Dashboard

An automated **Business Analytics Dashboard** built with **Streamlit** and **Python**.  
It connects to **Google Sheets** for live data, generates **interactive visualizations**, creates **PDF reports**, and sends **email alerts** when anomalies are detected.

This project is designed as a **portfolio-ready app** for showcasing data automation, visualization, and reporting skills.

---

## 🚀 Features

✅ **Google Sheets Integration** – load business data directly from Sheets  
✅ **KPIs Dashboard** – Revenue, Sales, AOV, Customers, Conversion Rate  
✅ **Forecasting** – Future trend predictions using Prophet  
✅ **Customer Insights** – breakdown of new vs returning customers  
✅ **Marketing & Regional Analysis** – see sales across channels and regions  
✅ **Automated Reports** – generate exportable **PDF reports** with KPIs & charts  
✅ **Anomaly Detection** – alerts for spikes/drops in revenue (>20%)  
✅ **Email Alerts** – send anomaly reports with **inline charts + PDF attachment**  
✅ **Secure Login** – simple authentication for dashboard access

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** – interactive dashboard UI
- **Pandas** – data wrangling
- **Plotly Express** – charts & visualizations
- **Prophet** – forecasting
- **ReportLab** – PDF generation
- **Google Sheets API** – live data source
- **SMTP (Gmail)** – email alerts
- **Kaleido** – chart image export

---

## 📂 Project Structure

```
business-dashboard/
│
├── dashboard/
│   ├── app.py                 # Main Streamlit app
│   ├── auth.py                # Login system
│   ├── data_loader.py         # Google Sheets data loader
│   ├── email_utils.py         # Email sending logic
│   ├── report_generator.py    # PDF report builder
│   ├── scheduler.py           # Automation (daily/weekly/monthly jobs)
│   ├── master_scheduler.py    # Unified job runner
│   └── ...
│
├── data/                      # Generated charts & reports
├── google_credentials.json    # GCP service account (excluded in .gitignore)
├── requirements.txt           # Dependencies
└── README.md
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone Repo

```bash
git clone https://github.com/YOUR_USERNAME/business-dashboard.git
cd business-dashboard
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Google Sheets Setup

- Create a **Google Cloud Project**
- Enable **Google Sheets API**
- Create a **Service Account** and download JSON key
- Share your Google Sheet with the service account email
- Save JSON file as:

```
google_credentials.json
```

### 5️⃣ Run Streamlit App

```bash
streamlit run dashboard/app.py
```

---

## 📧 Email Alerts

The app uses **Gmail SMTP** for sending alerts.  
Create an **App Password** in your Gmail account and update `email_utils.py`.

---

## 📊 Example Screenshots

_Add screenshots or GIFs here after running your app locally._

---

## 🗓 Automation

Reports can be automated:

- **Daily** – sends standard report
- **Weekly** – weekly summary
- **Monthly** – full report

Controlled via `scheduler.py` and `master_scheduler.py`.

---

## 🔐 Security

- Secrets like `google_credentials.json` and Gmail password are **ignored** via `.gitignore`
- Simple login system in `auth.py` protects the dashboard

---

## 🌟 Portfolio Value

This project demonstrates:

- **End-to-End Automation** (data → visualization → reporting → alerts)
- **Full-Stack Data Workflow** using Google APIs + Python
- **Practical Business Application** (KPI monitoring & anomaly detection)

---

## 📝 License

This project is open source and available under the MIT License.
=======
# 📊 Business Dashboard

An automated **Business Analytics Dashboard** built with **Streamlit** and **Python**.  
It connects to **Google Sheets** for live data, generates **interactive visualizations**, creates **PDF reports**, and sends **email alerts** when anomalies are detected.  

This project is designed as a **portfolio-ready app** for showcasing data automation, visualization, and reporting skills.

---

## 🚀 Features

✅ **Google Sheets Integration** – load business data directly from Sheets  
✅ **KPIs Dashboard** – Revenue, Sales, AOV, Customers, Conversion Rate  
✅ **Forecasting** – Future trend predictions using [Prophet](https://facebook.github.io/prophet/)  
✅ **Customer Insights** – breakdown of new vs returning customers  
✅ **Marketing & Regional Analysis** – see sales across channels and regions  
✅ **Automated Reports** – generate exportable **PDF reports** with KPIs & charts  
✅ **Anomaly Detection** – alerts for spikes/drops in revenue (>20%)  
✅ **Email Alerts** – send anomaly reports with **inline charts + PDF attachment**  
✅ **Secure Login** – simple authentication for dashboard access  

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** – interactive dashboard UI
- **Pandas** – data wrangling
- **Plotly Express** – charts & visualizations
- **Prophet** – forecasting
- **ReportLab** – PDF generation
- **Google Sheets API** – live data source
- **SMTP (Gmail)** – email alerts
- **Kaleido** – chart image export

---

## 📂 Project Structure

business-dashboard/
│
├── dashboard/
│ ├── app.py # Main Streamlit app
│ ├── auth.py # Login system
│ ├── data_loader.py # Google Sheets data loader
│ ├── email_utils.py # Email sending logic
│ ├── report_generator.py # PDF report builder
│ ├── scheduler.py # Automation (daily/weekly/monthly jobs)
│ ├── master_scheduler.py # Unified job runner
│ └── ...
│
├── data/ # Generated charts & reports
├── google_credentials.json # GCP service account (excluded in .gitignore)
├── requirements.txt # Dependencies
└── README.md

yaml
Copy code

---

## ⚙️ Setup & Installation

### 1️⃣ Clone Repo
```bash
git clone https://github.com/YOUR_USERNAME/business-dashboard.git
cd business-dashboard
2️⃣ Create Virtual Environment
bash
Copy code
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Google Sheets Setup
Create a Google Cloud Project

Enable Google Sheets API

Create a Service Account and download JSON key

Share your Google Sheet with the service account email

Save JSON file as:

pgsql
Copy code
google_credentials.json
5️⃣ Run Streamlit App
bash
Copy code
streamlit run dashboard/app.py
📧 Email Alerts
The app uses Gmail SMTP for sending alerts.
Create an App Password in your Gmail account and update email_utils.py.

📊 Example Screenshots
Add screenshots or GIFs here after running your app locally.

🗓 Automation
Reports can be automated:

Daily – sends standard report

Weekly – weekly summary

Monthly – full report

Controlled via scheduler.py and master_scheduler.py.

🔐 Security
Secrets like google_credentials.json and Gmail password are ignored via .gitignore

Simple login system in auth.py protects the dashboard

🌟 Portfolio Value
This project demonstrates:

End-to-End Automation (data → visualization → reporting → alerts)

Full-Stack Data Workflow using Google APIs + Python

Practical Business Application (KPI monitoring & anomaly detection)

📝 License
This project is open source and available under the MIT License.
>>>>>>> c15840c25f236d8f50bb9fabf7ae402fe948788d
