import os
os.environ.setdefault('INFOENERGIA_MODULE_SETTINGS', 'config.settings.testing')

from unittest import TestCase

from infoenergia_api.contrib import Pagination

class PaginationTest(TestCase):

    def setUp(self):
        self.maxDiff = None

    def test__create_pagination_object(self):
        element_list = [num for num in range(0, 10)]
        pagination_list = Pagination(element_list, 2)

        self.assertIsInstance(pagination_list, Pagination)

    def test__create_pagination_object_max_size(self):
        element_list = [num for num in range(0, 10)]

        pagination_list = Pagination(element_list, 150)

        self.assertEqual(pagination_list.page_size, pagination_list.MAX_PAGE_SIZE)

    def test__page(self):
        element_list = [num for num in range(0, 10)]
        pagination_list = Pagination(element_list, 2)

        page = pagination_list.page('MA==')
        self.assertListEqual(page, element_list[:2])

    def test__page__negative_cursor(self):
        element_list = [num for num in range(0, 10)]
        pagination_list = Pagination(element_list, 2)

        page = pagination_list.page('LTE=')
        self.assertListEqual(page, element_list[:2])

    def test__page__out_of_range_cursor(self):
        element_list = [num for num in range(0, 10)]
        pagination_list = Pagination(element_list, 2)

        page = pagination_list.page('MTA=')
        self.assertListEqual(page, element_list[8:10])

    def test__next_cursor(self):
        element_list = [num for num in range(0, 10)]
        pagination_list = Pagination(element_list, 2)

        next_cursor = pagination_list.next_cursor
        self.assertEqual(next_cursor, 'Mg==')

    def test__next_cursor_last_page(self):
        element_list = [num for num in range(0, 4)]
        pagination_list = Pagination(element_list, 2)

        next_cursor = pagination_list.next_cursor
        last_cursor = pagination_list.next_cursor
        self.assertFalse(last_cursor)

    def test__next_last_cursor__odd(self):
        element_list = [num for num in range(0, 5)]
        pagination_list = Pagination(element_list, 2)

        next_cursor = pagination_list.next_cursor
        next_cursor = pagination_list.next_cursor
        self.assertEqual(len(pagination_list.page(next_cursor)), 1)

        last_cursor = pagination_list.next_cursor
        self.assertFalse(last_cursor)

    def test__encode_cursor(self):
        element_list = [num for num in range(0, 5)]
        pagination_list = Pagination(element_list, 2)

        cursor = pagination_list.cursor

        self.assertEqual(cursor, 'MA==')
