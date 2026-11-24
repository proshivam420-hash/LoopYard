"""
database.py - SQLite Data Model and Operations for LoopYard MVP
Implements the 3 normalized tables: tenants, bins, pickups.
Zero external dependencies (uses standard library sqlite3 and json).
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loopyard.db")

# Conversion factors for estimated CO2 emissions avoided (kg CO2e per kg material diverted)
CO2_AVOIDANCE_FACTORS = {
    "metal": 2.1,
    "plastic": 1.5,
    "cardboard": 1.2,
    "oil": 1.8,
    "solvent": 1.6,
    "organic": 0.5,
    "mixed": 0.0  # Landfilled, 0 avoidance
}

HAZARDOUS_TYPES = {"solvent", "oil"}

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_reseed=False):
    """Create tables and seed initial data if empty or forced."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            zone TEXT NOT NULL,
            needs TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant TEXT NOT NULL,
            waste_type TEXT NOT NULL,
            fill_pct REAL NOT NULL DEFAULT 0.0,
            capacity_kg REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pickups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bin INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            created_time TEXT NOT NULL,
            done_time TEXT,
            kg_collected REAL,
            FOREIGN KEY (bin) REFERENCES bins(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS demo_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            scope TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()

    # Check if seeding is required
    cursor.execute("SELECT COUNT(*) FROM tenants")
    tenant_count = cursor.fetchone()[0]

    if tenant_count == 0 or force_reseed:
        if force_reseed:
            cursor.execute("DELETE FROM pickups")
            cursor.execute("DELETE FROM bins")
            cursor.execute("DELETE FROM tenants")
            cursor.execute("DELETE FROM demo_users")
            try:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('pickups', 'bins', 'tenants', 'demo_users')")
            except sqlite3.OperationalError:
                pass
            conn.commit()
        seed_data(conn)

    conn.close()

def seed_data(conn):
    """Seed initial 6 tenants and 11 smart bins across varied waste types, plus baseline compliance log."""
    cursor = conn.cursor()

    tenants = [
        ("AutoParts Co", "Zone A", json.dumps(["metal", "plastic"])),
        ("SteelWorks Ltd", "Zone A", json.dumps(["metal"])),
        ("EcoPack Solutions", "Zone B", json.dumps(["cardboard", "plastic"])),
        ("ChemClean Refining", "Zone B", json.dumps(["oil", "solvent"])),
        ("GreenAgro Organics", "Zone C", json.dumps(["organic"])),
        ("PolymerTech Industries", "Zone C", json.dumps(["plastic", "solvent"]))
    ]

    cursor.executemany("INSERT INTO tenants (name, zone, needs) VALUES (?, ?, ?)", tenants)

    # 11 smart bins across all categories
    bins = [
        ("AutoParts Co", "metal", 45.0, 500.0),       # Bin 1
        ("AutoParts Co", "oil", 60.0, 200.0),         # Bin 2 (Hazardous)
        ("SteelWorks Ltd", "metal", 35.0, 1000.0),    # Bin 3
        ("SteelWorks Ltd", "solvent", 72.0, 150.0),   # Bin 4 (Hazardous)
        ("EcoPack Solutions", "cardboard", 50.0, 400.0), # Bin 5
        ("EcoPack Solutions", "mixed", 20.0, 300.0),  # Bin 6 (Landfill stream)
        ("ChemClean Refining", "solvent", 75.0, 250.0), # Bin 7 (Hazardous)
        ("ChemClean Refining", "oil", 40.0, 350.0),   # Bin 8 (Hazardous)
        ("GreenAgro Organics", "organic", 55.0, 600.0), # Bin 9
        ("GreenAgro Organics", "cardboard", 30.0, 200.0), # Bin 10
        ("PolymerTech Industries", "plastic", 65.0, 450.0) # Bin 11
    ]

    cursor.executemany(
        "INSERT INTO bins (tenant, waste_type, fill_pct, capacity_kg) VALUES (?, ?, ?, ?)",
        bins
    )

    # Seed realistic baseline compliance log records so metrics are meaningful immediately
    now = datetime.now()
    t_2h_ago = (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    t_4h_ago = (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
    t_6h_ago = (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
    t_8h_ago = (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    t_1d_ago = (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    historical_pickups = [
        (1, "done", (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"), t_2h_ago, 420.0),
        (4, "done", (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"), t_4h_ago, 135.0),
        (5, "done", (now - timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"), t_6h_ago, 360.0),
        (6, "done", (now - timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S"), t_8h_ago, 210.0),
        (8, "done", (now - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M:%S"), t_1d_ago, 280.0)
    ]

    cursor.executemany(
        "INSERT INTO pickups (bin, status, created_time, done_time, kg_collected) VALUES (?, ?, ?, ?, ?)",
        historical_pickups
    )

    demo_users = [
        ("Elena Vance", "Park Manager", "Park-Wide Administration", now.strftime("%Y-%m-%d %H:%M:%S")),
        ("Marcus Chen", "Collector", "Truck #04 · Zones A & B Express", now.strftime("%Y-%m-%d %H:%M:%S")),
        ("Priya Sharma", "Tenant", "AutoParts Co", now.strftime("%Y-%m-%d %H:%M:%S"))
    ]

    cursor.executemany(
        "INSERT INTO demo_users (name, role, scope, created_at) VALUES (?, ?, ?, ?)",
        demo_users
    )

    conn.commit()

def get_all_tenants():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, zone, needs FROM tenants ORDER BY id ASC")
    rows = cursor.fetchall()
    tenants = []
    for r in rows:
        needs_list = json.loads(r["needs"]) if r["needs"] else []
        tenants.append({
            "id": r["id"],
            "name": r["name"],
            "zone": r["zone"],
            "needs": needs_list
        })
    conn.close()
    return tenants

def get_all_bins():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, b.tenant, b.waste_type, b.fill_pct, b.capacity_kg, t.zone,
               ROUND((b.fill_pct / 100.0) * b.capacity_kg, 1) as current_kg,
               CASE WHEN b.waste_type IN ('solvent', 'oil') THEN 1 ELSE 0 END as is_hazardous
        FROM bins b
        LEFT JOIN tenants t ON b.tenant = t.name
        ORDER BY b.id ASC
    """)
    rows = cursor.fetchall()
    bins = [dict(r) for r in rows]
    conn.close()
    return bins

def get_priority_pickups():
    """
    Priority Queue: Hazardous waste pickups (solvent and oil) are automatically
    sorted to the top of the dispatch queue, followed by standard tasks ordered
    from oldest to newest.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.bin as bin_id, p.status, p.created_time, p.done_time, p.kg_collected,
               b.tenant, b.waste_type, b.fill_pct, b.capacity_kg,
               ROUND((b.fill_pct / 100.0) * b.capacity_kg, 1) as current_kg,
               CASE WHEN b.waste_type IN ('solvent', 'oil') THEN 1 ELSE 0 END as is_hazardous
        FROM pickups p
        JOIN bins b ON p.bin = b.id
        WHERE p.status = 'open'
        ORDER BY
            is_hazardous DESC,
            p.created_time ASC
    """)
    rows = cursor.fetchall()
    pickups = [dict(r) for r in rows]
    conn.close()
    return pickups

def get_compliance_log():
    """
    Hazardous Waste & Compliance Log: Every completed pickup is permanently recorded
    with timestamp, tenant name, waste type, and collected weight (kg).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.bin as bin_id, p.status, p.created_time, p.done_time, p.kg_collected,
               b.tenant, b.waste_type,
               CASE WHEN b.waste_type IN ('solvent', 'oil') THEN 1 ELSE 0 END as is_hazardous
        FROM pickups p
        JOIN bins b ON p.bin = b.id
        WHERE p.status = 'done'
        ORDER BY p.done_time DESC, p.id DESC
    """)
    rows = cursor.fetchall()
    log = [dict(r) for r in rows]
    conn.close()
    return log

def get_reuse_matches():
    """
    Industrial Symbiosis Matching Rule:
    A reuse match is displayed whenever a bin's waste_type appears in another tenant's
    needs list AND that bin's current fill level is at least >= 30%.
    """
    tenants = get_all_tenants()
    bins = get_all_bins()

    matches = []
    for b in bins:
        if b["fill_pct"] >= 30.0:
            for t in tenants:
                # Rule: "another tenant's needs list" (not the bin owner itself)
                if t["name"] != b["tenant"] and b["waste_type"] in t["needs"]:
                    current_kg = round((b["fill_pct"] / 100.0) * b["capacity_kg"], 1)
                    matches.append({
                        "bin_id": b["id"],
                        "waste_type": b["waste_type"],
                        "fill_pct": b["fill_pct"],
                        "available_kg": current_kg,
                        "source_tenant": b["tenant"],
                        "source_zone": b.get("zone", "Zone A"),
                        "target_tenant": t["name"],
                        "target_zone": t["zone"],
                        "narrative": f"{b['tenant']} has {int(current_kg) if current_kg.is_integer() else current_kg} kg of {b['waste_type']}, {t['name']} needs it"
                    })
    # Sort matches by available weight descending
    matches.sort(key=lambda m: m["available_kg"], reverse=True)
    return matches

def get_impact_metrics():
    """
    Real-time calculation and display of:
    1. total kilograms collected
    2. overall diversion rate (percentage of waste diverted from landfill: every type except mixed)
    3. estimated CO2 emissions avoided
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.kg_collected, b.waste_type
        FROM pickups p
        JOIN bins b ON p.bin = b.id
        WHERE p.status = 'done' AND p.kg_collected IS NOT NULL
    """)
    rows = cursor.fetchall()
    conn.close()

    total_kg = 0.0
    diverted_kg = 0.0
    landfill_kg = 0.0
    co2_avoided_kg = 0.0

    by_category = {}

    for r in rows:
        kg = float(r["kg_collected"])
        w_type = r["waste_type"]
        total_kg += kg

        if w_type not in by_category:
            by_category[w_type] = {"kg": 0.0, "co2": 0.0}
        by_category[w_type]["kg"] += kg

        factor = CO2_AVOIDANCE_FACTORS.get(w_type, 0.0)
        avoided = kg * factor
        co2_avoided_kg += avoided
        by_category[w_type]["co2"] += avoided

        # Diversion Rate: every type except mixed is considered diverted from landfill
        if w_type != "mixed":
            diverted_kg += kg
        else:
            landfill_kg += kg

    diversion_rate = (diverted_kg / total_kg * 100.0) if total_kg > 0 else 0.0

    return {
        "total_kg_collected": round(total_kg, 1),
        "diverted_kg": round(diverted_kg, 1),
        "landfill_kg": round(landfill_kg, 1),
        "diversion_rate_pct": round(diversion_rate, 1),
        "co2_avoided_kg": round(co2_avoided_kg, 1),
        "by_category": by_category,
        "co2_factors": CO2_AVOIDANCE_FACTORS
    }

def dump_waste_into_bin(bin_id, amount_pct=25.0):
    """
    Adds +25% fill to target bin on demand.
    Applies Auto-Alert & Pickup Creation Rule if fill reaches >= 80%.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, tenant, waste_type, fill_pct, capacity_kg FROM bins WHERE id = ?", (bin_id,))
    b = cursor.fetchone()
    if not b:
        conn.close()
        return None

    new_fill = min(100.0, b["fill_pct"] + amount_pct)
    cursor.execute("UPDATE bins SET fill_pct = ? WHERE id = ?", (new_fill, bin_id))

    pickup_created = False
    # Auto-Alert & Pickup Creation Rule:
    # Whenever a bin's fill level reaches >= 80% AND there is currently no open pickup linked to that bin,
    # the system automatically inserts a new pickup record with status open and the current timestamp.
    if new_fill >= 80.0:
        cursor.execute("SELECT id FROM pickups WHERE bin = ? AND status = 'open'", (bin_id,))
        existing = cursor.fetchone()
        if not existing:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO pickups (bin, status, created_time) VALUES (?, 'open', ?)",
                (bin_id, now_str)
            )
            pickup_created = True

    conn.commit()
    conn.close()

    return {
        "bin_id": bin_id,
        "new_fill_pct": new_fill,
        "pickup_created": pickup_created
    }

def partial_collect_bin(bin_id, remove_pct=25.0):
    """
    Partial Collection / Remove Dump Percentage:
    - Clamp to available fill: actual_removed_pct = min(bin.fill_pct, remove_pct)
    - Calculate collected weight: collected_kg = round((actual_removed_pct / 100.0) * bin.capacity_kg, 1)
    - Update bin fill: bin.fill_pct = round(max(0.0, bin.fill_pct - actual_removed_pct), 1)
    - Record completed entry in pickups / Compliance Audit Trail
    - Auto-Resolve Open Pickup if Below 80% Threshold
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, tenant, waste_type, fill_pct, capacity_kg FROM bins WHERE id = ?", (bin_id,))
    b = cursor.fetchone()
    if not b:
        conn.close()
        return None

    current_fill = float(b["fill_pct"])
    capacity_kg = float(b["capacity_kg"])
    actual_removed_pct = min(current_fill, float(remove_pct))

    if actual_removed_pct <= 0:
        conn.close()
        return {
            "bin_id": bin_id,
            "actual_removed_pct": 0,
            "collected_kg": 0.0,
            "new_fill_pct": current_fill,
            "message": "Bin is already empty."
        }

    collected_kg = round((actual_removed_pct / 100.0) * capacity_kg, 1)
    new_fill_pct = round(max(0.0, current_fill - actual_removed_pct), 1)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update bin fill level
    cursor.execute("UPDATE bins SET fill_pct = ? WHERE id = ?", (new_fill_pct, bin_id))

    # Check for open pickup
    cursor.execute("SELECT id, created_time FROM pickups WHERE bin = ? AND status = 'open'", (bin_id,))
    open_pickup = cursor.fetchone()

    pickup_id = None
    if open_pickup and new_fill_pct < 80.0:
        # Resolve the open pickup directly into compliance log
        pickup_id = open_pickup["id"]
        cursor.execute("""
            UPDATE pickups
            SET status = 'done', done_time = ?, kg_collected = ?
            WHERE id = ?
        """, (now_str, collected_kg, pickup_id))
    else:
        # Insert a completed pickup record for this partial collection
        cursor.execute("""
            INSERT INTO pickups (bin, status, created_time, done_time, kg_collected)
            VALUES (?, 'done', ?, ?, ?)
        """, (bin_id, now_str, now_str, collected_kg))
        pickup_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "bin_id": bin_id,
        "tenant": b["tenant"],
        "waste_type": b["waste_type"],
        "actual_removed_pct": actual_removed_pct,
        "new_fill_pct": new_fill_pct,
        "collected_kg": collected_kg,
        "done_time": now_str,
        "pickup_id": pickup_id
    }

def complete_pickup(pickup_id):
    """
    Pickup Completion Rule:
    When a collector marks a pickup done, the system calculates
    kg_collected = (fill_pct / 100) * capacity_kg, records done_time,
    sets status to done, and resets the associated bin's fill_pct to 0%.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.bin, p.status, b.fill_pct, b.capacity_kg, b.tenant, b.waste_type
        FROM pickups p
        JOIN bins b ON p.bin = b.id
        WHERE p.id = ?
    """, (pickup_id,))
    p = cursor.fetchone()

    if not p or p["status"] != "open":
        conn.close()
        return None

    bin_id = p["bin"]
    fill_pct = p["fill_pct"]
    capacity_kg = p["capacity_kg"]

    kg_collected = round((fill_pct / 100.0) * capacity_kg, 1)
    done_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update pickup to done
    cursor.execute("""
        UPDATE pickups
        SET status = 'done', done_time = ?, kg_collected = ?
        WHERE id = ?
    """, (done_time_str, kg_collected, pickup_id))

    # Reset bin's fill_pct to 0%
    cursor.execute("UPDATE bins SET fill_pct = 0.0 WHERE id = ?", (bin_id,))

    conn.commit()
    conn.close()

    return {
        "pickup_id": pickup_id,
        "bin_id": bin_id,
        "tenant": p["tenant"],
        "waste_type": p["waste_type"],
        "kg_collected": kg_collected,
        "done_time": done_time_str
    }

def step_simulation_tick():
    """
    Sensor Simulation Loop: Every 3 seconds, a background worker thread increments
    the fill percentage of each bin at a waste-type-specific fill rate (capped at 100%).
    Triggers automatic pickup creation at >= 80% fill.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Fill rate per 3 seconds by waste type (% increments)
    fill_rates = {
        "cardboard": 1.2,
        "organic": 1.5,
        "metal": 0.8,
        "plastic": 1.1,
        "mixed": 1.0,
        "oil": 0.7,
        "solvent": 0.6
    }

    cursor.execute("SELECT id, waste_type, fill_pct FROM bins")
    bins = cursor.fetchall()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alerts_created = 0

    for b in bins:
        b_id = b["id"]
        w_type = b["waste_type"]
        current_fill = b["fill_pct"]

        increment = fill_rates.get(w_type, 1.0)
        new_fill = min(100.0, round(current_fill + increment, 2))

        cursor.execute("UPDATE bins SET fill_pct = ? WHERE id = ?", (new_fill, b_id))

        # Check pickup creation rule: >= 80% AND no open pickup
        if new_fill >= 80.0:
            cursor.execute("SELECT id FROM pickups WHERE bin = ? AND status = 'open'", (b_id,))
            has_open = cursor.fetchone()
            if not has_open:
                cursor.execute(
                    "INSERT INTO pickups (bin, status, created_time) VALUES (?, 'open', ?)",
                    (b_id, now_str)
                )
                alerts_created += 1

    conn.commit()
    conn.close()
    return alerts_created

def get_all_demo_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, role, scope, created_at FROM demo_users ORDER BY id ASC")
    rows = cursor.fetchall()
    users = [dict(r) for r in rows]
    conn.close()
    return users

def create_demo_user(name, role, scope):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO demo_users (name, role, scope, created_at) VALUES (?, ?, ?, ?)", (name, role, scope, now_str))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {
        "id": new_id,
        "name": name,
        "role": role,
        "scope": scope,
        "created_at": now_str
    }

def get_full_system_state():
    """Returns the full aggregated state for the unified dashboard."""
    return {
        "tenants": get_all_tenants(),
        "bins": get_all_bins(),
        "priority_pickups": get_priority_pickups(),
        "compliance_log": get_compliance_log(),
        "reuse_matches": get_reuse_matches(),
        "impact_metrics": get_impact_metrics(),
        "demo_users": get_all_demo_users(),
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
