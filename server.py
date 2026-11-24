"""
server.py - Zero-Dependency Backend and Sensor Simulator for LoopYard
Runs via standard library `python server.py` on http://localhost:8000.
Contains:
1. SQLite Database Lifecycle (via database.py)
2. Background Sensor Telemetry Simulation Daemon Thread (3s loop)
3. REST API Handlers:
   - GET /api/state: Full dashboard state
   - POST /api/bins/dump: Add +25% fill to specific bin
   - POST /api/pickups/complete: Mark pickup complete, reset bin, record compliance log
   - POST /api/simulation/toggle: Pause / resume live telemetry simulation
   - POST /api/reset: Reset database to fresh seed state
4. Static file serving for single-page web UI.
"""

import http.server
import socketserver
import json
import os
import sys
import threading
import time
import urllib.parse
from datetime import datetime

import database

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Simulation control flags
simulation_running = True
simulation_lock = threading.Lock()

def sensor_simulation_loop():
    """
    Background worker thread: Every 3 seconds, increments the fill percentage
    of each bin at a waste-type-specific fill rate (capped at 100%).
    Auto-creates pickup if fill reaches >= 80% and no open pickup exists.
    """
    global simulation_running
    while True:
        try:
            with simulation_lock:
                is_active = simulation_running

            if is_active:
                database.step_simulation_tick()
        except Exception as e:
            print(f"[Sensor Simulator Error] {e}", file=sys.stderr)

        time.sleep(3.0)

class LoopYardRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Zero-dependency HTTP Request Handler for API & UI."""

    def __init__(self, *args, **kwargs):
        # Serve static files from static directory or project directory
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Add CORS and no-cache headers for smooth local development & live polling
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status_code=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def parse_request_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw_body = self.rfile.read(content_length).decode("utf-8")
            try:
                return json.loads(raw_body)
            except Exception:
                # Fallback to urlencoded
                parsed = urllib.parse.parse_qs(raw_body)
                return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
        return {}

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/" or path == "/index.html":
            # Serve index.html from static or BASE_DIR
            index_path = os.path.join(STATIC_DIR, "index.html")
            if not os.path.exists(index_path):
                index_path = os.path.join(BASE_DIR, "index.html")

            if os.path.exists(index_path):
                with open(index_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_error(404, "index.html not found")
                return

        elif path == "/api/state":
            global simulation_running
            state = database.get_full_system_state()
            state["simulation_running"] = simulation_running
            self.send_json(state)
            return

        elif path == "/api/bins":
            bins = database.get_all_bins()
            self.send_json({"bins": bins})
            return

        elif path == "/api/pickups":
            pickups = database.get_priority_pickups()
            self.send_json({"pickups": pickups})
            return

        elif path == "/api/compliance":
            log = database.get_compliance_log()
            self.send_json({"compliance_log": log})
            return

        elif path == "/api/matches":
            matches = database.get_reuse_matches()
            self.send_json({"matches": matches})
            return

        elif path == "/api/impact":
            impact = database.get_impact_metrics()
            self.send_json({"impact": impact})
            return

        elif path == "/api/demo_users":
            users = database.get_all_demo_users()
            self.send_json({"demo_users": users})
            return

        # Serve static assets if any
        return super().do_GET()

    def do_POST(self):
        global simulation_running
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        body = self.parse_request_body()

        # Handle POST /api/bins/dump or /api/bin/dump
        if path in ("/api/bins/dump", "/api/bin/dump"):
            bin_id = body.get("bin_id") or body.get("id")
            if not bin_id:
                self.send_json({"error": "Missing bin_id parameter"}, 400)
                return

            try:
                bin_id = int(bin_id)
            except ValueError:
                self.send_json({"error": "bin_id must be integer"}, 400)
                return

            amount_pct = float(body.get("amount_pct", 25.0))
            result = database.dump_waste_into_bin(bin_id, amount_pct=amount_pct)
            if not result:
                self.send_json({"error": f"Bin with id {bin_id} not found"}, 404)
                return

            self.send_json({
                "success": True,
                "message": f"Successfully added +{amount_pct}% fill to bin #{bin_id}",
                "result": result,
                "state": database.get_full_system_state()
            })
            return

        # Handle POST /api/partial_collect or /api/bins/collect_partial
        elif path in ("/api/partial_collect", "/api/bins/collect_partial", "/api/bins/partial_collect"):
            bin_id = body.get("bin_id") or body.get("id")
            if not bin_id:
                self.send_json({"error": "Missing bin_id parameter"}, 400)
                return

            try:
                bin_id = int(bin_id)
            except ValueError:
                self.send_json({"error": "bin_id must be integer"}, 400)
                return

            percent = float(body.get("percent") or body.get("remove_pct") or body.get("amount_pct") or 25.0)
            result = database.partial_collect_bin(bin_id, remove_pct=percent)
            if not result:
                self.send_json({"error": f"Bin with id {bin_id} not found"}, 404)
                return

            self.send_json({
                "success": True,
                "message": f"Partially collected -{result['actual_removed_pct']}% ({result['collected_kg']} kg) from Bin #{bin_id}",
                "result": result,
                "state": database.get_full_system_state()
            })
            return

        # Handle POST /api/pickups/complete or /api/pickup/complete
        elif path in ("/api/pickups/complete", "/api/pickup/complete"):
            pickup_id = body.get("pickup_id") or body.get("id")
            if not pickup_id:
                self.send_json({"error": "Missing pickup_id parameter"}, 400)
                return

            try:
                pickup_id = int(pickup_id)
            except ValueError:
                self.send_json({"error": "pickup_id must be integer"}, 400)
                return

            result = database.complete_pickup(pickup_id)
            if not result:
                self.send_json({"error": f"Active open pickup with id {pickup_id} not found"}, 404)
                return

            self.send_json({
                "success": True,
                "message": f"Pickup #{pickup_id} completed successfully. {result['kg_collected']} kg logged to compliance.",
                "result": result,
                "state": database.get_full_system_state()
            })
            return

        # Handle POST /api/simulation/toggle
        elif path == "/api/simulation/toggle":
            with simulation_lock:
                if "running" in body:
                    simulation_running = bool(body["running"])
                else:
                    simulation_running = not simulation_running
                current_status = simulation_running

            self.send_json({
                "success": True,
                "simulation_running": current_status,
                "message": f"Sensor simulation is now {'ACTIVE' if current_status else 'PAUSED'}"
            })
            return

        # Handle POST /api/reset
        elif path == "/api/reset":
            database.init_db(force_reseed=True)
            self.send_json({
                "success": True,
                "message": "Database successfully reseeded to initial factory state.",
                "state": database.get_full_system_state()
            })
            return

        # Handle POST /api/demo_users
        elif path == "/api/demo_users":
            name = str(body.get("name", "Demo User")).strip()
            role = str(body.get("role", "Tenant")).strip()
            scope = str(body.get("scope", "AutoParts Co")).strip()
            new_user = database.create_demo_user(name, role, scope)
            self.send_json({
                "success": True,
                "user": new_user,
                "demo_users": database.get_all_demo_users(),
                "message": f"Demo profile for {name} ({role}) created successfully."
            })
            return

        else:
            self.send_json({"error": f"Unknown POST endpoint {path}"}, 404)
            return

def start_server():
    """Initializes DB, starts sensor simulation thread, and listens on port 8000."""
    print("=" * 65)
    print(" LoopYard: Closed-Loop Industrial Waste Management System")
    print("=" * 65)

    # Initialize database
    database.init_db()
    print("✓ SQLite database initialized & seeded.")

    # Start IoT sensor simulation thread
    sim_thread = threading.Thread(target=sensor_simulation_loop, daemon=True, name="SensorSimulator")
    sim_thread.start()
    print("✓ IoT Sensor Telemetry simulation daemon started (3-second loop).")

    # Start HTTP server
    # Allow port reuse to avoid 'Address already in use' during quick reboots
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), LoopYardRequestHandler) as httpd:
        print(f"✓ LoopYard server running at: http://localhost:{PORT}")
        print("  Zero external dependencies. Press Ctrl+C to stop.")
        print("-" * 65)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down LoopYard server.")
            httpd.server_close()

if __name__ == "__main__":
    start_server()
