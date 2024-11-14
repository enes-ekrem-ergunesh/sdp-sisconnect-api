import requests
from tests.base_test import BaseTestCase


class HarmonyStudentsTestCase(BaseTestCase):
    classPath = "harmonyStudents"

    def test_get_student_by_email(self):
        test_email = "2158esad@sis.edu.eg"
        url = f"{self.BASE_URL}/{HarmonyStudentsTestCase.classPath}/{test_email}"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200, f"GET /{HarmonyStudentsTestCase.classPath}/{test_email} failed.")
