"""
Defining error handlers
"""

# pylint: disable=duplicate-code
from unittest import TestCase
import logging

# pylint: disable=unused-import
from wsgi import app  # noqa: F401
from service.common import status

BASE_URL = "/orders"


class TestErrorHandler(TestCase):
    """Error Handler Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    def test_400_bad_request(self):
        """It should return a 400 bad request error"""
        resp = self.client.post(BASE_URL, json={})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_404_not_found(self):
        """It should return a 404 not found error"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_405_method_not_allowed(self):
        """It should return a 405 method not allowed error"""
        resp = self.client.put(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_415_unsupported_media_type(self):
        """It should return a 415 unsupported media type error"""
        resp = self.client.post(BASE_URL, data="not json", content_type="text/plain")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        resp = self.client.post(BASE_URL, data="not content_type")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_500_internal_server_error(self):
        """It should return a 500 internal_server_error error"""
        resp = self.client.get("/trigger_500")
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
