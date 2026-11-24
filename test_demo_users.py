#!/usr/bin/env python3
import urllib.request
import json
import unittest

class TestDemoUsers(unittest.TestCase):
    BASE_URL = "http://localhost:8000"

    def test_01_get_demo_users(self):
        req = urllib.request.Request(f"{self.BASE_URL}/api/demo_users")
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertIn("demo_users", data)
            users = data["demo_users"]
            self.assertGreaterEqual(len(users), 3)
            # Check default personas
            roles = [u["role"] for u in users]
            self.assertIn("Park Manager", roles)
            self.assertIn("Collector", roles)
            self.assertIn("Tenant", roles)

    def test_02_post_demo_user(self):
        payload = {
            "name": "Dr. Sarah Lin",
            "role": "Tenant",
            "scope": "EcoPack Solutions"
        }
        req = urllib.request.Request(
            f"{self.BASE_URL}/api/demo_users",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertTrue(data.get("success"))
            user = data.get("user")
            self.assertEqual(user["name"], "Dr. Sarah Lin")
            self.assertEqual(user["role"], "Tenant")
            self.assertEqual(user["scope"], "EcoPack Solutions")

    def test_03_state_has_demo_users(self):
        req = urllib.request.Request(f"{self.BASE_URL}/api/state")
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertIn("demo_users", data)
            self.assertIsInstance(data["demo_users"], list)

if __name__ == "__main__":
    unittest.main()
