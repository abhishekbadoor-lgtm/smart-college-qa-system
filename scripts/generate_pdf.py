import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Smart College QA - Test Cases Documentation', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def convert_md_to_pdf(md_file, pdf_file):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found.")
        return

    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue
        
        # Simple Markdown parsing
        if line.startswith('# '):
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, line[2:], 0, 1)
            pdf.set_font("Arial", size=10)
        elif line.startswith('## '):
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, line[3:], 0, 1)
            pdf.set_font("Arial", size=10)
        elif line.startswith('|'):
            # Basic table handling (ignore separator line)
            if '---' in line:
                continue
            cols = [c.strip() for c in line.split('|') if c.strip()]
            if not cols: continue
            
            # Simple column widths
            col_widths = [20, 30, 70, 70]
            
            # Check if this is the header row
            if 'Test Case ID' in line:
                pdf.set_font("Arial", 'B', 9)
            else:
                pdf.set_font("Arial", size=9)
            
            # Use multi_cell for wrapping text in descriptions and results
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            max_y = y_start

            for i, text in enumerate(cols):
                width = col_widths[i] if i < len(col_widths) else 30
                pdf.multi_cell(width, 7, text, border=1)
                curr_y = pdf.get_y()
                if curr_y > max_y: max_y = curr_y
                pdf.set_xy(x_start + width, y_start)
                x_start += width
            
            pdf.set_xy(10, max_y)
        else:
            pdf.multi_cell(0, 7, line)

    pdf.output(pdf_file)
    print(f"Successfully generated {pdf_file}")

if __name__ == "__main__":
    base_dir = r"c:\W\MCA\Backupp project\SMART COLLEGE QA"
    
    # 1. Generate Test Cases PDF
    md_path_tc = os.path.join(base_dir, "docs", "test_cases.md")
    pdf_path_tc = os.path.join(base_dir, "docs", "test_cases.pdf")
    os.makedirs(os.path.dirname(pdf_path_tc), exist_ok=True)
    convert_md_to_pdf(md_path_tc, pdf_path_tc)

    # 2. Generate Database Schema PDF
    md_path_db = os.path.join(base_dir, "docs", "database_schema.md")
    pdf_path_db = os.path.join(base_dir, "docs", "database_schema.pdf")
    convert_md_to_pdf(md_path_db, pdf_path_db)
