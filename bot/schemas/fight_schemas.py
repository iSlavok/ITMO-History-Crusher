from pydantic import BaseModel

from bot.schemas import PartialDate


class FightPlayer(BaseModel):
    id: int
    username: str
    health: int
    current_answer: PartialDate | None = None
    current_score: int = 0
    message_id: int | None = None
