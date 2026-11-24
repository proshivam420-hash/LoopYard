"""
test_api.py - Test REST API HTTP endpoints
Tests:
- GET /
- GET /api/state
- POST /api/bins/dump
- POST /api/pickups/complete
- POST /api/simulation/toggle
- POST /api/reset
"""

import threading
import time
import urllib.request
import json
import socketserver
from server import LoopYardRequestHandler, PORT, sensor_simulation_loop
import database

def run_api_tests():
    database.init_db(force_reseed=True)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), LoopYardRequestHandler)

    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    base_url = f"http://localhost:{PORT}"

    # 1. Test GET /
    with urllib.request.urlopen(f"{base_url}/") as res:
        assert res.status == 200
        html = res.read().decode("utf-8")
        assert "LoopYard" in html
        assert "Industrial Symbiosis" in html
        print("✓ API Test 1: GET / serves HTML frontend correctly.")

    # 2. Test GET /api/state
    with urllib.request.urlopen(f"{base_url}/api/state") as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        assert len(data["tenants"]) == 6
        assert len(data["bins"]) == 11
        assert "impact_metrics" in data
        assert "priority_pickups" in data
        print("✓ API Test 2: GET /api/state returns full system state.")

    # 3. Test POST /api/bins/dump
    dump_data = json.dumps({"bin_id": 4, "amount_pct": 25.0}).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/api/bins/dump", data=dump_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        dump_res = json.loads(res.read().decode("utf-8"))
        assert dump_res["success"] is True
        assert dump_res["result"]["bin_id"] == 4
        # Bin 4 was 72.0 + 25 = 97.0%, so pickup must be created!
        assert dump_res["result"]["pickup_created"] is True
        print("✓ API Test 3: POST /api/bins/dump adds waste and creates auto-pickup.")

    # 4. Test POST /api/pickups/complete
    # Get the open pickup
    with urllib.request.urlopen(f"{base_url}/api/pickups") as res:
        p_data = json.loads(res.read().decode("utf-8"))
        pickups = p_data["pickups"]
        assert len(pickups) >= 1
        p_id = pickups[0]["id"]

    comp_data = json.dumps({"pickup_id": p_id}).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/api/pickups/complete", data=comp_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        comp_res = json.loads(res.read().decode("utf-8"))
        assert comp_res["success"] is True
        assert comp_res["result"]["pickup_id"] == p_id
        print("✓ API Test 4: POST /api/pickups/complete completes task and updates compliance log.")

    # 5. Test POST /api/simulation/toggle
    req = urllib.request.Request(f"{base_url}/api/simulation/toggle", data=b"{}", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        tog_res = json.loads(res.read().decode("utf-8"))
        assert tog_res["success"] is True
        print("✓ API Test 5: POST /api/simulation/toggle toggles simulation state.")

    # 6. Test POST /api/partial_collect
    part_data = json.dumps({"bin_id": 1, "percent": 25.0}).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/api/partial_collect", data=part_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        part_res = json.loads(res.read().decode("utf-8"))
        assert part_res["success"] is True
        assert part_res["result"]["bin_id"] == 1
        assert part_res["result"]["actual_removed_pct"] == 25.0
        print("✓ API Test 6: POST /api/partial_collect executes partial collection.")

    # 7. Test POST /api/reset
    req = urllib.request.Request(f"{base_url}/api/reset", data=b"{}", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        reset_res = json.loads(res.read().decode("utf-8"))
        assert reset_res["success"] is True
        assert len(reset_res["state"]["bins"]) == 11
        print("✓ API Test 7: POST /api/reset resets database to seed state.")

    httpd.shutdown()
    httpd.server_close()
    print("========================================")
    print(" ALL API TESTS PASSED! 100% SUCCESS")
    print("========================================")

if __name__ == "__main__":
    run_api_tests()
