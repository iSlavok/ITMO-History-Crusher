from typing import Generic, TypeVar, Type, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from bot.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, session: Session, model: Type[ModelType]):
        self.session = session
        self.model = model

    def get_by_id(self, obj_id: int) -> ModelType | None:
        return self.session.get(self.model, obj_id)

    def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        statement = (
            select(self.model)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.id)
        )
        result = self.session.execute(statement)
        return result.scalars().all()

    def add(self, db_obj: ModelType) -> None:
        self.session.add(db_obj)

    def delete(self, db_obj: ModelType) -> None:
        self.session.delete(db_obj)
