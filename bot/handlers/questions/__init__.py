from .questions_handler import router as questions_router
from .create_question_handler import router as create_question_router
from .list_questions_handler import router as list_questions_router
from .delete_question_handler import router as delete_question_router

questions_router.include_routers(
    create_question_router,
    list_questions_router,
    delete_question_router,
)

__all__ = [
    "questions_router",
]
