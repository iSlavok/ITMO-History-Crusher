from sqlalchemy import func, select
from sqlalchemy.orm import Session

from bot.models import PublicQuestion
from bot.repositories import BaseRepository


class PublicQuestionRepository(BaseRepository[PublicQuestion]):
    def __init__(self, session: Session):
        super().__init__(session, PublicQuestion)

    def get_public_questions_count(self):
        statement = (
            select(func.count(self.model.id))
        )
        return self.session.scalar(statement) or 0
