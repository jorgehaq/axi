from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Token
from io import BytesIO
from django.test import override_settings
from django.conf import settings
import tempfile
import os

"""
class CoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("tester", password="pass12345")

    def test_health(self):
        res = self.client.get("/api/health/")
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
"""

class CoreDRFTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("tester", password="pass12345")

    def test_health(self):
        # ✅ ESTE SÍ FUNCIONA - no cambió
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("status"), "ok")

    def test_jwt_login_flow(self):
        # ✅ NUEVO - JWT authentication
        res = self.client.post("/api/token/", {
            "username": "tester",
            "password": "pass12345"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        return data["access"]

    def test_protected_endpoint_requires_auth(self):
        # ✅ NUEVO - Test sin auth
        res = self.client.get("/api/me/")
        self.assertEqual(res.status_code, 401)

    def test_me_endpoint_with_jwt(self):
        # ✅ NUEVO - Test con JWT válido
        token = self.test_jwt_login_flow()
        res = self.client.get("/api/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["username"], "tester")

    def test_upload_with_jwt(self):
        # ✅ ACTUALIZADO - Upload con JWT
        token = self.test_jwt_login_flow()
        csv_bytes = BytesIO(b"a,b\n1,2\n")
        csv_bytes.name = "test.csv"
        
        res = self.client.post("/api/datasets/upload", 
                              {"file": csv_bytes}, 
                              HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(res.status_code, 200)
        self.assertIn("id", res.json())


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




CSV_CONTENT = b"""date,amount,country,category
2024-01-01,10,CO,A
2024-01-01,20,CO,B
2024-01-02,5,PE,A
2024-01-03,30,CO,A
2024-01-10,15,AR,B
"""

@override_settings(
    USE_GCS=False,  # Force local storage
    MEDIA_ROOT=tempfile.mkdtemp(),  # Temporary directory for test files
    MEDIA_URL='/test-media/'
)
class AnalyticsPhase3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("u2", password="p2")
        
        # JWT authentication  
        res = self.client.post("/api/token/", {
            "username": "u2", 
            "password": "p2"
        })
        self.assertEqual(res.status_code, 200)
        self.token = res.json()["access"]
        
        # Upload with local storage (no GCS)
        csv = BytesIO(CSV_CONTENT)
        csv.name = "data.csv"
        up = self.client.post("/api/datasets/upload", 
                             {"file": csv}, 
                             HTTP_AUTHORIZATION=f"Bearer {self.token}")
        
        self.assertEqual(up.status_code, 200)
        self.file_id = up.json()["id"]

    def _auth_headers(self):
        return {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

    def test_rows_filters_pagination(self):
        url = f"/api/datasets/{self.file_id}/rows?columns=date,amount,country&f=country,eq,CO&sort=-amount&page=1&page_size=2"
        r = self.client.get(url, **self._auth_headers())
        self.assertEqual(r.status_code, 200)
        payload = r.json()
        self.assertEqual(payload["page"], 1)
        self.assertEqual(payload["page_size"], 2)
        self.assertGreaterEqual(payload["total"], 1)
        self.assertTrue(isinstance(payload["items"], list))

    def test_correlation_basic(self):
        r = self.client.get(f"/api/datasets/{self.file_id}/correlation?cols=amount", 
                           **self._auth_headers())
        self.assertEqual(r.status_code, 200)
        corr = r.json()["correlation"]
        self.assertIn("amount", corr)

    def test_trend_daily_sum(self):
        url = f"/api/datasets/{self.file_id}/trend?date=date&value=amount&freq=D&agg=sum"
        r = self.client.get(url, **self._auth_headers())
        self.assertEqual(r.status_code, 200)
        arr = r.json()["trend"]
        self.assertTrue(isinstance(arr, list))

    def test_trend_requires_params(self):
        r = self.client.get(f"/api/datasets/{self.file_id}/trend", 
                           **self._auth_headers())
        self.assertEqual(r.status_code, 400)
        
        r2 = self.client.get(f"/api/datasets/{self.file_id}/trend?date=date&agg=count", 
                            **self._auth_headers())
        self.assertEqual(r2.status_code, 200)





# Add temporary test to see exact error
class DebugUploadTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("debug", password="debug123")

    def test_debug_upload_step_by_step(self):
        # Step 1: Test JWT login
        res = self.client.post("/api/token/", {
            "username": "debug", 
            "password": "debug123"
        })
        print(f"Login status: {res.status_code}")
        self.assertEqual(res.status_code, 200)
        token = res.json()["access"]
        print(f"Got token: {token[:20]}...")

        # Step 2: Test upload with detailed error
        csv = BytesIO(b"a,b\n1,2\n")
        csv.name = "debug.csv"
        
        up = self.client.post("/api/datasets/upload", 
                             {"file": csv}, 
                             HTTP_AUTHORIZATION=f"Bearer {token}")
        
        print(f"Upload status: {up.status_code}")
        print(f"Upload response: {up.content.decode()}")
        
        # Don't assert yet, just see what happens
        return up