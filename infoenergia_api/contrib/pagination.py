from base64 import urlsafe_b64encode, urlsafe_b64decode


class DecodeException(Exception):
    pass


class Pagination(object):

    MAX_PAGE_SIZE = 100

    def __init__(self, elems, page_size):
        self._elems = elems
        self.page_size = page_size if page_size <= self.MAX_PAGE_SIZE else self.MAX_PAGE_SIZE
        self._cursor = 0
        self.len = len(elems)

    def page(self, cursor):
        '''
        return page pointed by cursor
        '''
        self._cursor = self._decode_cursor(cursor)
        if self._cursor < 0:
            self._cursor = 0
        if self._cursor >= self.len:
            self._cursor = self.len - self.page_size

        return self._elems[self._cursor:self._cursor + self.page_size]

    @property
    def next_cursor(self):
        '''
        return next page of the pagination
        '''
        if self._cursor + self.page_size >= self.len:
            return False
        self._cursor += self.page_size

        return self.cursor

    @property
    def cursor(self):
        return self._encode_cursor()

    def _encode_cursor(self):
        return urlsafe_b64encode(str(self._cursor).encode()).decode('utf8')

    def _decode_cursor(self, cursor):
        try:
            return int(urlsafe_b64decode(cursor))
        except ValueError:
            raise DecodeException(f'{cursor} is not a valid value to decode')
