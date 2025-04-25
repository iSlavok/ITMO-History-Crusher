import os

import yaml
from pathlib import Path

from pydantic import BaseModel


class Config(BaseModel):
    answer_history_limit: int = 10
    boost_answer_threshold: int = 10
    boost_limit_factor: float = 10.0
    max_weight_during_boost: float = 15.0
    min_final_weight: float = 1.0


class Buttons(BaseModel):
    main: str
    adminka: str
    back: str
    test: str
    questions: str
    settings: str

    create_question: str
    list_questions: str
    delete_question: str
    delete_question_confirm: str

    create_public_question: str
    list_public_questions: str
    delete_public_question: str
    delete_public_question_confirm: str

    setting_answer_count: str
    enable_public_questions: str
    disable_public_questions: str

    public_questions: str
    users_list: str


class ErrorMessages(BaseModel):
    date_parsing_error: str
    question_not_found: str
    answer_not_found: str


class CreateQuestionMessages(BaseModel):
    question_text_request: str
    question_date_request: str
    success_created: str


class ListQuestionsMessages(BaseModel):
    header: str
    question: str


class DeleteQuestionMessages(BaseModel):
    id_request: str
    delete_confirm: str
    delete_success: str


class UsersListMessages(BaseModel):
    header: str
    user: str


class TestMessages(BaseModel):
    question: str
    correct_text_answer: str
    incorrect_text_answer: str
    correct_choice_answer: str
    incorrect_choice_answer: str
    question_not_found: str


class QuestionsMessages(BaseModel):
    questions_menu: str
    create_question: CreateQuestionMessages
    list_questions: ListQuestionsMessages
    delete_question: DeleteQuestionMessages

    public_questions_menu: str
    create_public_question: CreateQuestionMessages
    list_public_questions: ListQuestionsMessages
    delete_public_question: DeleteQuestionMessages


class SettingsMessages(BaseModel):
    settings_menu: str
    answer_count_request: str
    answer_count_success: str


class AdminkaMessages(BaseModel):
    adminka_menu: str
    users_list: UsersListMessages


class Messages(BaseModel):
    main_menu: str
    buttons: Buttons
    errors: ErrorMessages
    test: TestMessages
    questions: QuestionsMessages
    settings: SettingsMessages
    adminka: AdminkaMessages


class EnvConfig(BaseModel):
    DB_DRIVER: str = os.getenv("DB_DRIVER")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT"))
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")


def load_config(path: str = "bot/config/config.yaml") -> Config:
    with open(Path(path), encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)
    return Config(**raw_config)


def load_messages(path: str = "bot/config/messages.yaml") -> Messages:
    with open(Path(path), encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)
    return Messages(**raw_config)


def load_env_config() -> EnvConfig:
    return EnvConfig()


config = load_config()
messages = load_messages()
env_config = load_env_config()
