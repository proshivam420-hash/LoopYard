<<<<<<< HEAD
# LoopYard: Closed-Loop Industrial Waste & Symbiosis OS

> **A circular waste platform and autonomous logistics operating system for gated industrial parks.**  
> Featuring simulated IoT telemetry, automated priority dispatch, industrial symbiosis cross-factory reuse matching, and certified hazardous compliance logs.

---

## 1. Executive Summary & Core Idea in One Line

> *"An industrial park has many factories, and each one throws away things that another factory could use. LoopYard tracks every waste bin, sends pickups at the right time, keeps hazardous waste records, and tells factories who nearby can reuse their waste."*

LoopYard transforms industrial parks from traditional linear "take-make-waste" polluters into connected, circular resource-sharing hubs. Instead of factories paying haulage fees to discard scrap, used solvents, waste oils, and packaging into landfills, LoopYard autonomously streams bin telemetry, matches byproduct outputs to neighboring factories' raw-material needs, dispatches pickups based on hazardous priority, and maintains an immutable compliance audit trail.

---

## 2. Why This Is Fundamentally Different

Traditional waste management systems fail in industrial settings because they are designed for the general public:

| Dimension | Legacy Citizen Complaint Apps | LoopYard Closed-Loop Industrial OS |
| :--- | :--- | :--- |
| **Operating Environment** | Open public streets; unverified complaints from random citizens. | **Closed gated industrial park** with registered factory tenants across zones (Zone A, B, C). |
| **Data Collection** | Manual user complaint forms; slow, subjective, and reactive. | **Autonomous IoT telemetry**: bins report fill percentages every 3 seconds without human intervention. |
| **Dispatch Logic** | First-in, first-out or manual admin review. | **Automated threshold dispatch ($\ge 80\%$)** with hazardous materials (`solvent`, `oil`) auto-sorted to top priority. |
| **Material Destination** | Municipal landfill or general dump. | **Industrial Symbiosis**: byproducts are matched directly to neighboring factories as raw inputs. |
| **Compliance & ESG** | Basic status flags ("Pending" / "Resolved"). | **Certified immutable audit trail** with exact weights, timestamps, and real-time $\text{CO}_2\text{e}$ avoidance calculations. |

---

## 3. Technology Stack

LoopYard features a **Zero-External-Dependency Backend** paired with a **Dual-Engine Frontend** that runs seamlessly both locally and as a static deployment on Vercel:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LOOPYARD SYSTEM TOPOLOGY                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   [ Live Smart Bins (11) ] ──(Every 3s)──► [ IoT Sensor Telemetry ]   │
│                                                     │                  │
│                                                     ▼                  │
│     ┌────────────────────────────────────────────────────────────┐     │
│     │            DUAL-ENGINE EXECUTION ARCHITECTURE              │     │
│     ├─────────────────────────────┬──────────────────────────────┤     │
│     │  Local / On-Premise Engine  │  Standalone Vercel Engine    │     │
│     │  • Python http.server (8000)│  • In-Browser Simulation     │     │
│     │  • Normalized SQLite (3 tbl)│  • LocalStorage Persistence  │     │
│     │  • Background Daemon Thread │  • Instant Hydration (No 0s) │     │
│     └─────────────────────────────┴──────────────────────────────┘     │
│                                   │                                    │
│         ┌─────────────────────────┴─────────────────────────┐          │
│         ▼                                                   ▼          │
│  [ Priority Dispatch Queue ]                        [ Symbiosis Engine ]│
│  (Hazardous P1 Pinned First)                       (Cross-Factory Match)│
│         │                                                   │          │
│         ▼                                                   ▼          │
│  [ Compliance Audit Trail ]                         [ Impact Metrics ] │
│  (Immutable Certified Log)                         (Diversion & CO2e)  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### Backend Layer
- **Language / Runtime:** Python 3 (Standard Library only — zero external packages, `no pip install required`).
- **Web Server:** `http.server` & `socketserver` serving REST API endpoints and static assets.
- **Database:** SQLite (`sqlite3`) with three normalized relational tables (`tenants`, `bins`, `pickups`).
- **Telemetry Simulator:** Multithreaded Python daemon thread (`threading.Thread`) ticking a 3-second loop.

### Frontend Layer
- **Architecture:** Single-Page Application (SPA) in Vanilla JavaScript, HTML5, and CSS3.
- **Visual Design System:** Inspired by Linear, Samsara, and Stripe Dashboard.
  - **High-Contrast Header:** Anchored in dark slate (`#0F172A`) with emerald logo and glowing status pill (`● Live · 3s`).
  - **Light Mode (Default):** Canvas `#F8FAFC`, Surface `#FFFFFF`, Border `#E2E8F0`, Text `#0F172A`.
  - **Dark Mode Toggle:** Zinc/Graphite palette (`#09090B` / `#121215` / `#27272A`), persistent in `localStorage`.
  - **Typography:** `Inter` for UI labels; `JetBrains Mono` for tabular metrics, task IDs, and weights.
- **Universal Static Hosting (Vercel Ready):** If `/api/state` is unreachable, the client automatically switches to an in-browser simulation loop without blank screens, maintaining state in `localStorage`.

---

## 4. How the Core Features Work

### 1. Smart Bin Telemetry (11 Bins Across 6 Tenants)
Bins track specific waste categories, maximum capacities (kg), and live fill percentages. In the 3-second simulation loop, bins increment according to material-specific fill rates:
- **Cardboard:** $+1.2\%$ / 3s
- **Organic Byproducts:** $+1.5\%$ / 3s
- **Plastic Scrap:** $+1.1\%$ / 3s
- **Mixed Landfill Waste:** $+1.0\%$ / 3s
- **Metal Offcuts:** $+0.8\%$ / 3s
- **Waste Oil (Hazardous):** $+0.7\%$ / 3s
- **Chemical Solvent (Hazardous):** $+0.6\%$ / 3s

### 2. Autonomous Alert & Dispatch Rule ($\ge 80\%$)
Whenever a bin reaches **$80\%$ fill or higher**, an autonomous dispatch record is created with status `'open'` without requiring any human manual entry.

### 3. Priority Dispatch Queue (Collector Driver View)
Open dispatch tasks are sorted by safety and regulatory urgency:
$$\text{ORDER BY } (\text{waste\_type IN ('solvent', 'oil')}) \text{ DESC}, \text{created\_time ASC}$$
- **P1 Hazardous Tasks** (`solvent`, `oil`) are pinned to the top with a rose tint and crimson accent.
- **P2 Standard Tasks** follow in chronological order (oldest to newest).

### 4. Certified Pickup Completion & Reset
When a collector clicks **"Mark Collected"**:
1. Calculates collected weight:
   $$\text{kg\_collected} = \left(\frac{\text{fill\_pct}}{100}\right) \times \text{capacity\_kg}$$
2. Sets `status = 'done'`, logs `done_time = datetime.now()`.
3. Resets the associated bin's fill level to **$0\%$**.
4. Appends to the **Hazardous Waste & Compliance Audit Trail**.

### 5. Industrial Symbiosis Matching Board
The circular engine scans all bins and cross-references active waste with neighboring factories' raw material needs. A match is displayed whenever:
$$\text{Bin fill level} \ge 30\% \quad \text{AND} \quad \text{waste\_type} \in \text{another tenant's needs}$$
*Example:* `"AutoParts Co has 225 kg of metal, SteelWorks Ltd needs it"` with a direct route badge (`Zone A → Zone A`).

### 6. Sustainability & Impact Metrics
- **Landfill Diversion Rate:** Percentage of waste diverted through recycling and symbiosis reuse (every category except `mixed`):
  $$\text{Diversion Rate} = \frac{\sum \text{kg}_{\text{non-mixed}}}{\sum \text{kg}_{\text{total}}} \times 100\%$$
- **Estimated $\text{CO}_2\text{e}$ Avoided:** Avoided emissions calculated using lifecycle factors:
  - Metal: $2.1\text{ kg CO}_2\text{e / kg}$
  - Waste Oil: $1.8\text{ kg CO}_2\text{e / kg}$
  - Chemical Solvent: $1.6\text{ kg CO}_2\text{e / kg}$
  - Plastic: $1.5\text{ kg CO}_2\text{e / kg}$
  - Cardboard: $1.2\text{ kg CO}_2\text{e / kg}$
  - Organic: $0.5\text{ kg CO}_2\text{e / kg}$
  - Mixed: $0.0\text{ kg CO}_2\text{e / kg}$ (landfilled)

### 7. Evaluator Persona Showcase & Fast Demo Sign-Up
Built specifically for live hackathon evaluation and investor pitches:
- **Pre-Seeded Operational Personas:**
  1. **Elena Vance (Park Manager):** Park-wide oversight of all 6 factories, 11 smart bins, diversion rate KPIs, and compliance ledger.
  2. **Marcus Chen (Collector / Logistics Driver):** Truck #04 Express route, real-time driver dispatch queue with hazardous priority sorting, partial offloading (`-25%`, `-50%`), and certified collection.
  3. **Priya Sharma (Tenant / AutoParts Co):** Dedicated factory portal automatically filtering sensor telemetry to AutoParts Co bins and highlighting direct incoming/outgoing industrial symbiosis exchanges.
- **Dynamic Role Adaptation:** Switching personas instantly filters bin lists, updates scope badges, and tailors the dashboard perspective.
- **Zero-Friction Demo Sign-Up:** Allows judges to register a custom pitch persona in $<10$ seconds using one-click presets (`Judge as Tenant - SteelWorks`, `Judge as Driver - Truck #02`, `Judge as Park Director`).
- **Honest Local Simulation:** Stored transparently in browser `localStorage` and synchronized with the SQLite database via REST API. Zero password friction or dummy auth screens.

---

## 5. Quickstart & How to Run

### Method A: Local Python Server (Recommended)

```bash
# 1. Navigate to the project directory
cd /Users/ishantverma/Desktop/kunj

# 2. Run the server
python3 server.py
```

Open your browser to:
**[http://localhost:8000](http://localhost:8000)**

### Method B: Deploy to Vercel (Static Hosting)

The repository includes `vercel.json` and a universal frontend engine:
1. Push this directory to a GitHub repository.
2. Import the repository in [Vercel](https://vercel.com).
3. Click **Deploy**.
4. The dashboard will immediately boot in standalone browser simulation mode with all baseline figures, live 3-second sensor polling, interactive dump buttons, and audit logging.

### Method C: Run Automated Test Suites

```bash
# Test all 7 PDR logic and calculation rules
python3 test_system.py

# Test all REST API endpoints
python3 test_api.py
```

---

## 6. REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/state` | Returns full dashboard state (tenants, bins, queue, log, matches, metrics, demo users). |
| `GET` | `/api/bins` | Returns array of 11 bins with current fill percentages and weights. |
| `GET` | `/api/pickups` | Returns open pickup tasks sorted by hazardous priority then oldest first. |
| `GET` | `/api/compliance` | Returns immutable compliance audit trail of completed pickups. |
| `GET` | `/api/matches` | Returns active cross-factory industrial symbiosis matches. |
| `GET` | `/api/impact` | Returns sustainability figures (total kg, diversion %, $\text{CO}_2\text{e}$ avoided). |
| `GET` | `/api/demo_users` | Returns list of registered evaluator demo users and personas. |
| `POST` | `/api/demo_users` | Body: `{"name": "...", "role": "...", "scope": "..."}`. Registers custom judge demo identity. |
| `POST` | `/api/bins/dump` | Body: `{"bin_id": 4, "amount_pct": 25.0}`. Adds +25% fill; triggers auto-dispatch if $\ge 80\%$. |
| `POST` | `/api/partial_collect` | Body: `{"bin_id": 1, "percent": 25.0}`. Partially offloads bin, auto-resolves task if $<80\%$, logs to audit trail. |
| `POST` | `/api/pickups/complete` | Body: `{"pickup_id": 1}`. Completes task, resets bin to 0%, appends to audit log. |
| `POST` | `/api/simulation/toggle` | Toggles sensor telemetry daemon (pause / resume). |
| `POST` | `/api/reset` | Reseeds database back to clean factory demo state. |

---

## 7. Relational Data Model (SQLite)

```sql
-- Registered Industrial Park Factories & Input Needs
CREATE TABLE tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    zone TEXT NOT NULL,
    needs TEXT NOT NULL  -- JSON array of required materials
);

-- Smart Bins Monitored via IoT Telemetry
CREATE TABLE bins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant TEXT NOT NULL,
    waste_type TEXT NOT NULL,  -- metal, plastic, cardboard, oil, solvent, organic, mixed
    fill_pct REAL NOT NULL DEFAULT 0.0,
    capacity_kg REAL NOT NULL
);

-- Autonomous Dispatch Queue & Historical Compliance Ledger
CREATE TABLE pickups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',  -- 'open' or 'done'
    created_time TEXT NOT NULL,
    done_time TEXT,
    kg_collected REAL,
    FOREIGN KEY (bin) REFERENCES bins(id)
);

-- Evaluator Personas & Live Pitch Sign-Ups
CREATE TABLE demo_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,   -- 'Park Manager', 'Collector', 'Tenant'
    scope TEXT NOT NULL,  -- Factory name, route/truck, or park-wide oversight
    created_at TEXT NOT NULL
);
```

---

## 8. Two-Minute Live Demonstration Walkthrough

Follow these 6 steps to demonstrate the complete circular lifecycle during evaluation:

1. **Step 1: System Overview**  
   Open `http://localhost:8000`. Show the 11 bins across 6 factories incrementing telemetry every 3 seconds alongside top-level KPIs.
2. **Step 2: Trigger Autonomous Alert**  
   Click the **`+25% Dump Waste`** button on a solvent bin (e.g. Bin #4 or Bin #7) until fill reaches **$\ge 80\%$**. Point out the red `ALERT` badge and autonomous task creation.
3. **Step 3: Hazardous Priority Sorting**  
   In the **Collector Priority Dispatch Queue**, observe that the solvent task automatically jumps to the top as **`● P1 HAZARDOUS`**, ahead of older standard tasks.
4. **Step 4: Collect & Audit Trail**  
   Click **`✓ Mark Collected`**. Observe that the bin resets to **`0%`**, and the exact weight and timestamp are logged to the **Compliance Audit Trail**.
5. **Step 5: Industrial Symbiosis Matching**  
   Inspect the **Industrial Symbiosis Matches** board showing how one factory's byproduct fulfills a neighboring factory's raw input requirements.
6. **Step 6: Impact & $\text{CO}_2$ Verification**  
   Point out the updated **Landfill Diversion Rate ($>85\%$)** and the estimated **$\text{CO}_2\text{e}$ emissions avoided**.

---

## 9. PowerPoint Presentation Deck

An executive 16:9 widescreen presentation deck has been generated:
- **File:** [LoopYard_Presentation.pptx](file:///Users/ishantverma/Desktop/kunj/LoopYard_Presentation.pptx)
- **Slide 1:** Title Slide (Dark Executive Aesthetic)
- **Slide 2:** The Industrial Inefficiency (Market Problem)
- **Slide 3:** The LoopYard 3-Pillar Circular Solution
- **Slide 4:** Three Operational Roles & Perspectives (Manager, Collector, Tenant)
- **Slide 5:** Technical Architecture & Dual-Engine Stack
- **Slide 6:** Autonomous Dispatch & Sorting Logic Rules
- **Slide 7:** Industrial Symbiosis & Lifecycle Emissions Model
- **Slide 8:** Two-Minute Live Demonstration Script
- **Slide 9:** Future Vision & Post-MVP Upgrade Path

To regenerate the deck at any time:
```bash
python3 generate_deck.py
```
=======
# LoopYard
>>>>>>> c35b5e2256e86cae52daf74e3dfcc6f9ec916ea0
