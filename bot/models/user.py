from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String, Enum, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database import Base
from bot.enums import UserRole

if TYPE_CHECKING:
    from . import Question, PublicAnswer


class User(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum", create_constraint=True, native_enum=False),
        nullable=False,
        default=UserRole.USER
    )
    suggested_answers_count: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    enable_public_questions: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    public_answers: Mapped[list["PublicAnswer"]] = relationship(
        "PublicAnswer",
        back_populates="user",
        cascade="all, delete-orphan"
    )
