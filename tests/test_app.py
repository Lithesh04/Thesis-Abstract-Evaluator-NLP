import unittest
from io import BytesIO

from app import app


class ThesisEvaluatorAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Thesis Abstract Evaluator", response.data)

    def test_evaluate_text_success(self):
        payload = {
            "abstract": "This study defines the research objective, applies a method, reports a 10% improvement, and concludes with contribution."
        }
        response = self.client.post("/evaluate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("score", data)
        self.assertIn("dimensions", data)
        self.assertIn("rewrite_suggestions", data)

    def test_evaluate_text_empty(self):
        response = self.client.post("/evaluate", json={"abstract": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_evaluate_file_missing(self):
        response = self.client.post("/evaluate-file", data={}, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_evaluate_file_unsupported_extension(self):
        response = self.client.post(
            "/evaluate-file",
            data={"file": (BytesIO(b"plain text"), "note.txt")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
