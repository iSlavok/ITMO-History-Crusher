import calendar
import random
import re

from sqlalchemy.orm import Session

from bot.enums import AnswerType
from bot.models import Question, Answer, User
from bot.repositories import AnswerRepository, QuestionRepository
from bot.schemas import PartialDate
from bot.services.exceptions import DateParsingError, QuestionNotFoundError


class QuestionService:
    ANSWERS_HISTORY_LIMIT = 10  # Кол-во ответов для расчета веса
    BOOST_ANSWER_THRESHOLD = 10  # Порог кол-ва ответов для буста
    BOOST_LIMIT_FACTOR = 10.0  # Множитель для буста (10/k)
    MAX_WEIGHT_DURING_BOOST = 15.0  # Максимальный вес во время буста
    MIN_FINAL_WEIGHT = 1.0  # Минимальный финальный вес

    def __init__(self, session: Session):
        self.session = session
        self.question_repo = QuestionRepository(session)
        self.answer_repo = AnswerRepository(session)

    def get_random_question(self, user: User) -> Question | None:
        questions = self.question_repo.get_prioritized_questions(user=user)
        if not questions:
            return None
        weights = [question.weight for question in questions]
        return random.choices(questions, weights=weights, k=1)[0]

    @staticmethod
    def parse_date_string(raw_string: str) -> PartialDate:
        raw_string = raw_string.strip()
        if re.fullmatch(r"\d{4}", raw_string):
            year = int(raw_string)
            return PartialDate(year=year, month=None, day=None)

        parts: list[str] = []
        if '.' in raw_string:
            parts = raw_string.split('.')
        elif '/' in raw_string:
            parts = raw_string.split('/')
        elif '-' in raw_string:
            if raw_string.count('-') == 2:
                parts = raw_string.split('-')
                if len(parts[0]) == 4:
                    parts = [parts[2], parts[1], parts[0]]
            elif raw_string.count('-') == 1:
                parts = raw_string.split('-')
                if len(parts[0]) == 4:
                    parts = [parts[1], parts[0]]

        parts = [p.strip() for p in parts if p.strip()]
        day: int | None = None

        if len(parts) == 3:
            day = int(parts[0])
            month = int(parts[1])
            year = int(parts[2])
        elif len(parts) == 2:
            month = int(parts[0])
            year = int(parts[1])
        else:
            raise DateParsingError("Unsupported date format structure")
        try:
            return PartialDate(year=year, month=month, day=day)
        except ValueError:
            raise DateParsingError("Invalid date format")

    @staticmethod
    def _compare_dates(user_date: PartialDate, correct_date: PartialDate) -> AnswerType:
        if user_date == correct_date:
            return AnswerType.CORRECT
        return AnswerType.INCORRECT

    def _submit_answer_and_update_weight(self, question: Question, raw_user_input: str, user_date: PartialDate,
                                         answer_type: AnswerType, answer_id: int = None) -> Answer:
        if answer_id:
            answer = self.answer_repo.get_by_id(answer_id)
            if answer is None:
                raise QuestionNotFoundError
            answer.type = answer_type
        else:
            answer = Answer(
                question_id=question.id,
                text=raw_user_input,
                year=user_date.year,
                month=user_date.month,
                day=user_date.day,
                type=answer_type
            )
            self.answer_repo.add(answer)
            self.session.flush([answer])

        last_types, total_count = self.answer_repo.get_answer_counts_for_weight(
            question_id=question.id,
            history_limit=self.ANSWERS_HISTORY_LIMIT
        )

        incorrect_count = last_types.count(AnswerType.INCORRECT)
        part_count = last_types.count(AnswerType.PART)

        base_weight_calc = (2.0 * incorrect_count) + (1.0 * part_count)
        final_weight = base_weight_calc

        if 0 < total_count < self.BOOST_ANSWER_THRESHOLD:
            boost_multiplier = self.BOOST_LIMIT_FACTOR / total_count
            boosted_weight = base_weight_calc * boost_multiplier
            final_weight = min(self.MAX_WEIGHT_DURING_BOOST, boosted_weight)

        final_weight = max(self.MIN_FINAL_WEIGHT, final_weight)
        question.weight = final_weight

        self.session.add(question)
        self.session.commit()

        return answer

    def submit_user_text_answer(self, question_id: int, raw_user_input: str) -> Answer:
        user_date = self.parse_date_string(raw_user_input)
        question = self.question_repo.get_by_id(question_id)
        if question is None:
            raise QuestionNotFoundError
        answer_type = self._compare_dates(user_date, question.correct_answer_date)
        return self._submit_answer_and_update_weight(question=question, raw_user_input=raw_user_input,
                                                     user_date=user_date, answer_type=answer_type)

    def submit_user_choice_answer(self, text_answer_id: int, user_date: PartialDate) -> Answer:
        answer = self.answer_repo.get_by_id(text_answer_id)
        if answer is None:
            raise QuestionNotFoundError
        question = answer.question
        answer_type = self._compare_dates(user_date, question.correct_answer_date)
        if answer_type == AnswerType.CORRECT:
            return self._submit_answer_and_update_weight(question=question, raw_user_input=answer.text,
                                                         user_date=user_date, answer_type=AnswerType.PART,
                                                         answer_id=text_answer_id)
        return answer

    @staticmethod
    def generate_distractor_dates(answer: Answer, user: User) -> list[PartialDate]:
        distractor_count = user.suggested_answers_count-1
        user_date = answer.date
        correct_date = answer.question.correct_answer_date

        years = [correct_date.year] * distractor_count
        months = [correct_date.month] * distractor_count
        days = [correct_date.day] * distractor_count

        if correct_date.year != user_date.year:
            available_years = [year for year in range(correct_date.year - 5, correct_date.year + 6)]
            if ((correct_date.month is not None and correct_date.month != user_date.month)
                    or (correct_date.day is not None and correct_date.day != user_date.day)):
                years = [random.choice(available_years) for _ in range(distractor_count)]
            else:
                available_years.remove(correct_date.year)
                if user_date.year in available_years:
                    available_years.remove(user_date.year)
                years = random.sample(available_years, k=distractor_count)

        if correct_date.month is not None and correct_date.month != user_date.month:
            available_months = [month for month in range(1, 13)]
            if correct_date.day is not None and correct_date.day != user_date.day:
                months = [random.choice(available_months) for _ in range(distractor_count)]
            else:
                for i in range(distractor_count):
                    _available_months = available_months.copy()
                    if years[i] == correct_date.year:
                        _available_months.remove(correct_date.month)
                    if years[i] == user_date.year and user_date.month is not None:
                        _available_months.remove(user_date.month)
                    for j in range(i):
                        if years[i] == years[j]:
                            _available_months.remove(months[j])
                    months[i] = random.choice(_available_months)

        if correct_date.day is not None and correct_date.day != user_date.day:
            for i in range(distractor_count):
                available_days = [day for day in range(1, calendar.monthrange(years[i], months[i])[1] + 1)]
                if years[i] == correct_date.year and months[i] == correct_date.month:
                    available_days.remove(correct_date.day)
                if years[i] == user_date.year and months[i] == user_date.month:
                    available_days.remove(user_date.day)
                for j in range(i):
                    if years[i] == years[j] and months[i] == months[j]:
                        available_days.remove(days[j])
                days[i] = random.choice(available_days)

        dates = [
            PartialDate(year=years[i], month=months[i], day=days[i])
            for i in range(distractor_count)
        ]
        dates.append(correct_date)
        random.shuffle(dates)
        return dates

    def create_question(self, user: User, text: str, correct_answer_date: PartialDate) -> Question:
        question = Question(text=text)
        question.user = user
        question.correct_answer_date = correct_answer_date
        self.question_repo.add(question)
        self.session.commit()
        return question
