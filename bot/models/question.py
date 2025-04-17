from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database import Base
from bot.schemas import PartialDate

if TYPE_CHECKING:
    from . import User, Answer


class Question(Base):
    text: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, default=10.0, nullable=False, index=True)
    answer_year: Mapped[int] = mapped_column(Integer, nullable=False)
    answer_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    answer_day: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship("Answer", back_populates="question")

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
