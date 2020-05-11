from base64 import urlsafe_b64encode, urlsafe_b64decode

class Pagination(object):

    MAX_PAGE_SIZE = 100

    def __init__(self, elems, page_size):
        self._elems = elems
        self.page_size = page_size if page_size <= self.MAX_PAGE_SIZE else self.MAX_PAGE_SIZE
        self._cursor = 0
        self.len = len(elems)

    @property
    def page(self):
        '''
        return actual page
        '''
        return self._elems[self._cursor:self._cursor + self.page_size]

    @property
    def next_page(self):
        '''
        return next page of the pagination
        '''
        if self._cursor + self.page_size >= self.len:
            return False
        self._cursor += self.page_size

        return self.page

    @property
    def cursor(self):
        return urlsafe_b64encode(str(self._cursor).encode()).decode('utf8')

    def decode_cursor(self):
        return json.loads(urlsafe_b64decode(self.encoded_cursor))

    def link_nextcursor(self):
        if self.encode_cursor():
            absolute_url = self.request.url.split('?')
            return '?'.join([absolute_url[0], 'cursor='+self.encode_cursor()])
        return ''
