from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database import Base
from bot.enums import UserRole

if TYPE_CHECKING:
    from . import Question


class User(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum", create_constraint=True, native_enum=False),
        nullable=False,
        default=UserRole.USER
    )

    questions: Mapped[list["Question"]] = relationship("Question", back_populates="user")
