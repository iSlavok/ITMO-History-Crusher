import calendar

from pydantic import BaseModel, Field, model_validator


class PartialDate(BaseModel):
    year: int = Field(..., description="Год", ge=1)
    month: int | None = Field(None, description="Месяц (1-12)", ge=1, le=12)
    day: int | None = Field(None, description="День (1-31)", ge=1)

    @model_validator(mode='after')
    def check_date_logic(self) -> 'PartialDate':
        if self.day is not None and self.month is None:
            raise ValueError({"day": "День не может быть указан без месяца"})
        if self.day is not None and self.month is not None:
            max_days = calendar.monthrange(self.year, self.month)[1]
            if not (1 <= self.day <= max_days):
                raise ValueError(
                    {"day": f"День недопустим для {self.month:02d}.{self.year}. Допустимые значения: 1-{max_days}"})
        return self

    def __str__(self):
        if self.day is not None and self.month is not None:
            return f"{self.day:02d}.{self.month:02d}.{self.year}"
        elif self.month is not None:
            return f"{self.month:02d}.{self.year}"
        else:
            return str(self.year)

    def __eq__(self, other):
        if not isinstance(other, PartialDate):
            return NotImplemented
        return (self.year, self.month, self.day) == (other.year, other.month, other.day)

    def __hash__(self):
        return hash((self.year, self.month, self.day))
