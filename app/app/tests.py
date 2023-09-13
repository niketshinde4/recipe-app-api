"""
Tests
"""
from django.test import SimpleTestCase

class CalcTests(SimpleTestCase):

    def test_add_numbers(self):
        res = calc.add(5, 6)
        self.assertEqual(res, 11)
