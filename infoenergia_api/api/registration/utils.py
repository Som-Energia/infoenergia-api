from infoenergia_api.contrib import ResponseMixin
from sanic_jwt import Responses
from sanic_jwt.exceptions import AuthenticationFailed, Unauthorized


class ApiAuthResponses(Responses):
    @staticmethod
    def exception_response(request, exception):
        if isinstance(exception, (Unauthorized, AuthenticationFailed)):
            return ResponseMixin.unauthorized_error(exception)
