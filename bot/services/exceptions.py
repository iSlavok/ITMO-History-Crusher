class ServiceError(Exception):
    pass


class QuestionServiceError(ServiceError):
    pass


class DateParsingError(QuestionServiceError):
    pass


class QuestionNotFoundError(QuestionServiceError):
    pass


class AnswerNotFoundError(QuestionServiceError):
    pass
