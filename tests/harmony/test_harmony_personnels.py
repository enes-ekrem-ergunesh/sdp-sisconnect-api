import requests
from tests.base_test import BaseTestCase

class HarmonyPersonnelsTestCase(BaseTestCase):
    classPath = "harmonyPersonnels"

    def test_get_personnel_by_email(self):
        test_email = "eergunes@sis.edu.eg"
        url = f"{self.BASE_URL}/{HarmonyPersonnelsTestCase.classPath}/{test_email}"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200, f"GET /{HarmonyPersonnelsTestCase.classPath}/{test_email} failed.")
