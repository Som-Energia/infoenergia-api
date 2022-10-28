class ApiError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


class NotUrlFoundError(Exception):
    _msg = "I couldn't find an url for the resource {}"
    status_code = 500

    def __init__(self, resource_name):
        msg = self._msg.format(resource_name)
        super().__init__(msg)
