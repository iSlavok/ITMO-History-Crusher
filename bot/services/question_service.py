import calendar
import random
import re
from operator import attrgetter
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import config
from bot.enums import AnswerType
from bot.models import Question, Answer, User, PublicQuestion, PublicAnswer
from bot.repositories import AnswerRepository, QuestionRepository, PublicQuestionRepository, PublicAnswerRepository
from bot.schemas import PartialDate, QuestionInfo
from bot.services.exceptions import DateParsingError, QuestionNotFoundError, AnswerNotFoundError

ANSWERS_HISTORY_LIMIT = config.answer_history_limit
BOOST_ANSWER_THRESHOLD = config.boost_answer_threshold
BOOST_LIMIT_FACTOR = config.boost_limit_factor
MAX_WEIGHT_DURING_BOOST = config.max_weight_during_boost
MIN_FINAL_WEIGHT = config.min_final_weight


class QuestionService:
    def __init__(self, session: AsyncSession, question_repo: QuestionRepository, answer_repo: AnswerRepository,
                 public_question_repo: PublicQuestionRepository, public_answer_repo: PublicAnswerRepository):
        self.session = session
        self.question_repo = question_repo
        self.answer_repo = answer_repo
        self.public_question_repo = public_question_repo
        self.public_answer_repo = public_answer_repo

    async def get_random_question(self, user: User) -> Question | PublicQuestion | None:
        user_questions = await self.question_repo.get_prioritized_questions(user=user) or []
        public_questions = []
        if user.enable_public_questions:
            public_questions = await self.public_question_repo.list_all(limit=1000) or []
        questions = user_questions + public_questions
        if not questions:
            return None
        weights = (
                [q.weight for q in user_questions] +
                [10] * len(public_questions)
        )
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

    async def _submit_answer_and_update_weight(self, question: Question, raw_user_input: str, user_date: PartialDate,
                                               answer_type: AnswerType, answer_id: int = None) -> Answer:
        if answer_id:
            answer = await self.answer_repo.get_with_question(answer_id)
            if answer is None:
                raise AnswerNotFoundError
            answer.type = answer_type
        else:
            answer = Answer(
                question=question,
                text=raw_user_input,
                year=user_date.year,
                month=user_date.month,
                day=user_date.day,
                type=answer_type
            )
            self.answer_repo.add(answer)
            await self.session.flush([answer])

        last_types, total_count = await self.answer_repo.get_answer_counts_for_weight(
            question_id=question.id,
            history_limit=ANSWERS_HISTORY_LIMIT
        )

        incorrect_count = last_types.count(AnswerType.INCORRECT)
        part_count = last_types.count(AnswerType.PART)

        base_weight_calc = (2.0 * incorrect_count) + (1.0 * part_count)
        final_weight = base_weight_calc

        if 0 < total_count < BOOST_ANSWER_THRESHOLD:
            boost_multiplier = BOOST_LIMIT_FACTOR / total_count
            boosted_weight = base_weight_calc * boost_multiplier
            final_weight = min(MAX_WEIGHT_DURING_BOOST, boosted_weight)

        final_weight = max(MIN_FINAL_WEIGHT, final_weight)
        question.weight = final_weight

        self.question_repo.add(question)
        await self.session.commit()
        return answer

    async def _submit_public_answer(self, question: PublicQuestion, raw_user_input: str, user_date: PartialDate,
                                    user: User, answer_type: AnswerType, answer_id: int = None) -> PublicAnswer:
        if answer_id:
            answer = await self.public_answer_repo.get_by_id(answer_id)
            if answer is None:
                raise AnswerNotFoundError
            answer.type = answer_type
        else:
            answer = PublicAnswer(
                text=raw_user_input,
                year=user_date.year,
                month=user_date.month,
                day=user_date.day,
                type=answer_type
            )
            answer.question = question
            answer.user = user
            self.public_answer_repo.add(answer)
            await self.session.flush([answer])

        await self.session.commit()
        return answer

    async def submit_user_text_public_answer(self, question_id: int, raw_user_input: str, user: User) -> PublicAnswer:
        user_date = self.parse_date_string(raw_user_input)
        question = await self.public_question_repo.get_by_id(question_id)
        if question is None:
            raise QuestionNotFoundError
        answer_type = self._compare_dates(user_date, question.correct_answer_date)
        return await self._submit_public_answer(question=question, raw_user_input=raw_user_input, user_date=user_date,
                                                answer_type=answer_type, user=user)

    async def submit_user_text_answer(self, question_id: int, raw_user_input: str) -> Answer:
        user_date = self.parse_date_string(raw_user_input)
        question = await self.question_repo.get_by_id(question_id)
        if question is None:
            raise QuestionNotFoundError
        answer_type = self._compare_dates(user_date, question.correct_answer_date)
        return await self._submit_answer_and_update_weight(question=question, raw_user_input=raw_user_input,
                                                           user_date=user_date, answer_type=answer_type)

    async def submit_user_choice_public_answer(self, text_answer_id: int, user_date: PartialDate) -> PublicAnswer:
        answer = await self.public_answer_repo.get_with_question(text_answer_id)
        if answer is None:
            raise AnswerNotFoundError
        question = answer.question
        answer_type = self._compare_dates(user_date, question.correct_answer_date)
        if answer_type == AnswerType.CORRECT:
            return await self._submit_public_answer(question=question, raw_user_input=answer.text,
                                                    user_date=user_date, answer_type=AnswerType.PART,
                                                    answer_id=text_answer_id, user=answer.user)
        return answer

    async def submit_user_choice_answer(self, text_answer_id: int, user_date: PartialDate) -> Answer:
        answer = await self.answer_repo.get_with_question(text_answer_id)
        if answer is None:
            raise AnswerNotFoundError
        question = answer.question
        answer_type = self._compare_dates(user_date, question.correct_answer_date)
        if answer_type == AnswerType.CORRECT:
            return await self._submit_answer_and_update_weight(question=question, raw_user_input=answer.text,
                                                               user_date=user_date, answer_type=AnswerType.PART,
                                                               answer_id=text_answer_id)
        return answer

    @staticmethod
    def generate_distractor_dates(user_date: PartialDate, correct_date: PartialDate, user: User) -> list[PartialDate]:
        distractor_count = user.suggested_answers_count - 1

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

    async def create_question(self, user: User, text: str, correct_answer_date: PartialDate) -> Question:
        question = Question(text=text)
        question.user = user
        question.correct_answer_date = correct_answer_date
        self.question_repo.add(question)
        await self.session.commit()
        return question

    async def create_public_question(self, text: str, correct_answer_date: PartialDate) -> PublicQuestion:
        question = PublicQuestion(text=text)
        question.correct_answer_date = correct_answer_date
        self.public_question_repo.add(question)
        await self.session.commit()
        return question

    async def get_questions(self, user: User, page: int = 1, limit: int = 10,
                            latest_answers_limit: int = 10) -> list[QuestionInfo]:
        if page < 1:
            page = 1
        skip = (page - 1) * limit
        db_questions: Sequence[Question] = await self.question_repo.get_user_questions_paginated_with_answers(
            user=user, skip=skip, limit=limit
        )
        result_list: list[QuestionInfo] = []
        start_number = skip + 1
        for i, question in enumerate(db_questions):
            all_answers = question.answers
            sorted_answers = sorted(
                all_answers,
                key=attrgetter('created_at'),
                reverse=True
            )
            latest_answers = sorted_answers[:latest_answers_limit]
            score = 0.0
            for answer in latest_answers:
                if answer.type == AnswerType.CORRECT:
                    score += 1.0
                elif answer.type == AnswerType.PART:
                    score += 0.5
            total_considered = len(latest_answers)
            score_str = f"{score:g}/{total_considered}"
            question_info = QuestionInfo(
                number=start_number + i,
                id=question.id,
                text=question.text,
                date=question.correct_answer_date,
                latest_answers_score=score_str
            )
            result_list.append(question_info)
        return result_list

    async def get_public_questions(self, page: int = 1, limit: int = 10) -> Sequence[PublicQuestion]:
        return await self.public_question_repo.list_all(skip=(page - 1) * limit, limit=limit)

    async def get_questions_count(self, user: User) -> int:
        return await self.question_repo.get_user_questions_count(user=user)

    async def get_public_questions_count(self) -> int:
        return await self.public_question_repo.get_public_questions_count()

    async def get_question_by_id(self, question_id: int, user: User) -> Question:
        question = await self.question_repo.get_by_id_and_user(question_id, user)
        if question is None:
            raise QuestionNotFoundError
        return question

    async def get_public_question_by_id(self, question_id: int) -> PublicQuestion:
        question = await self.public_question_repo.get_by_id(question_id)
        if question is None:
            raise QuestionNotFoundError
        return question

    async def delete_question(self, question_id: int, user: User) -> Question:
        question = await self.question_repo.get_by_id_and_user(question_id, user)
        if question is None:
            raise QuestionNotFoundError
        await self.question_repo.delete(question)
        await self.session.commit()
        return question

    async def delete_public_question(self, question_id: int) -> PublicQuestion:
        question = await self.public_question_repo.get_by_id(question_id)
        if question is None:
            raise QuestionNotFoundError
        await self.public_question_repo.delete(question)
        await self.session.commit()
        return question
