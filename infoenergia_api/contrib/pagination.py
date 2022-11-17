import pickle
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime

from infoenergia_api.utils import make_uuid
from sanic.log import logger


class DecodeException(Exception):
    pass


class PageNotFoundError(Exception):
    code = "page_not_found"
    pass


class Pagination(object):

    MAX_PAGE_SIZE = 100

    def __init__(self, elems, page_size):
        self._elems = elems
        self.page_size = (
            page_size if page_size <= self.MAX_PAGE_SIZE else self.MAX_PAGE_SIZE
        )
        self._cursor = 0
        self.len = len(elems)

    def page(self, cursor=None):
        """
        return page pointed by cursor
        """
        self._cursor = self._decode_cursor(cursor)
        if self._cursor < 0:
            self._cursor = 0
        if self._cursor >= self.len:
            self._cursor = self.len - self.page_size

        return self._elems[self._cursor : self._cursor + self.page_size], self.len

    @property
    def next_cursor(self):
        """
        return next page of the pagination
        """
        if self._cursor + self.page_size >= self.len:
            return False
        self._cursor += self.page_size

        return self.cursor

    @property
    def cursor(self):
        return self._encode_cursor()

    def _encode_cursor(self):
        return urlsafe_b64encode(str(self._cursor).encode()).decode("utf8")

    def _decode_cursor(self, cursor):
        try:
            return int(urlsafe_b64decode(cursor))
        except ValueError:
            raise DecodeException(f"{cursor} is not a valid value to decode")


class PaginationLinksMixin:
    async def _next_cursor(self, request_id, cursor):
        return (
            urlsafe_b64encode(
                "{request_id}:{cursor}".format(
                    request_id=request_id, cursor=cursor
                ).encode()
            ).decode()
            if cursor
            else ""
        )

    async def _pagination_links(self, request, request_id, pagination_list, **kwargs):
        url = request.url_for(self.endpoint_name, **kwargs)
        url_cursor = await self._next_cursor(request_id, pagination_list.next_cursor)

        if "cch" in self.endpoint_name:
            next_page = (
                "{url}?type={cch_type}&cursor={cursor}&limit={limit}".format(
                    url=url,
                    cch_type=request.args["type"][0],
                    cursor=url_cursor,
                    limit=pagination_list.page_size,
                )
                if url_cursor
                else False
            )
        else:
            next_page = (
                "{url}?cursor={cursor}&limit={limit}".format(
                    url=url, cursor=url_cursor, limit=pagination_list.page_size
                )
                if url_cursor
                else False
            )

        return dict(
            cursor=url_cursor,
            next_page=next_page,
        )

    async def paginate_results(self, request, function, **kwargs):
        args = request.args
        page_size = int(
            args.get("limit", request.app.config.get("MAX_RESULT_SIZE", 50))
        )
        links = {}
        total_results = 0

        if "cursor" in args:
            encoded_cursor = args.get("cursor", "")
            request_id, cursor = (
                urlsafe_b64decode(encoded_cursor.encode()).decode().split(":")
            )
            binary_results = await request.app.ctx.redis.get(request_id)
            if not binary_results:
                raise PageNotFoundError(
                    f"Sorry cursor {encoded_cursor} is no available"
                )

            results_pagination = pickle.loads(binary_results)
            results_ids, total_results = results_pagination.page(cursor)
            links = await self._pagination_links(
                request, request_id, results_pagination, **kwargs
            )
        else:
            contract_id = kwargs.get("contract_id")
            results_ids = await function(request, contract_id)
            total_results = len(results_ids)

            logger.info(f"There are {total_results} results to process")

            if total_results > page_size:
                request_id = make_uuid(str(datetime.now()), id(request))
                results_pagination = Pagination(results_ids, page_size)
                results_ids, total_results = results_pagination.page(
                    results_pagination.cursor
                )
                links = await self._pagination_links(
                    request, request_id, results_pagination, **kwargs
                )
                await request.app.ctx.redis.set(
                    request_id, pickle.dumps(results_pagination)
                )
                await request.app.ctx.redis.expire(
                    request_id, request.app.config.get("RESULTS_TTL", 60)
                )
        return results_ids, links, total_results
