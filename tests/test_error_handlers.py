"""
Defining error handlers
"""

from service.common import status
from tests.test_base import TestBase

BASE_URL = "/api/orders"


class TestErrorHandler(TestBase):
    """Error Handler Tests"""

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
        resp = self.client.get("/api/trigger_500")
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
