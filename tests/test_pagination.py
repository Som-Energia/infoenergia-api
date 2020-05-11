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

    def test__next_page(self):
        element_list = [num for num in range(0, 10)]
        pagination_list = Pagination(element_list, 2)

        page_one = pagination_list.next_page
        self.assertListEqual(page_one, element_list[2:4])

    def test__next_last_page(self):
        element_list = [num for num in range(0, 4)]
        pagination_list = Pagination(element_list, 2)

        last_page = pagination_list.next_page
        self.assertListEqual(last_page, element_list[2:4])

        next_page = pagination_list.next_page
        self.assertFalse(next_page)

    def test__next_last_page__odd(self):
        element_list = [num for num in range(0, 5)]
        pagination_list = Pagination(element_list, 2)

        next_page = pagination_list.next_page
        self.assertListEqual(next_page, element_list[2:4])

        next_page = pagination_list.next_page
        self.assertEqual(len(next_page), 1)

        next_page = pagination_list.next_page
        self.assertFalse(next_page)

    def test__encode_cursor(self):
        element_list = [num for num in range(0, 5)]
        pagination_list = Pagination(element_list, 2)

        cursor = pagination_list.cursor

        self.assertEqual(cursor, 'MA==')
