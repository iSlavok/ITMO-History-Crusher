import asyncio
import time

from aiogram import Bot

from bot.config import messages, config
from bot.models import User
from bot.services import FightSession


class FightManager:
    def __init__(self):
        self.active_sessions = {}
        self.waiting_player: User | None = None
        self.waiting_timestamp: int = 0
        self.waiting_task = None

    async def add_waiting_player(self, player: User, bot: Bot) -> FightSession | None:
        current_time = time.time()
        if self.waiting_player is not None and self.waiting_player.id != player.id:
            if current_time - self.waiting_timestamp < config.fight_waiting_player_timeout:
                if self.waiting_task is not None:
                    self.waiting_task.cancel()
                session = FightSession(
                    player1_id=self.waiting_player.id,
                    player1_username=self.waiting_player.username,
                    player2_id=player.id,
                    player2_username=player.username,
                    on_game_end_callback=self.remove_session
                )
                self.active_sessions[session.session_id] = session
                self.waiting_player = None
                return session
        self.waiting_player = player
        self.waiting_timestamp = current_time
        self.waiting_task = asyncio.create_task(self._remove_waiting_player_after_timeout(player.id, bot))
        return None

    async def _remove_waiting_player_after_timeout(self, player_id: int, bot: Bot):
        await asyncio.sleep(config.fight_waiting_player_timeout)
        if self.waiting_player.id == player_id:
            self.waiting_player = None
            await bot.send_message(player_id, messages.fight.wait_timeout)

    def get_session_by_player(self, player_id: int) -> FightSession | None:
        for session in self.active_sessions.values():
            if session.is_player_in_game(player_id):
                return session
        return None

    def is_player_in_game(self, player_id: int) -> bool:
        return self.get_session_by_player(player_id) is not None

    def remove_session(self, session_id: str):
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
