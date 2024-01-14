import unittest
from src.utils import html_parser

class TestHtmlParser(unittest.TestCase):
    def test_remove_html_tags(self):
        test_str = "<p>Hello, world!</p>"
        result = html_parser.remove_html_tags(test_str)
        self.assertEqual(result, "Hello, world!")

if __name__ == '__main__':
    unittest.main()