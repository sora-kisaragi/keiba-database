import unittest
from src.scraper.jockey_scraper import JockeyScraper

class TestJockeyScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = JockeyScraper()

    def test_send_request(self):
        # Test that the send_request method works as expected
        pass

    def test_parse_html(self):
        # Test that the parse_html method works as expected
        pass

    def test_extract_data(self):
        # Test that the extract_data method works as expected
        pass

if __name__ == '__main__':
    unittest.main()