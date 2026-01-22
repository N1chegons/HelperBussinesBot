class BaseExceptions(Exception):
    pass

class AppointmentsNotFound(BaseExceptions):
    pass

class AppointmentsCreatedError(BaseExceptions):
    pass

class AppointmentsUpdateError(BaseExceptions):
    pass