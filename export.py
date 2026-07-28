"""Экспорт сметы в PDF через fpdf2."""

import os
from fpdf import FPDF

from models import Calculation, ROLES


class CalcPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        font_dir = os.path.dirname(os.path.abspath(__file__))
        self.add_font("DejaVu", "", os.path.join(font_dir, "DejaVuSans.ttf"), uni=True)
        self.add_font("DejaVu", "B", os.path.join(font_dir, "DejaVuSans-Bold.ttf"), uni=True)
        self.add_page()
        self.set_auto_page_break(auto=False)


def _rub(value) -> str:
    return f"{value:,.2f} руб.".replace(",", " ")


def export_calculation_to_pdf(calc: Calculation, filepath: str) -> str:
    pdf = CalcPDF()

    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "РАСЧЕТ СТОИМОСТИ ВЫЕЗДНЫХ РАБОТ", align="C")
    pdf.ln(10)

    pdf.set_font("DejaVu", "", 11)
    title_text = calc.work_type if calc.work_type else "поверка, калибровка, испытания"
    pdf.cell(0, 6, f"({title_text})", align="C")
    pdf.ln(10)

    pdf.set_font("DejaVu", "", 9)
    pdf.cell(0, 5, f"Дата: {calc.formatted_date()}", align="R")
    pdf.ln(5)
    pdf.cell(0, 5, f"Сотрудник: {calc.role}", align="R")
    pdf.ln(5)
    if calc.customer:
        pdf.cell(0, 5, f"Заказчик: {calc.customer}", align="R")
        pdf.ln(5)
    if calc.work_location:
        pdf.cell(0, 5, f"Место проведения: {calc.work_location}", align="R")
        pdf.ln(5)
    if calc.contract_number:
        pdf.cell(0, 5, f"Номер КП (договора): {calc.contract_number}", align="R")
        pdf.ln(5)
    if calc.instrument_name:
        pdf.cell(0, 5, f"СИ: {calc.instrument_name}", align="R")
        pdf.ln(5)
    pdf.ln(5)

    col_w = [75, 35, 35, 40]
    headers = ["Наименование", "Параметр", "Стоимость", "Сумма"]

    pdf.set_font("DejaVu", "B", 10)
    pdf.set_fill_color(0x1A, 0x47, 0x8A)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(0, 0, 0)

    def row(name, param, price, total, bold=False):
        if bold:
            pdf.set_font("DejaVu", "B", 10)
            pdf.set_fill_color(0xE8, 0xEE, 0xF7)
        else:
            pdf.set_font("DejaVu", "", 10)
        pdf.cell(col_w[0], 8, name, border=1, fill=bold, align="L")
        pdf.cell(col_w[1], 8, param, border=1, fill=bold, align="C")
        pdf.cell(col_w[2], 8, price, border=1, fill=bold, align="C")
        pdf.cell(col_w[3], 8, total, border=1, fill=bold, align="R")
        pdf.ln()

    row("Командировочные", f"{calc.total_days} дн.", "", _rub(calc.daily_cost))
    row("Суточные", f"{calc.total_days} дн.", "", _rub(calc.daily_allowance_total))
    row("Проезд", "", "", _rub(calc.travel_cost))
    row("Проведение работ", "", "", _rub(calc.work_cost))
    if calc.hotel_nights > 0:
        row("Проживание", f"{calc.hotel_nights} ноч.", "", _rub(calc.hotel_total))
    row("Дней на работы", str(calc.work_days), "(информационно)", "—")
    row("ИТОГО", "", "", _rub(calc.total), bold=True)

    pdf.ln(8)
    pdf.set_font("DejaVu", "", 8)
    pdf.cell(0, 5, f"Расчет выполнил: {calc.calculated_by}", align="R")

    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    pdf.output(filepath)
    return filepath
