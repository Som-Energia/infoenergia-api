import asyncio

from sanic.log import logger
from sanic.response import json
from sentry_sdk import capture_exception


class ResponseMixin(object):

    serializer = dict

    async def make_response_body(self, request, instances, extra_body):
        serialized_instances = []

        todo = [
            request.app.loop.run_in_executor(
                request.app.ctx.thread_pool, self.serializer, object_
            )
            for object_ in instances
        ]
        while todo:
            logger.debug(f"Dumping to dict {len(todo)} instances")
            done, todo = await asyncio.wait(
                todo, timeout=request.app.config.TASK_TIMEOUT
            )
            for task in done:
                serialized_instances.append(task.result())

        response = {
            "count": len(serialized_instances),
            "data": serialized_instances,
            **extra_body,
        }
        return response

    @staticmethod
    def empty_body_response():
        response = {
            "error": {
                "code": "empty_body",
                "message": "Body is empty, request will be not processed",
            }
        }
        return json(response, status=400)

    def error_response(self, exception):
        response = {
            "error": {
                "code": exception.code,
                "message": str(exception),
            }
        }
        return json(response, status=400)

    @staticmethod
    def unauthorized_error_response(exception):
        reason = exception.args[0]
        response = {"error": {"code": "unauthorized", "message": "".join(reason)}}
        return json(response, 401)

    @staticmethod
    def unexpected_error_response(exception):
        capture_exception(exception)
        response = {
            "error": {
                "code": "unexpected_error",
                "message": f"Sorry, an unexpected error append: {str(exception)}",
            }
        }
        return json(response, 500)
