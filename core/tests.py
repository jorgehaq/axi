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





from io import BytesIO
from django.test import TestCase, Client
from django.contrib.auth.models import User

CSV_CONTENT = b"""date,amount,country,category
2024-01-01,10,CO,A
2024-01-01,20,CO,B
2024-01-02,5,PE,A
2024-01-03,30,CO,A
2024-01-10,15,AR,B
"""

class AnalyticsPhase3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("u2", password="p2")
        res = self.client.post("/auth/login", data='{"username":"u2","password":"p2"}',
                               content_type="application/json")
        self.token = res.json()["token"]
        csv = BytesIO(CSV_CONTENT)
        csv.name = "data.csv"
        up = self.client.post("/upload", {"file": csv}, HTTP_AUTHORIZATION=f"Token {self.token}")
        self.file_id = up.json()["id"]

    def test_rows_filters_pagination(self):
        # filtro country=CO, seleccionar columnas y ordenar
        url = f"/data/{self.file_id}/rows?columns=date,amount,country&f=country,eq,CO&sort=-amount&page=1&page_size=2"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        payload = r.json()
        self.assertEqual(payload["page"], 1)
        self.assertEqual(payload["page_size"], 2)
        self.assertGreaterEqual(payload["total"], 1)
        self.assertTrue(isinstance(payload["items"], list))
        if payload["items"]:
            self.assertIn("date", payload["items"][0])

    def test_correlation_basic(self):
        # correlación sobre 'amount' sola (matriz 1x1), debería regresar algo
        r = self.client.get(f"/data/{self.file_id}/correlation?cols=amount")
        self.assertEqual(r.status_code, 200)
        corr = r.json()["correlation"]
        self.assertIn("amount", corr)
        self.assertIn("amount", corr["amount"])

    def test_trend_daily_sum(self):
        # trend por día sumando amount
        url = f"/data/{self.file_id}/trend?date=date&value=amount&freq=D&agg=sum"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        arr = r.json()["trend"]
        self.assertTrue(isinstance(arr, list))
        if arr:
            self.assertIn("date", arr[0])
            self.assertIn("amount", arr[0])

    def test_trend_requires_params(self):
        # falta 'date'
        r = self.client.get(f"/data/{self.file_id}/trend")
        self.assertEqual(r.status_code, 400)
        # agg=count permite omitir 'value'
        r2 = self.client.get(f"/data/{self.file_id}/trend?date=date&agg=count")
        self.assertEqual(r2.status_code, 200)