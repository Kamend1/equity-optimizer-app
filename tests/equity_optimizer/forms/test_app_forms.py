from datetime import date
from django.test import TestCase
from EquityOptimizerApp.equity_optimizer.forms import BaseDataRangeForm, DateRangeForm


class BaseDataRangeFormTestCase(TestCase):
    def setUp(self):
        self.valid_data = {
            'start_date': '2022-01-01',
            'end_date': '2023-01-01'
        }
        self.invalid_date_range_data = {
            'start_date': '2023-01-01',
            'end_date': '2022-01-01'
        }
        self.before_min_date_data = {
            'start_date': '2009-12-31',
            'end_date': '2023-01-01'
        }

    def test_valid_date_range(self):
        form = BaseDataRangeForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_date_range(self):
        form = BaseDataRangeForm(data=self.invalid_date_range_data)
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)
        self.assertEqual(form.errors['end_date'][0], "End date cannot be start date or earlier than start date.")

    def test_start_date_before_min_date(self):
        form = BaseDataRangeForm(data=self.before_min_date_data)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
        self.assertEqual(form.errors['start_date'][0], "Start date cannot be before January 1, 2010.")

    def test_date_range_form_inherits_clean(self):
        form = DateRangeForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
