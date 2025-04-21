from .user_main_handler import router as user_main_router
from .questions import questions_router
from .test_handler import router as test_router
from .user_settings_handler import router as user_settings_router
from .adminka import adminka_router

__all__ = [
    "user_main_router",
    "questions_router",
    "test_router",
    "user_settings_router",
    "adminka_router",
]
