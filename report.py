from fpdf import FPDF
from extract import CompanyProfile


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Company Research Report", ln=True, align="C")
        self.ln(4)
    
def _section(pdf: FPDF, title: str, body: str | list[str]):
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, title, ln=True)
    pdf.set_font("Helvetica", "", 10)
    if isinstance(body, list):
        body = "\n".join(f"- {b}" for b in body) if body else "N/A"
    pdf.multi_cell(0, 6, body or "N/A")
    pdf.ln(3)
    
def build_pdf(profile: CompanyProfile, out_path: str):
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, profile.name, ln=True)
    pdf.ln(2)
    
    _section(pdf, "Summary", profile.summary or "N/A")
    _section(pdf, "Industry", profile.industry or "N/A")
    _section(pdf, "Headquarters", profile.hq_location or "N/A")
    _section(pdf, "Founded", str(profile.founded_year) if profile.founded_year else "N/A")
    _section(pdf, "Employees (est.)", profile.employee_count_estimate or "N/A")
    _section(pdf, "Products / Services", profile.products_services)
    _section(pdf, "Key People", profile.key_people)
    _section(pdf, "Funding", profile.funding_summary or "N/A")
    _section(pdf, "Recent News", profile.recent_news)
    _section(pdf, "Competitors", profile.competitors)
    
    pdf.output(out_path)