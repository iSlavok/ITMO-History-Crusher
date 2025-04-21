from .adminka_handler import router as adminka_router
from .public_questions_handler import router as public_questions_router
from .create_public_question_handler import router as create_public_question_router
from .delete_public_question_handler import router as delete_public_question_router
from .users_list_handler import router as users_list_router

adminka_router.include_routers(
    public_questions_router,
    create_public_question_router,
    delete_public_question_router,
    users_list_router,
)

__all__ = [
    "adminka_router",
]
