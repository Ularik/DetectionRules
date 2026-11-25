class NoResultException(Exception):
    detail = "Ошибка"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ObjectNotFoundException(NoResultException):
    detail = "Объект не найден"

class UserNotFoundException(NoResultException):
    detail = "Сотрудник не найден"

class RuleNotFoundException(ObjectNotFoundException):
    detail = "Правило не найдено"

class AuditNotFoundException(ObjectNotFoundException):
    detail = "История не найдена"

class UniqueObjIsExistException(Exception):
    detail = 'Такой объект уже существует'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class RuleAlreadyExistException(UniqueObjIsExistException):
    detail = "Такое правило уже существует"

class HasNotRightsException(Exception):
    detail = 'У вас недостаточно прав'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class InvalidSearchParamsException(Exception):
    detail = "Некорректные параметры поиска"
    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)

class StorageUnavailableException(Exception):
    detail = "Хранилище правил (Elasticsearch) недоступно, попробуйте позже"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

