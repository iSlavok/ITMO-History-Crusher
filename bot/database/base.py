import re
from datetime import datetime

from sqlalchemy import Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, declared_attr


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=None,
        onupdate=func.now(),
        nullable=True
    )

    @declared_attr.directive
    def __tablename__(self) -> str:
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', self.__name__).lower()
        if not name.endswith('s'):
            name += 's'
        return name
