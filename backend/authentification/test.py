from django.test import TestCase

class FirstTestCase(TestCase):

    def setUp(self):
        print('setup called')

    def test_equal(self):
        self.assertEqual(1, 1)



