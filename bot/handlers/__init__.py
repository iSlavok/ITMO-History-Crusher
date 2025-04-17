from .user_main_handler import router as user_main_router
from .create_question_handler import router as create_question_router
from .test_handler import router as test_router
from .user_settings_handler import router as user_settings_router

__all__ = [
    "user_main_router",
    "create_question_router",
    "test_router",
    "user_settings_router",
]
