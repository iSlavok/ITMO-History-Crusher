from enum import Enum


class AnswerType(str, Enum):
    CORRECT = "correct"
    PART = "partially correct"
    INCORRECT = "incorrect"
