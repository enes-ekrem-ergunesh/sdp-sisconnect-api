import requests
from tests.base_test import BaseTestCase


class AuthenticationTestCase(BaseTestCase):
    classPath = "authentication"

    def test_login_with_email_password(self):
        method = "POST"
        payload = {
          "email": "eergunes@sis.edu.eg",
          "password": "DevTest123"
        }
        headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        url = f"{self.BASE_URL}/{AuthenticationTestCase.classPath}/"
        response = requests.post(url, json=payload, headers=headers)
        self.assertEqual(response.status_code, 200, f"{method} /{AuthenticationTestCase.classPath}/ failed.")
