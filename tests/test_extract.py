import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.extract import fetch_html_content, parse_product_details, get_fashion_data, HEADERS
from bs4 import BeautifulSoup
import requests

class TestExtract(unittest.TestCase):

    @patch('utils.extract.requests.get')
    def test_fetch_html_content_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body>Test Page</body></html>"
        mock_get.return_value = mock_response

        result = fetch_html_content("https://example.com")
        self.assertEqual(result, b"<html><body>Test Page</body></html>")
        mock_get.assert_called_once_with("https://example.com", headers=HEADERS, timeout=10)

    @patch('utils.extract.requests.get')
    def test_fetch_html_content_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")
        result = fetch_html_content("https://example.com")
        self.assertIsNone(result)

    @patch('utils.extract.requests.get')
    @patch('utils.extract.time.sleep', return_value=None)
    def test_fetch_html_content_retries_exhausted(self, mock_sleep, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Timeout")
        result = fetch_html_content("https://example.com", retries=2, delay=0)
        self.assertIsNone(result)
        self.assertEqual(mock_get.call_count, 2)

    def test_parse_product_details_complete(self):
        html = """
            <div class="collection-card">
                <div class="product-details"><h3 class="product-title">Cool Jacket</h3></div>
                <div class="price-container">$49.99</div>
                <p>Rating: ⭐ 4.7</p>
                <p>Colors: 3 Colors</p>
                <p>Size: M</p>
                <p>Gender: Male</p>
            </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = parse_product_details(soup.select_one(".collection-card"))
        self.assertEqual(result["Title"], "Cool Jacket")
        self.assertEqual(result["Price"], "$49.99")
        self.assertEqual(result["Rating"], "4.7")
        self.assertEqual(result["Colors"], "3")
        self.assertEqual(result["Size"], "M")
        self.assertEqual(result["Gender"], "Male")
        self.assertIn("Timestamp", result)

    def test_parse_product_details_incomplete(self):
        html = """
            <div class="collection-card">
                <div class="product-details"><h3 class="product-title"></h3></div>
            </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = parse_product_details(soup.select_one(".collection-card"))
        self.assertEqual(result["Title"], "Unknown")
        self.assertEqual(result["Price"], "Unavailable")
        self.assertEqual(result["Rating"], "Invalid")
        self.assertEqual(result["Colors"], "0")
        self.assertEqual(result["Size"], "Unknown")
        self.assertEqual(result["Gender"], "Unknown")

    def test_parse_product_details_no_match(self):
        html = """
            <div class="collection-card">
                <div class="product-details"><h3 class="product-title">Mismatch</h3></div>
                <div class="price-container">$99.99</div>
                <p>Rating: ⭐⭐ Excellent</p>
                <p>Colors: many</p>
                <p>Size: </p>
                <p>Gender: </p>
            </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = parse_product_details(soup.select_one(".collection-card"))
        self.assertEqual(result["Title"], "Mismatch")
        self.assertEqual(result["Rating"], "Invalid")
        self.assertEqual(result["Colors"], "0")
        self.assertEqual(result["Size"], "Unknown")
        self.assertEqual(result["Gender"], "Unknown")

    def test_parse_product_details_none(self):
        self.assertIsNone(parse_product_details(None))

    def test_parse_product_details_exception(self):
        class BadCard:
            def select_one(self, _): return None
            def find(self, *a, **kw): raise ValueError("Forced error")
            def find_all(self, *a, **kw): return []

        result = parse_product_details(BadCard())
        self.assertIsNone(result)

    @patch("utils.extract.fetch_html_content")
    def test_get_fashion_data_one_page(self, mock_fetch):
        html = """
            <html><body>
            <div class="collection-card">
                <div class="product-details"><h3 class="product-title">Test</h3></div>
                <div class="price-container">$25</div>
                <p>Rating: ⭐ 4.5</p>
                <p>Colors: 2 Colors</p>
                <p>Size: M</p>
                <p>Gender: Female</p>
            </div></body></html>
        """
        mock_fetch.return_value = html.encode("utf-8")
        data = get_fashion_data(page_limit=1, pause=0)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["Title"], "Test")

    @patch("utils.extract.fetch_html_content")
    @patch("builtins.print")
    def test_get_fashion_data_no_cards(self, mock_print, mock_fetch):
        html = "<html><body><div class='no-card'></div></body></html>"
        mock_fetch.return_value = html.encode("utf-8")
        data = get_fashion_data(page_limit=1, pause=0)
        self.assertEqual(data, [])
        mock_print.assert_any_call("[INFO] Tidak ada kartu produk di halaman 1.")

    @patch("utils.extract.fetch_html_content")
    def test_get_fashion_data_none_returned_from_parser(self, mock_fetch):
        html = "<html><body><div class='collection-card'></div></body></html>"
        mock_fetch.return_value = html.encode("utf-8")
        with patch("utils.extract.parse_product_details", return_value=None):
            data = get_fashion_data(page_limit=1, pause=0)
            self.assertEqual(data, [])

    @patch("utils.extract.fetch_html_content")
    @patch("utils.extract.time.sleep", return_value=None)
    def test_get_fashion_data_with_pause(self, mock_sleep, mock_fetch):
        html = """
            <html><body>
            <div class="collection-card">
                <div class="product-details"><h3 class="product-title">Pause Test</h3></div>
                <div class="price-container">$55</div>
                <p>Rating: ⭐ 5.0</p>
                <p>Colors: 1 Colors</p>
                <p>Size: S</p>
                <p>Gender: Female</p>
            </div></body></html>
        """
        mock_fetch.return_value = html.encode("utf-8")
        data = get_fashion_data(page_limit=1, pause=1.5)
        self.assertEqual(data[0]["Title"], "Pause Test")
        mock_sleep.assert_called_once_with(1.5)

if __name__ == "__main__":
    unittest.main()
