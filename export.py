"""Экспорт сметы в PDF через reportlab."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from models import Calculation, ROLES


try:
    pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
    FONT_NAME = "DejaVu"
    FONT_BOLD = "DejaVu-Bold"
except Exception:
    FONT_NAME = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"


def _rub(value) -> str:
    return f"{value:,.2f} ₽".replace(",", " ")


def _footer(canvas, doc, calculated_by: str):
    canvas.saveState()
    canvas.setFont(FONT_NAME, 8)
    canvas.drawRightString(
        A4[0] - 20 * mm, 12 * mm,
        f"Расчет выполнил: {calculated_by}"
    )
    canvas.restoreState()


def export_calculation_to_pdf(calc: Calculation, filepath: str) -> str:
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=22 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontName=FONT_BOLD, fontSize=18,
        textColor=HexColor("#1A478A"), alignment=TA_CENTER,
        spaceAfter=2 * mm,
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        fontName=FONT_NAME, fontSize=12, alignment=TA_CENTER,
        spaceAfter=6 * mm,
    )
    right_style = ParagraphStyle(
        "Right", parent=styles["Normal"],
        fontName=FONT_NAME, fontSize=10, alignment=TA_RIGHT,
    )
    normal = ParagraphStyle(
        "NC", parent=styles["Normal"],
        fontName=FONT_NAME, fontSize=10,
    )

    story = []
    story.append(Paragraph("РАСЧЕТ СТОИМОСТИ ВЫЕЗДНЫХ РАБОТ", title_style))
    story.append(Paragraph(f"({calc.work_type})" if calc.work_type else "(поверка, калибровка, испытания)", sub_style))
    story.append(Paragraph(f"Дата: {calc.formatted_date()}", right_style))
    story.append(Paragraph(f"Сотрудник: {calc.role}", right_style))
    if calc.customer:
        story.append(Paragraph(f"Заказчик: {calc.customer}", right_style))
    if calc.work_location:
        story.append(Paragraph(f"Место проведения: {calc.work_location}", right_style))
    if calc.contract_number:
        story.append(Paragraph(f"Номер КП (договора): {calc.contract_number}", right_style))
    if calc.instrument_name:
        story.append(Paragraph(f"СИ: {calc.instrument_name}", right_style))
    story.append(Spacer(1, 6 * mm))

    role_rates = ROLES[calc.role]
    table_data = [
        ["Наименование", "Параметр", "Стоимость", "Сумма"],
    ]

    table_data.append([
        Paragraph("Командировочные", normal),
        Paragraph(f"{calc.total_days} дн.", normal),
        "",
        Paragraph(_rub(calc.daily_cost), normal),
    ])
    table_data.append([
        Paragraph("Суточные", normal),
        Paragraph(f"{calc.total_days} дн.", normal),
        "",
        Paragraph(_rub(calc.daily_allowance_total), normal),
    ])
    table_data.append([
        Paragraph("Проезд", normal), "", "", Paragraph(_rub(calc.travel_cost), normal),
    ])
    table_data.append([
        Paragraph("Проведение работ", normal), "", "", Paragraph(_rub(calc.work_cost), normal),
    ])
    if calc.hotel_nights > 0:
        table_data.append([
            Paragraph("Проживание", normal),
            Paragraph(f"{calc.hotel_nights} ноч.", normal),
            "",
            Paragraph(_rub(calc.hotel_total), normal),
        ])
    table_data.append([
        Paragraph("Дней на работы", normal),
        Paragraph(str(calc.work_days), normal),
        Paragraph("(информационно)", normal),
        Paragraph("—", normal),
    ])
    table_data.append([
        Paragraph("<b>ИТОГО</b>", normal), "", "",
        Paragraph(f"<b>{_rub(calc.total)}</b>", normal),
    ])

    col_widths = [doc.width * 0.35, doc.width * 0.25, doc.width * 0.20, doc.width * 0.20]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1A478A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BACKGROUND", (0, -1), (-1, -1), HexColor("#E8EEF7")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 10 * mm))

    def on_page(canvas, doc_obj):
        _footer(canvas, doc_obj, calc.calculated_by)

    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return filepath
