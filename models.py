"""Модели данных для расчета стоимости выездных работ (поверка/калибровка)."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


ROLES = {
    "Специалист": {
        "cost_per_day": Decimal("35000"),
        "hotel_per_night": Decimal("10000"),
    },
    "Начальник лаборатории": {
        "cost_per_day": Decimal("55000"),
        "hotel_per_night": Decimal("12000"),
    },
    "Руководитель отдела": {
        "cost_per_day": Decimal("66000"),
        "hotel_per_night": Decimal("12000"),
    },
}

DEFAULT_DAILY_ALLOWANCE = Decimal("700")


@dataclass
class Calculation:
    role: str
    work_days: int
    total_days: Decimal
    hotel_nights: int
    travel_cost: Decimal
    work_cost: Decimal
    daily_allowance: Decimal
    calculated_by: str
    customer: str = ""
    city: str = ""
    work_type: str = ""
    instrument_name: str = ""
    work_location: str = ""
    contract_number: str = ""
    date: datetime = field(default_factory=datetime.now)
    number: Optional[str] = None

    @property
    def cost_per_day(self) -> Decimal:
        return ROLES[self.role]["cost_per_day"]

    @property
    def hotel_per_night(self) -> Decimal:
        return ROLES[self.role]["hotel_per_night"]

    @property
    def daily_cost(self) -> Decimal:
        return self.total_days * self.cost_per_day

    @property
    def daily_allowance_total(self) -> Decimal:
        return self.total_days * self.daily_allowance

    @property
    def hotel_total(self) -> Decimal:
        return Decimal(str(self.hotel_nights)) * self.hotel_per_night

    @property
    def total(self) -> Decimal:
        return (
            self.daily_cost
            + self.daily_allowance_total
            + self.travel_cost
            + self.work_cost
            + self.hotel_total
        )

    def breakdown(self) -> list:
        lines = []
        lines.append((f"Командировочные ({self.total_days} дн.)", self.daily_cost))
        lines.append((f"Суточные ({self.total_days} дн.)", self.daily_allowance_total))
        lines.append(("Проезд", self.travel_cost))
        lines.append(("Проведение работ", self.work_cost))
        if self.hotel_nights > 0:
            lines.append((f"Проживание ({self.hotel_nights} ноч.)", self.hotel_total))
        lines.append(("ИТОГО", self.total))
        return lines

    def formatted_date(self, fmt: str = "%d.%m.%Y %H:%M") -> str:
        return self.date.strftime(fmt)

    def formatted_number(self) -> str:
        if self.number:
            return self.number
        return self.date.strftime("%Y%m%d-%H%M%S")
