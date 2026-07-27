"""Streamlit-приложение «Расчет стоимости выездных работ»."""

import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from decimal import Decimal
from datetime import datetime

from models import Calculation, ROLES, DEFAULT_DAILY_ALLOWANCE
from storage import save_calculation_to_docx
from export import export_calculation_to_pdf

st.set_page_config(page_title="Расчет стоимости выездных работ", layout="wide")

st.markdown("""<style>
.block-container { padding-top: 1.5rem; padding-bottom: 0; max-width: 100%; }
div[data-testid="stVerticalBlock"] > div { gap: 0.3rem; }
</style>""", unsafe_allow_html=True)

st.markdown("## Расчет стоимости выездных работ")
st.caption("поверка · калибровка · испытания")

left, right = st.columns([1, 1])

with left:
    c1, c2 = st.columns(2)
    role = c1.selectbox("Сотрудник", list(ROLES.keys()))
    work_type = c2.selectbox("Вид работ", ["поверка", "калибровка", "испытания"])

    instrument_name = st.text_input("Наименование СИ", "", placeholder="Обязательно")
    customer = st.text_input("Заказчик", "", placeholder="Обязательно")
    work_location = st.text_input("Место проведения работ", "", placeholder="Обязательно")

    no_contract = st.checkbox("КП/договор отсутствует")
    contract_number = st.text_input("Номер КП/договора (1С)", "", disabled=no_contract)

    c1, c2, c3 = st.columns(3)
    total_days = c1.number_input("Всего дней", min_value=1, max_value=365, value=3)
    work_days = c2.number_input("Дней на работы", min_value=0, max_value=365, value=1)
    hotel_nights = c3.number_input("Ночей в отеле", min_value=0, max_value=365, value=2)

with right:
    c1, c2, c3 = st.columns(3)
    work_cost = c1.number_input("Стоимость работ", min_value=0.0, value=0.0, format="%.0f",
                                disabled=(work_type == "испытания"))
    travel_cost = c2.number_input("Проезд", min_value=0.0, value=0.0, format="%.0f")
    daily_allowance = c3.number_input("Суточные", min_value=0.0, value=float(DEFAULT_DAILY_ALLOWANCE), format="%.0f")

    calculated_by = st.text_input("Кто рассчитывает", "", placeholder="Обязательно")

    calc = Calculation(
        role=role, work_days=int(work_days),
        total_days=Decimal(str(total_days)), hotel_nights=int(hotel_nights),
        travel_cost=Decimal(str(travel_cost)), work_cost=Decimal(str(work_cost)),
        daily_allowance=Decimal(str(daily_allowance)),
        calculated_by=calculated_by, customer=customer,
        work_type=work_type, instrument_name=instrument_name,
        work_location=work_location,
        contract_number="" if no_contract else contract_number.strip(),
        date=datetime.now(),
    )

    contract_value = "" if no_contract else contract_number.strip()
    file_prefix = "_".join(filter(None, [customer.strip(), work_location.strip(), instrument_name.strip(), contract_value]))
    if not file_prefix:
        file_prefix = calc.formatted_number()

    can_save = all([
        calculated_by.strip(), customer.strip(),
        instrument_name.strip(), work_location.strip(),
    ])

    st.divider()

    st.caption(f"**{customer}** — {work_location}" if customer and work_location else "")
    st.markdown(f"### {calc.total:,.2f} руб.".replace(",", " "))

    if "docx_data" not in st.session_state:
        st.session_state.docx_data = None
        st.session_state.pdf_data = None
        st.session_state.docx_name = ""
        st.session_state.pdf_name = ""

    ba, bb = st.columns(2)
    with ba:
        if st.button("Сохранить Word", use_container_width=True, disabled=not can_save):
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
                path = save_calculation_to_docx(calc, f.name)
            with open(path, "rb") as f:
                st.session_state.docx_data = f.read()
            st.session_state.docx_name = f"Смета_{file_prefix}.docx"
            os.unlink(path)
    with bb:
        if st.button("Экспорт PDF", use_container_width=True, disabled=not can_save):
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                path = export_calculation_to_pdf(calc, f.name)
            with open(path, "rb") as f:
                st.session_state.pdf_data = f.read()
            st.session_state.pdf_name = f"Смета_{file_prefix}.pdf"
            os.unlink(path)

    if st.session_state.docx_data:
        st.download_button("Скачать Word", st.session_state.docx_data,
            file_name=st.session_state.docx_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True, key="dw")
    if st.session_state.pdf_data:
        st.download_button("Скачать PDF", st.session_state.pdf_data,
            file_name=st.session_state.pdf_name,
            mime="application/pdf", use_container_width=True, key="dp")
