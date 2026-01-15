class BaseExceptions(Exception):
    pass

class UserNotFoundError(BaseExceptions):
    pass

class UserAlreadyExistsError(BaseExceptions):
    pass

class UserCreatedError(BaseExceptions):
    pass

class UserUpdateError(BaseExceptions):
    pass