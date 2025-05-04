import asyncio
import uuid
from datetime import date
from typing import Callable

from aiogram import Bot

from bot.config import messages, config
from bot.database import get_session
from bot.keyboards import get_main_kb
from bot.models import PublicQuestion
from bot.repositories import QuestionRepository, AnswerRepository, PublicQuestionRepository, PublicAnswerRepository
from bot.schemas import FightPlayer, PartialDate
from bot.services import QuestionService


class FightSession:
    def __init__(self, player1_id: int, player1_username: str, player2_id: int, player2_username: str,
                 on_game_end_callback: Callable[[str], None], health: int = config.fight_starting_health):
        self.session_id = str(uuid.uuid4())
        self.player1 = FightPlayer(id=player1_id, username=player1_username, health=health)
        self.player2 = FightPlayer(id=player2_id, username=player2_username, health=health)
        self.current_round = 1
        self.current_question: PublicQuestion | None = None
        self.round_timer_task = None
        self.countdown_task = None
        self._on_game_end = on_game_end_callback

    async def start_game(self, bot: Bot):
        await bot.send_message(self.player1.id, messages.fight.game_start.format(username=self.player2.username))
        await bot.send_message(self.player2.id, messages.fight.game_start.format(username=self.player1.username))
        await self.start_round(bot)

    async def start_round(self, bot: Bot):
        message_text = messages.fight.round_start.format(round=self.current_round,
                                                         time=config.fight_round_countdown_time)
        self.player1.message_id = (await bot.send_message(self.player1.id, message_text)).message_id
        self.player2.message_id = (await bot.send_message(self.player2.id, message_text)).message_id
        self.countdown_task = asyncio.create_task(self._countdown_timer(bot))

    async def _countdown_timer(self, bot: Bot):
        for seconds_left in range(config.fight_round_countdown_time - 1, 0, -1):
            await asyncio.sleep(1)
            message_text = messages.fight.round_start.format(round=self.current_round, time=seconds_left)
            await bot.edit_message_text(message_text, chat_id=self.player1.id, message_id=self.player1.message_id)
            await bot.edit_message_text(message_text, chat_id=self.player2.id, message_id=self.player2.message_id)
        async for session in get_session():
            question_service = QuestionService(
                session=session,
                question_repo=QuestionRepository(session),
                answer_repo=AnswerRepository(session),
                public_question_repo=PublicQuestionRepository(session),
                public_answer_repo=PublicAnswerRepository(session)
            )
            self.current_question = await question_service.get_random_public_question()
        self.player1.current_answer = None
        self.player2.current_answer = None
        message_text = messages.fight.round.format(round=self.current_round, question=self.current_question.text,
                                                   time=config.fight_round_answer_time)
        await bot.edit_message_text(message_text, chat_id=self.player1.id,
                                    message_id=self.player1.message_id)
        await bot.edit_message_text(message_text, chat_id=self.player2.id,
                                    message_id=self.player2.message_id)
        self.round_timer_task = asyncio.create_task(self._answer_timer(bot))

    async def _answer_timer(self, bot: Bot):
        for seconds_left in range(config.fight_round_answer_time - 1, 0, -1):
            await asyncio.sleep(1)
            if self.player1.current_answer is not None and self.player2.current_answer is not None:
                return await self.end_round(bot)
            message_text = messages.fight.round.format(round=self.current_round,
                                                       question=self.current_question.text,
                                                       time=seconds_left)
            if self.player1.current_answer is None:
                await bot.edit_message_text(message_text, chat_id=self.player1.id,
                                            message_id=self.player1.message_id)
            if self.player2.current_answer is None:
                await bot.edit_message_text(message_text, chat_id=self.player2.id,
                                            message_id=self.player2.message_id)
        if self.player1.current_answer is None and self.player2.current_answer is None:
            await bot.send_message(
                self.player1.id,
                messages.fight.game_draw.format(health=self.player1.health, opponent_health=self.player2.health),
            )
            await bot.send_message(
                self.player2.id,
                messages.fight.game_draw.format(health=self.player2.health, opponent_health=self.player1.health),
            )
            self._cleanup_session()
            return None
        return await self.end_round(bot)

    async def process_answer(self, user_id: int, answer: PartialDate, bot: Bot):
        if user_id == self.player1.id and self.player1.current_answer is None:
            player = self.player1
            msg = self.player1.message_id
        elif user_id == self.player2.id and self.player2.current_answer is None:
            player = self.player2
            msg = self.player2.message_id
        else:
            raise ValueError("Player has already answered or is not in the game")
        player.current_answer = answer
        message_text = messages.fight.round_answer.format(round=self.current_round,
                                                          question=self.current_question.text,
                                                          answer=answer)
        await bot.edit_message_text(message_text, chat_id=user_id, message_id=msg)
        if self.player1.current_answer is not None and self.player2.current_answer is not None:
            if self.round_timer_task and not self.round_timer_task.done():
                self.round_timer_task.cancel()
            await self.end_round(bot)

    async def end_round(self, bot: Bot):
        correct_answer = self.current_question.correct_answer_date

        self.player1.current_score = self._calculate_score(self.player1.current_answer)
        self.player2.current_score = self._calculate_score(self.player2.current_answer)

        damage = abs(self.player1.current_score - self.player2.current_score)

        if self.player1.current_score < self.player2.current_score:
            self.player1.health -= damage
            if self.player1.health < 0:
                self.player1.health = 0
            winner = self.player2
            loser = self.player1
        elif self.player2.current_score < self.player1.current_score:
            self.player2.health -= damage
            if self.player2.health < 0:
                self.player2.health = 0
            winner = self.player1
            loser = self.player2
        else:
            await bot.edit_message_text(
                messages.fight.round_draw.format(
                    round=self.current_round,
                    question=self.current_question.text,
                    answer=self.player1.current_answer,
                    score=self.player1.current_score,
                    opponent_answer=self.player2.current_answer,
                    opponent_score=self.player2.current_score,
                    correct_answer=self.current_question.correct_answer_date,
                    health=self.player1.health,
                    opponent_health=self.player2.health
                ),
                chat_id=self.player1.id,
                message_id=self.player1.message_id,
            )
            await bot.edit_message_text(
                messages.fight.round_draw.format(
                    round=self.current_round,
                    question=self.current_question.text,
                    answer=self.player2.current_answer,
                    score=self.player2.current_score,
                    opponent_answer=self.player1.current_answer,
                    opponent_score=self.player1.current_score,
                    correct_answer=self.current_question.correct_answer_date,
                    health=self.player2.health,
                    opponent_health=self.player1.health
                ),
                chat_id=self.player2.id,
                message_id=self.player2.message_id,
            )
            self.current_round += 1
            await asyncio.sleep(1)
            await self.start_round(bot)
            return None

        await bot.edit_message_text(
            messages.fight.round_win.format(
                round=self.current_round,
                question=self.current_question.text,
                answer=winner.current_answer,
                score=winner.current_score,
                opponent_answer=loser.current_answer,
                opponent_score=loser.current_score,
                correct_answer=correct_answer,
                damage=damage,
                health=winner.health,
                opponent_health=loser.health,
            ),
            chat_id=winner.id,
            message_id=winner.message_id,

        )
        await bot.edit_message_text(
            messages.fight.round_lose.format(
                round=self.current_round,
                question=self.current_question.text,
                answer=loser.current_answer,
                score=loser.current_score,
                opponent_answer=winner.current_answer,
                opponent_score=winner.current_score,
                correct_answer=correct_answer,
                damage=damage,
                health=loser.health,
                opponent_health=winner.health,
            ),
            chat_id=loser.id,
            message_id=loser.message_id,
        )

        if self.player1.health <= 0 or self.player2.health <= 0:
            await bot.send_message(winner.id, messages.fight.game_win.format(health=winner.health,
                                                                             opponent_health=loser.health))
            await bot.send_message(loser.id, messages.fight.game_lose.format(health=loser.health,
                                                                             opponent_health=winner.health))
            await bot.send_message(self.player1.id, messages.main_menu, reply_markup=get_main_kb())
            await bot.send_message(self.player2.id, messages.main_menu, reply_markup=get_main_kb())
            self._cleanup_session()
            return None
        else:
            self.current_round += 1
            await asyncio.sleep(1)
            await self.start_round(bot)
            return None

    def is_player_in_game(self, user_id: int) -> bool:
        return user_id in (self.player1.id, self.player2.id)

    def _calculate_score(self, player_answer: PartialDate) -> int:
        correct = self.current_question.correct_answer_date

        if (player_answer.year == correct.year
                and (correct.month is None or player_answer.month == correct.month)
                and (correct.day is None or player_answer.day == correct.day)):
            return 5000

        if correct.day is not None and player_answer.day is not None:
            d_corr = date(correct.year, correct.month, correct.day)
            d_user = date(player_answer.year, player_answer.month, player_answer.day)
            delta_years = abs((d_corr - d_user).days) / 365.2425
        elif correct.month is not None and player_answer.month is not None:
            total_corr = correct.year * 12 + (correct.month - 1)
            total_user = player_answer.year * 12 + (player_answer.month - 1)
            delta_years = abs(total_corr - total_user) / 12.0
        else:
            delta_years = abs(correct.year - player_answer.year)

        if correct.month is not None and player_answer.month is None:
            delta_years += 0.5
        if correct.day is not None and player_answer.day is None:
            delta_years += 1 / 24

        if delta_years > 100:
            return 0
        return int(round(5000 * (1 - delta_years / 100)))

    def _cleanup_session(self):
        if self.round_timer_task:
            self.round_timer_task.cancel()
        if self.countdown_task:
            self.countdown_task.cancel()
        self._on_game_end(self.session_id)

    async def leave_player(self, user_id: int, bot: Bot):
        if user_id == self.player1.id:
            await bot.send_message(self.player2.id, messages.fight.game_win.format(health=self.player2.health,
                                                                                   opponent_health=self.player1.health))
            await bot.send_message(self.player2.id, messages.main_menu, reply_markup=get_main_kb())
        elif user_id == self.player2.id:
            await bot.send_message(self.player1.id, messages.fight.game_win.format(health=self.player1.health,
                                                                                   opponent_health=self.player2.health))
            await bot.send_message(self.player1.id, messages.main_menu, reply_markup=get_main_kb())
        else:
            raise ValueError("Player is not in the game")
        self._cleanup_session()
