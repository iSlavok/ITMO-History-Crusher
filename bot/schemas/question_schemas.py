from pydantic import BaseModel, ConfigDict

from bot.schemas import PartialDate


class QuestionInfo(BaseModel):
    number: int
    id: int
    text: str
    date: PartialDate
    latest_answers_score: str

    model_config = ConfigDict(from_attributes=True)
