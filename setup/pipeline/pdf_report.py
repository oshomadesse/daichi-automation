import os
from datetime import date

from fpdf import FPDF

import config


class EstimatePDF(FPDF):
    def __init__(self):
        super().__init__()
        if os.path.exists(config.FONT_PATH):
            self.add_font("NotoSansJP", "", config.FONT_PATH, uni=True)
            self.font_name = "NotoSansJP"
        else:
            self.font_name = "Helvetica"

    def header(self):
        self.set_font(self.font_name, "", 18)
        self.cell(0, 15, "お見積書", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font(self.font_name, "", 10)
        self.cell(0, 8, f"作成日: {date.today().isoformat()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_name, "", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def generate_pdf(estimates: list[dict], output_path: str) -> str:
    pdf = EstimatePDF()
    pdf.alias_nb_pages()

    for i, est in enumerate(estimates):
        pdf.add_page()

        # Proposal title
        pdf.set_font(pdf.font_name, "", 14)
        pdf.cell(0, 12, f"企画案{i + 1}: {est['title']}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # Table header
        pdf.set_font(pdf.font_name, "", 10)
        pdf.set_fill_color(230, 230, 230)
        col_widths = [60, 30, 20, 20, 40]
        headers = ["項目", "単価", "数量", "単位", "小計"]
        for w, h in zip(col_widths, headers):
            pdf.cell(w, 8, h, border=1, fill=True, align="C")
        pdf.ln()

        # Table rows
        for item in est["items"]:
            pdf.cell(col_widths[0], 8, item["item"], border=1)
            pdf.cell(col_widths[1], 8, f"¥{item['unit_price']:,}", border=1, align="R")
            pdf.cell(col_widths[2], 8, str(item["quantity"]), border=1, align="C")
            pdf.cell(col_widths[3], 8, item["unit"], border=1, align="C")
            pdf.cell(col_widths[4], 8, f"¥{item['subtotal']:,}", border=1, align="R")
            pdf.ln()

        # Total
        pdf.ln(3)
        pdf.set_font(pdf.font_name, "", 12)
        pdf.cell(0, 10, f"合計: ¥{est['total']:,}（税別）", align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.output(output_path)
    return output_path
