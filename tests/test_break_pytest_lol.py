import unittest

class BreaksPytestTestCase(unittest.TestCase):
    @unittest.skip('Remove this decorator and be amazed')
    def test_breaks_pytest(self):
        self.assertEqual(
            'a',
            # This comment alone will break py.test
            1
        )
