import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf_report(kpi_data, chart_paths):
    # Always save inside the "data" folder
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(base_dir, exist_ok=True)

    output_path = os.path.join(base_dir, "business_report.pdf")

    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Business Report")

    # KPIs
    c.setFont("Helvetica", 12)
    y = height - 100
    for key, value in kpi_data.items():
        c.drawString(50, y, f"{key}: {value}")
        y -= 20

    # Charts
    y -= 40
    for chart_path in chart_paths:
        if os.path.exists(chart_path):
            c.drawImage(chart_path, 50, y - 180, width=500, height=180)
            y -= 200
            if y < 100:  # start new page if running out of space
                c.showPage()
                y = height - 100

    c.save()
    return output_path
