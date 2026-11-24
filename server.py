import json
import os
import random
import sqlite3
import threading
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loopyard.db")
HOST = "0.0.0.0"
PORT = 8000

HAZARDOUS_TYPES = {"solvent", "oil"}
FILL_SPEEDS = {
    "solvent": 1.6,
    "oil": 1.4,
    "metal": 1.2,
    "plastic": 1.5,
    "cardboard": 1.7,
    "organic": 1.8,
    "mixed": 1.3,
}
CO2_FACTORS = {
    "metal": 1.8,
    "plastic": 1.5,
    "cardboard": 1.1,
    "oil": 1.2,
    "solvent": 1.4,
    "organic": 0.6,
    "mixed": 0.1,
}

db_lock = threading.Lock()
sim_paused = False


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset=False):
    global sim_paused
    with db_lock:
        if reset and os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        conn = get_conn()
        cur = conn.cursor()

        # Check if legacy table exists without bin_id
        try:
            cols = [c[1] for c in cur.execute("PRAGMA table_info(pickups)").fetchall()]
            if cols and "bin_id" not in cols:
                cur.execute("DROP TABLE IF EXISTS pickups")
                cur.execute("DROP TABLE IF EXISTS bins")
                cur.execute("DROP TABLE IF EXISTS tenants")
                cur.execute("DROP TABLE IF EXISTS demo_users")
        except Exception:
            pass

        cur.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                zone TEXT NOT NULL,
                needs_json TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS bins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                tenant_id INTEGER NOT NULL,
                waste_type TEXT NOT NULL,
                fill_pct REAL NOT NULL,
                capacity_kg REAL NOT NULL,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS pickups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bin_id INTEGER NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('open', 'done')),
                created_at TEXT NOT NULL,
                done_at TEXT,
                kg_collected REAL NOT NULL DEFAULT 0.0,
                actor_name TEXT,
                note TEXT,
                FOREIGN KEY (bin_id) REFERENCES bins(id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS demo_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('park_manager', 'collector', 'tenant')),
                scope_label TEXT NOT NULL,
                tenant_id INTEGER,
                created_at TEXT NOT NULL
            )
        """)

        if cur.execute("SELECT COUNT(*) FROM tenants").fetchone()[0] == 0:
            tenants_seed = [
                ("AutoParts Co", "Zone A", ["metal", "oil"]),
                ("SteelWorks Ltd", "Zone A", ["metal", "solvent"]),
                ("ChemClean Refining", "Zone B", ["solvent", "oil"]),
                ("EcoPack Solutions", "Zone B", ["cardboard", "plastic"]),
                ("GreenAgro Organics", "Zone C", ["organic", "cardboard"]),
                ("PolymerTech Industries", "Zone C", ["plastic", "solvent"]),
            ]
            cur.executemany(
                "INSERT INTO tenants (name, zone, needs_json) VALUES (?, ?, ?)",
                [(n, z, json.dumps(needs)) for n, z, needs in tenants_seed],
            )

            t_rows = {r["name"]: r["id"] for r in cur.execute("SELECT id, name FROM tenants")}
            bins_seed = [
                ("Bin #1", t_rows["AutoParts Co"], "metal", 46.0, 500.0),
                ("Bin #2", t_rows["AutoParts Co"], "oil", 64.0, 200.0),
                ("Bin #3", t_rows["SteelWorks Ltd"], "metal", 42.0, 1000.0),
                ("Bin #4", t_rows["SteelWorks Ltd"], "solvent", 74.0, 150.0),
                ("Bin #5", t_rows["EcoPack Solutions"], "cardboard", 52.0, 400.0),
                ("Bin #6", t_rows["EcoPack Solutions"], "mixed", 26.0, 300.0),
                ("Bin #7", t_rows["ChemClean Refining"], "solvent", 78.0, 250.0),
                ("Bin #8", t_rows["ChemClean Refining"], "oil", 44.0, 350.0),
                ("Bin #9", t_rows["GreenAgro Organics"], "organic", 61.0, 600.0),
                ("Bin #10", t_rows["GreenAgro Organics"], "cardboard", 38.0, 200.0),
                ("Bin #11", t_rows["PolymerTech Industries"], "plastic", 54.0, 450.0),
            ]
            cur.executemany(
                "INSERT INTO bins (label, tenant_id, waste_type, fill_pct, capacity_kg) VALUES (?, ?, ?, ?, ?)",
                bins_seed,
            )

            b_rows = {r["label"]: r["id"] for r in cur.execute("SELECT id, label FROM bins")}
            initial_done = [
                (b_rows["Bin #1"], "done", "2026-11-24 18:10:00", "2026-11-24 18:35:00", 420.0, "Marcus Chen", "Symbiosis transfer → SteelWorks Ltd"),
                (b_rows["Bin #4"], "done", "2026-11-24 18:45:00", "2026-11-24 19:05:00", 135.0, "Marcus Chen", "Hazardous full pickup"),
                (b_rows["Bin #5"], "done", "2026-11-24 19:15:00", "2026-11-24 19:40:00", 360.0, "Marcus Chen", "Symbiosis transfer → GreenAgro Organics"),
                (b_rows["Bin #6"], "done", "2026-11-24 19:50:00", "2026-11-24 20:15:00", 210.0, "Marcus Chen", "Mixed landfill run"),
                (b_rows["Bin #9"], "done", "2026-11-24 20:20:00", "2026-11-24 20:45:00", 280.0, "Marcus Chen", "Full pickup (100%)"),
            ]
            cur.executemany(
                """INSERT INTO pickups (bin_id, status, created_at, done_at, kg_collected, actor_name, note)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                initial_done,
            )

            users_seed = [
                ("Ananya Verma", "park_manager", "All Zones (Park-Wide)", None, now_str()),
                ("Marcus Chen", "collector", "Truck #04 · Zones A, B & C", None, now_str()),
                ("Priya Sharma", "tenant", "AutoParts Co (Zone A)", t_rows["AutoParts Co"], now_str()),
            ]
            cur.executemany(
                "INSERT INTO demo_users (name, role, scope_label, tenant_id, created_at) VALUES (?, ?, ?, ?, ?)",
                users_seed,
            )

        sim_paused = False
        conn.commit()
        conn.close()


def ensure_open_pickup_for_high_bins(conn):
    cur = conn.cursor()
    bins = cur.execute("SELECT id, fill_pct FROM bins WHERE fill_pct >= 80.0").fetchall()
    ts = now_str()
    for b in bins:
        open_exists = cur.execute(
            "SELECT 1 FROM pickups WHERE bin_id = ? AND status = 'open' LIMIT 1",
            (b["id"],),
        ).fetchone()
        if not open_exists:
            cur.execute(
                """INSERT INTO pickups (bin_id, status, created_at, kg_collected, note)
                   VALUES (?, 'open', ?, 0.0, 'Auto-dispatched at >=80% fill')""",
                (b["id"], ts),
            )


def sensor_tick_locked(conn):
    cur = conn.cursor()
    bins = cur.execute("SELECT id, waste_type, fill_pct FROM bins").fetchall()
    for b in bins:
        wtype = b["waste_type"]
        base = FILL_SPEEDS.get(wtype, 1.3)
        delta = round(random.uniform(base * 0.4, base * 1.4), 1)
        new_fill = min(100.0, round(float(b["fill_pct"]) + delta, 1))
        cur.execute("UPDATE bins SET fill_pct = ? WHERE id = ?", (new_fill, b["id"]))
    ensure_open_pickup_for_high_bins(conn)
    conn.commit()


def sensor_loop():
    while True:
        time.sleep(3)
        if sim_paused:
            continue
        try:
            with db_lock:
                conn = get_conn()
                sensor_tick_locked(conn)
                conn.close()
        except Exception as exc:
            print("Sensor tick error:", exc)


def build_state():
    with db_lock:
        conn = get_conn()
        ensure_open_pickup_for_high_bins(conn)
        conn.commit()

        tenants_raw = conn.execute("SELECT id, name, zone, needs_json FROM tenants ORDER BY id").fetchall()
        tenants = []
        for t in tenants_raw:
            needs = json.loads(t["needs_json"])
            tenants.append({"id": t["id"], "name": t["name"], "zone": t["zone"], "needs": needs})

        bins_raw = conn.execute(
            """SELECT b.id, b.label, b.tenant_id, b.waste_type, b.fill_pct, b.capacity_kg,
                      t.name AS tenant_name, t.zone AS zone
               FROM bins b JOIN tenants t ON b.tenant_id = t.id ORDER BY b.id"""
        ).fetchall()
        bins = []
        for b in bins_raw:
            fill_pct = round(float(b["fill_pct"]), 1)
            cap = float(b["capacity_kg"])
            est_kg = round((fill_pct / 100.0) * cap, 1)
            bins.append({
                "id": b["id"],
                "label": b["label"],
                "tenant_id": b["tenant_id"],
                "tenant_name": b["tenant_name"],
                "zone": b["zone"],
                "waste_type": b["waste_type"],
                "fill_pct": fill_pct,
                "capacity_kg": cap,
                "est_kg": est_kg,
                "is_hazardous": b["waste_type"] in HAZARDOUS_TYPES,
            })

        open_raw = conn.execute(
            """SELECT p.id, p.bin_id, p.created_at, p.note,
                      b.label AS bin_label, b.waste_type, b.fill_pct, b.capacity_kg,
                      t.id AS tenant_id, t.name AS tenant_name, t.zone
               FROM pickups p
               JOIN bins b ON p.bin_id = b.id
               JOIN tenants t ON b.tenant_id = t.id
               WHERE p.status = 'open'"""
        ).fetchall()

        open_pickups = []
        for r in open_raw:
            is_haz = r["waste_type"] in HAZARDOUS_TYPES
            est_kg = round((float(r["fill_pct"]) / 100.0) * float(r["capacity_kg"]), 1)
            open_pickups.append({
                "id": r["id"],
                "bin_id": r["bin_id"],
                "bin_label": r["bin_label"],
                "tenant_id": r["tenant_id"],
                "tenant_name": r["tenant_name"],
                "zone": r["zone"],
                "waste_type": r["waste_type"],
                "fill_pct": round(float(r["fill_pct"]), 1),
                "est_kg": est_kg,
                "is_hazardous": is_haz,
                "priority_rank": 1 if is_haz else 2,
                "created_at": r["created_at"],
                "note": r["note"] or "",
            })

        open_pickups.sort(key=lambda x: (x["priority_rank"], x["created_at"], x["id"]))

        done_raw = conn.execute(
            """SELECT p.id, p.bin_id, p.created_at, p.done_at, p.kg_collected, p.actor_name, p.note,
                      b.label AS bin_label, b.waste_type,
                      t.id AS tenant_id, t.name AS tenant_name, t.zone
               FROM pickups p
               JOIN bins b ON p.bin_id = b.id
               JOIN tenants t ON b.tenant_id = t.id
               WHERE p.status = 'done'
               ORDER BY p.id DESC"""
        ).fetchall()

        completed_log = []
        total_kg = 0.0
        diverted_kg = 0.0
        landfill_kg = 0.0
        co2_avoided_kg = 0.0

        for r in done_raw:
            kg = round(float(r["kg_collected"]), 1)
            wtype = r["waste_type"]
            total_kg = round(total_kg + kg, 1)
            if wtype == "mixed":
                landfill_kg = round(landfill_kg + kg, 1)
            else:
                diverted_kg = round(diverted_kg + kg, 1)
            factor = CO2_FACTORS.get(wtype, 0.5)
            co2_avoided_kg = round(co2_avoided_kg + (kg * factor), 1)

            completed_log.append({
                "id": r["id"],
                "bin_id": r["bin_id"],
                "bin_label": r["bin_label"],
                "tenant_id": r["tenant_id"],
                "tenant_name": r["tenant_name"],
                "zone": r["zone"],
                "waste_type": wtype,
                "kg_collected": kg,
                "created_at": r["created_at"],
                "done_at": r["done_at"],
                "actor_name": r["actor_name"] or "Collector",
                "note": r["note"] or "",
            })

        diversion_rate = round((diverted_kg / total_kg) * 100.0, 1) if total_kg > 0 else 0.0

        matches = []
        for b in bins:
            if b["fill_pct"] >= 30.0 and b["est_kg"] > 0:
                for t in tenants:
                    if t["id"] != b["tenant_id"] and b["waste_type"] in t["needs"]:
                        matches.append({
                            "source_tenant_id": b["tenant_id"],
                            "source_tenant": b["tenant_name"],
                            "source_zone": b["zone"],
                            "bin_id": b["id"],
                            "bin_label": b["label"],
                            "waste_type": b["waste_type"],
                            "fill_pct": b["fill_pct"],
                            "available_kg": b["est_kg"],
                            "target_tenant_id": t["id"],
                            "target_tenant": t["name"],
                            "target_zone": t["zone"],
                        })
        matches.sort(key=lambda m: (-m["available_kg"], m["source_tenant"]))

        demo_users = [
            dict(u) for u in conn.execute(
                "SELECT id, name, role, scope_label, tenant_id, created_at FROM demo_users ORDER BY id"
            ).fetchall()
        ]

        conn.close()

        haz_open = sum(1 for p in open_pickups if p["is_hazardous"])
        std_open = len(open_pickups) - haz_open

        return {
            "paused": sim_paused,
            "server_time": now_str(),
            "stats": {
                "total_kg": total_kg,
                "diverted_kg": diverted_kg,
                "landfill_kg": landfill_kg,
                "diversion_rate": diversion_rate,
                "co2_avoided_kg": co2_avoided_kg,
                "open_pickups_count": len(open_pickups),
                "haz_pickups_count": haz_open,
                "std_pickups_count": std_open,
            },
            "tenants": tenants,
            "bins": bins,
            "open_pickups": open_pickups,
            "completed_log": completed_log,
            "matches": matches,
            "demo_users": demo_users,
        }


def complete_pickup_action(pickup_id=None, bin_id=None, percent=None, actor_name="Collector", custom_note=None):
    with db_lock:
        conn = get_conn()
        cur = conn.cursor()

        if pickup_id is not None:
            p = cur.execute("SELECT * FROM pickups WHERE id = ? AND status = 'open'", (pickup_id,)).fetchone()
            if not p:
                conn.close()
                return {"ok": False, "error": "Open pickup not found"}
            target_bin_id = p["bin_id"]
            open_pickup_id = p["id"]
        elif bin_id is not None:
            target_bin_id = bin_id
            open_row = cur.execute(
                "SELECT id FROM pickups WHERE bin_id = ? AND status = 'open' ORDER BY id ASC LIMIT 1",
                (target_bin_id,),
            ).fetchone()
            open_pickup_id = open_row["id"] if open_row else None
        else:
            conn.close()
            return {"ok": False, "error": "pickup_id or bin_id required"}

        b = cur.execute("SELECT * FROM bins WHERE id = ?", (target_bin_id,)).fetchone()
        if not b:
            conn.close()
            return {"ok": False, "error": "Bin not found"}

        current_fill = float(b["fill_pct"])
        cap = float(b["capacity_kg"])
        ts = now_str()

        if percent is not None:
            pct = max(1.0, min(100.0, float(percent)))
            removed_pct = min(current_fill, pct)
            if removed_pct <= 0:
                conn.close()
                return {"ok": False, "error": "Bin is already empty"}
            kg_collected = round((removed_pct / 100.0) * cap, 1)
            new_fill = round(max(0.0, current_fill - removed_pct), 1)
            note = custom_note or f"Partial removal (-{removed_pct:.0f}%)"
            cur.execute("UPDATE bins SET fill_pct = ? WHERE id = ?", (new_fill, target_bin_id))

            if open_pickup_id is not None and new_fill < 80.0:
                cur.execute(
                    """UPDATE pickups
                       SET status = 'done', done_at = ?, kg_collected = ?, actor_name = ?, note = ?
                       WHERE id = ?""",
                    (ts, kg_collected, actor_name, f"{note}; fill <80%", open_pickup_id),
                )
            else:
                cur.execute(
                    """INSERT INTO pickups (bin_id, status, created_at, done_at, kg_collected, actor_name, note)
                       VALUES (?, 'done', ?, ?, ?, ?, ?)""",
                    (target_bin_id, ts, ts, kg_collected, actor_name, note),
                )
        else:
            kg_collected = round((current_fill / 100.0) * cap, 1)
            cur.execute("UPDATE bins SET fill_pct = 0.0 WHERE id = ?", (target_bin_id,))
            note = custom_note or "Full pickup (100%)"
            if open_pickup_id is not None:
                cur.execute(
                    """UPDATE pickups
                       SET status = 'done', done_at = ?, kg_collected = ?, actor_name = ?, note = ?
                       WHERE id = ?""",
                    (ts, kg_collected, actor_name, note, open_pickup_id),
                )
            else:
                cur.execute(
                    """INSERT INTO pickups (bin_id, status, created_at, done_at, kg_collected, actor_name, note)
                       VALUES (?, 'done', ?, ?, ?, ?, ?)""",
                    (target_bin_id, ts, ts, kg_collected, actor_name, note),
                )

        conn.commit()
        conn.close()
    return {"ok": True, "kg_collected": kg_collected, "state": build_state()}


def transfer_symbiosis_action(bin_id, target_tenant_id, percent=100.0, actor_name="Symbiosis Router"):
    with db_lock:
        conn = get_conn()
        b = conn.execute(
            """SELECT b.*, t.name AS source_name
               FROM bins b JOIN tenants t ON b.tenant_id = t.id WHERE b.id = ?""",
            (bin_id,),
        ).fetchone()
        target = conn.execute("SELECT id, name, zone FROM tenants WHERE id = ?", (target_tenant_id,)).fetchone()
        conn.close()

    if not b or not target:
        return {"ok": False, "error": "Source bin or target factory not found"}

    pct = max(10.0, min(100.0, float(percent)))
    avail_pct = min(float(b["fill_pct"]), pct)
    if avail_pct <= 0:
        return {"ok": False, "error": "No waste available in source bin to transfer"}

    transferred_kg = round((avail_pct / 100.0) * float(b["capacity_kg"]), 1)
    note = f"Transferred {transferred_kg:.1f} kg {b['waste_type']} → {target['name']} for reuse"
    return complete_pickup_action(
        bin_id=int(bin_id),
        percent=avail_pct,
        actor_name=actor_name,
        custom_note=note,
    )


def dump_waste_action(bin_id, add_pct=25.0):
    with db_lock:
        conn = get_conn()
        cur = conn.cursor()
        b = cur.execute("SELECT * FROM bins WHERE id = ?", (bin_id,)).fetchone()
        if not b:
            conn.close()
            return {"ok": False, "error": "Bin not found"}
        new_fill = min(100.0, round(float(b["fill_pct"]) + float(add_pct), 1))
        cur.execute("UPDATE bins SET fill_pct = ? WHERE id = ?", (new_fill, bin_id))
        ensure_open_pickup_for_high_bins(conn)
        conn.commit()
        conn.close()
    return {"ok": True, "new_fill": new_fill, "state": build_state()}


def create_demo_user_action(name, role, scope_label=None, scope=None, tenant_id=None):
    name = (name or "").strip()
    raw_role = (role or "tenant").strip()
    role_norm = raw_role.lower().replace(" ", "_")
    if role_norm not in ("park_manager", "collector", "tenant"):
        role_norm = "tenant"
    if not name:
        return {"ok": False, "success": False, "error": "Name is required"}
    scope_val = (scope or scope_label or "").strip() or (
        "All Zones (Park-Wide)" if role_norm == "park_manager"
        else "Truck #05 · Express Route" if role_norm == "collector"
        else "Assigned Factory Tenant"
    )
    with db_lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO demo_users (name, role, scope_label, tenant_id, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, role_norm, scope_val, tenant_id, now_str()),
        )
        new_id = cur.lastrowid
        conn.commit()
        conn.close()
    user_dict = {
        "id": new_id,
        "name": name,
        "role": raw_role,
        "scope": scope_val,
        "scope_label": scope_val,
        "tenant_id": tenant_id
    }
    return {"ok": True, "success": True, "user_id": new_id, "user": user_dict, "state": build_state()}


class LoopYardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def _send_json(self, payload, status=200):
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/state":
            self._send_json(build_state())
            return
        if path == "/api/demo_users":
            conn = get_conn()
            raw_users = conn.execute("SELECT id, name, role, scope_label, tenant_id, created_at FROM demo_users ORDER BY id").fetchall()
            conn.close()
            role_map = {"park_manager": "Park Manager", "collector": "Collector", "tenant": "Tenant"}
            users = []
            for u in raw_users:
                d = dict(u)
                d["scope"] = d.get("scope_label", "")
                d["role"] = role_map.get(d["role"], d["role"])
                users.append(d)
            self._send_json({"ok": True, "success": True, "demo_users": users})
            return
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        global sim_paused
        path = self.path.split("?")[0]
        try:
            body = self._read_json()
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, status=400)
            return

        if path == "/api/dump":
            bin_id = body.get("bin_id")
            pct = float(body.get("percent", 25.0))
            if bin_id is None:
                self._send_json({"ok": False, "error": "bin_id required"}, status=400)
                return
            self._send_json(dump_waste_action(int(bin_id), pct))
            return

        if path == "/api/transfer":
            bin_id = body.get("bin_id")
            target_tenant_id = body.get("target_tenant_id")
            pct = float(body.get("percent", 100.0))
            actor_name = body.get("actor_name", "Symbiosis Router")
            if bin_id is None or target_tenant_id is None:
                self._send_json({"ok": False, "error": "bin_id and target_tenant_id required"}, status=400)
                return
            res = transfer_symbiosis_action(int(bin_id), int(target_tenant_id), pct, str(actor_name))
            self._send_json(res, status=200 if res.get("ok") else 400)
            return

        if path in ("/api/pickup", "/api/complete_pickup", "/api/partial_collect"):
            pickup_id = body.get("pickup_id")
            bin_id = body.get("bin_id")
            percent = body.get("percent")
            actor_name = body.get("actor_name", "Collector")
            res = complete_pickup_action(
                pickup_id=int(pickup_id) if pickup_id is not None else None,
                bin_id=int(bin_id) if bin_id is not None else None,
                percent=float(percent) if percent is not None else None,
                actor_name=str(actor_name),
            )
            self._send_json(res, status=200 if res.get("ok") else 400)
            return

        if path == "/api/toggle_pause":
            sim_paused = not sim_paused
            self._send_json({"ok": True, "paused": sim_paused, "state": build_state()})
            return

        if path == "/api/reset":
            init_db(reset=True)
            self._send_json({"ok": True, "state": build_state()})
            return

        if path == "/api/demo_users":
            res = create_demo_user_action(
                name=body.get("name"),
                role=body.get("role"),
                scope_label=body.get("scope_label"),
                scope=body.get("scope"),
                tenant_id=body.get("tenant_id"),
            )
            self._send_json(res, status=200 if res.get("ok") else 400)
            return

        self._send_json({"ok": False, "error": "Not found"}, status=404)

    def log_message(self, format, *args):
        return


LoopYardRequestHandler = LoopYardHandler
sensor_simulation_loop = sensor_loop


def main():
    init_db(reset=False)
    t = threading.Thread(target=sensor_loop, daemon=True)
    t.start()
    server = ThreadingHTTPServer((HOST, PORT), LoopYardHandler)
    print(f"LoopYard running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down LoopYard...")
        server.server_close()


if __name__ == "__main__":
    main()