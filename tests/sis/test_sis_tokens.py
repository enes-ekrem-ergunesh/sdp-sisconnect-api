import requests
from tests.base_test import BaseTestCase


class SisTokensTestCase(BaseTestCase):
    classPath = "tokens"

    def test_get_token_info(self):
        method = "POST"
        payload = {
            "token": "testtoken123"
        }
        headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        url = f"{self.BASE_URL}/{SisTokensTestCase.classPath}/"
        response = requests.post(url, json=payload, headers=headers)
        self.assertEqual(response.status_code, 200, f"{method} /{SisTokensTestCase.classPath}/ failed.")
