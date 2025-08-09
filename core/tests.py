from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Token
from io import BytesIO

class CoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("tester", password="pass12345")

    def test_health(self):
        res = self.client.get("/health/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("status"), "ok")

    def test_login_and_upload(self):
        # login
        res = self.client.post("/auth/login", data='{"username":"tester","password":"pass12345"}',
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        token = res.json().get("token")
        self.assertTrue(Token.objects.filter(key=token).exists())

        # upload
        csv_bytes = BytesIO(b"a,b\n1,2\n")
        csv_bytes.name = "t.csv"
        res2 = self.client.post("/upload", {"file": csv_bytes}, HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(res2.status_code, 200)
        self.assertIn("id", res2.json())