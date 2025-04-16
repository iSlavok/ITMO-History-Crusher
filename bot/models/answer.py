from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database import Base
from ..enums import AnswerType
from ..schemas import PartialDate

if TYPE_CHECKING:
    from . import Question


class Answer(Base):
    text: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[AnswerType] = mapped_column(
        Enum(AnswerType, name="answer_type_enum", create_constraint=True, native_enum=False),
        nullable=False,
    )
    year: Mapped[int] = mapped_column(nullable=False)
    month: Mapped[int | None] = mapped_column(nullable=True)
    day: Mapped[int | None] = mapped_column(nullable=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)

    question: Mapped["Question"] = relationship("Question", back_populates="answers")

    @property
    def date(self) -> PartialDate:
        return PartialDate(
            year=self.year,
            month=self.month,
            day=self.day
        )

    @date.setter
    def date(self, value: PartialDate):
        if not isinstance(value, PartialDate):
            raise TypeError("Expected a PartialDate instance.")
        self.year = value.year
        self.month = value.month
        self.day = value.day
