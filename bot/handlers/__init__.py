from .user_main_handler import get_user_main_router
from .create_question_handler import get_create_question_router
from .test_handler import get_test_router

__all__ = [
    "get_user_main_router",
    "get_create_question_router",
    "get_test_router",
]
