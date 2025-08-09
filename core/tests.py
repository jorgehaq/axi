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




from io import BytesIO
from django.contrib.auth.models import User
from django.test import TestCase, Client
from .models import DataFile, Token

class AnalyticsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("u1", password="p1")
        # login
        res = self.client.post("/auth/login", data='{"username":"u1","password":"p1"}',
                               content_type="application/json")
        self.token = res.json()["token"]

    def _auth(self):
        return {"HTTP_AUTHORIZATION": f"Token {self.token}"}

    def test_preview_and_summary(self):
        csv = BytesIO(b"a,b,c\n1,2,3\n4,5,6\n7,8,9\n")
        csv.name = "s.csv"
        up = self.client.post("/upload", {"file": csv}, **self._auth())
        file_id = up.json()["id"]

        prev = self.client.get(f"/data/{file_id}/preview")
        self.assertEqual(prev.status_code, 200)
        self.assertTrue(len(prev.json()["rows"]) <= 5)

        summ = self.client.get(f"/data/{file_id}/summary")
        self.assertEqual(summ.status_code, 200)
        s = summ.json()["summary"]
        self.assertIn("a", s)
        self.assertIn("mean", s["a"])