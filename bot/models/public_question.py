from typing import TYPE_CHECKING

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database import Base
from bot.schemas import PartialDate

if TYPE_CHECKING:
    from . import PublicAnswer


class PublicQuestion(Base):
    text: Mapped[str] = mapped_column(nullable=False)
    answer_year: Mapped[int] = mapped_column(Integer, nullable=False)
    answer_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    answer_day: Mapped[int | None] = mapped_column(Integer, nullable=True)

    answers: Mapped[list["PublicAnswer"]] = relationship("PublicAnswer", back_populates="question")

    @property
    def correct_answer_date(self) -> PartialDate:
        return PartialDate(
            year=self.answer_year,
            month=self.answer_month,
            day=self.answer_day
        )

    @correct_answer_date.setter
    def correct_answer_date(self, value: PartialDate):
        if not isinstance(value, PartialDate):
            raise TypeError("Expected a PartialDate instance.")
        self.answer_year = value.year
        self.answer_month = value.month
        self.answer_day = value.day
