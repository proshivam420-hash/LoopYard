"""
generate_deck.py - Generates an executive 16:9 PowerPoint presentation for LoopYard.
Covers: Problem, Solution, Architecture, Tech Stack, Logic Rules, Symbiosis, and 2-Minute Demo.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import os

def create_presentation():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Color Palette
    COLOR_BG_DARK = RGBColor(15, 23, 42)      # #0F172A
    COLOR_CARD_DARK = RGBColor(30, 41, 59)    # #1E293B
    COLOR_BG_LIGHT = RGBColor(248, 250, 252)  # #F8FAFC
    COLOR_CARD_LIGHT = RGBColor(255, 255, 255)# #FFFFFF
    COLOR_BORDER_LIGHT = RGBColor(226, 232, 240) # #E2E8F0
    COLOR_EMERALD = RGBColor(5, 150, 105)     # #059669
    COLOR_EMERALD_LIGHT = RGBColor(16, 185, 129) # #10B981
    COLOR_COBALT = RGBColor(37, 99, 235)      # #2563EB
    COLOR_TEAL = RGBColor(13, 148, 136)       # #0D9488
    COLOR_CRIMSON = RGBColor(220, 38, 38)     # #DC2626
    COLOR_AMBER = RGBColor(217, 119, 6)       # #D97706
    COLOR_TEXT_PRIMARY = RGBColor(15, 23, 42)
    COLOR_TEXT_MUTED = RGBColor(100, 116, 139)
    COLOR_WHITE = RGBColor(255, 255, 255)

    def add_header(slide, title, category="LOOPYARD PLATFORM"):
        # Category Tracker
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.3))
        cat_tf = cat_box.text_frame
        cat_tf.word_wrap = True
        cat_p = cat_tf.paragraphs[0]
        cat_p.text = category.upper()
        cat_p.font.size = Pt(10)
        cat_p.font.bold = True
        cat_p.font.color.rgb = COLOR_EMERALD

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.5), Inches(0.6))
        title_tf = title_box.text_frame
        title_tf.word_wrap = True
        title_p = title_tf.paragraphs[0]
        title_p.text = title
        title_p.font.size = Pt(22)
        title_p.font.bold = True
        title_p.font.color.rgb = COLOR_TEXT_PRIMARY

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide (Dark Executive Aesthetic)
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_BG_DARK
    bg1.line.color.rgb = COLOR_BG_DARK

    # Accent Top Stripe
    stripe = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.1))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = COLOR_EMERALD_LIGHT
    stripe.line.color.rgb = COLOR_EMERALD_LIGHT

    # Title & Subtitle Box
    t_box = slide1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(3.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "CLOSED-LOOP INDUSTRIAL WASTE & SYMBIOSIS OS"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_EMERALD_LIGHT
    p0.space_after = Pt(14)

    p1 = tf1.add_paragraph()
    p1.text = "LoopYard"
    p1.font.size = Pt(54)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_after = Pt(14)

    p2 = tf1.add_paragraph()
    p2.text = "Autonomous Smart Bins, Priority Hazardous Dispatch, and Cross-Factory Raw Material Reuse for Gated Industrial Parks."
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_after = Pt(28)

    p3 = tf1.add_paragraph()
    p3.text = "Product Design Specification • System Architecture • Live Operational Demo"
    p3.font.size = Pt(12)
    p3.font.color.rgb = RGBColor(148, 163, 184)

    # -------------------------------------------------------------
    # SLIDE 2: Problem & Core Opportunity
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "The Industrial Inefficiency: Why Legacy Models Fail", "PROBLEM & MARKET CONTEXT")

    cards2 = [
        {
            "num": "01",
            "title": "Legacy Public Complaint Apps",
            "body": "Traditional municipal apps rely on passive citizen complaint forms where an admin manually flags status. They function only as basic, reactive CRUD forms completely disconnected from industrial parks.",
            "color": COLOR_CRIMSON
        },
        {
            "num": "02",
            "title": "The Linear Waste Trap",
            "body": "Factories pay high haulage fees to discard industrial byproducts (scrap metals, solvents, packaging, oils) directly to landfills, while neighboring factories buy the exact same virgin raw inputs.",
            "color": COLOR_AMBER
        },
        {
            "num": "03",
            "title": "Regulatory Compliance Risks",
            "body": "Hazardous industrial waste (used chemical solvents and industrial oils) lacks immutable chain-of-custody tracking, creating environmental liabilities and compliance audit failures.",
            "color": COLOR_COBALT
        }
    ]

    for i, c in enumerate(cards2):
        left = Inches(0.8 + i * 3.95)
        top = Inches(1.6)
        width = Inches(3.75)
        height = Inches(4.8)

        card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_LIGHT
        card.line.color.rgb = COLOR_BORDER_LIGHT

        # Top accent
        acc = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
        acc.fill.solid()
        acc.fill.fore_color.rgb = c["color"]
        acc.line.color.rgb = c["color"]

        tb = slide2.shapes.add_textbox(left + Inches(0.2), top + Inches(0.3), width - Inches(0.4), height - Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True

        pn = tf.paragraphs[0]
        pn.text = c["num"]
        pn.font.size = Pt(28)
        pn.font.bold = True
        pn.font.color.rgb = c["color"]
        pn.space_after = Pt(10)

        pt = tf.add_paragraph()
        pt.text = c["title"]
        pt.font.size = Pt(16)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_TEXT_PRIMARY
        pt.space_after = Pt(12)

        pb = tf.add_paragraph()
        pb.text = c["body"]
        pb.font.size = Pt(12)
        pb.font.color.rgb = COLOR_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 3: LoopYard 3-Pillar Solution
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "LoopYard Solution: Circular Economy Transformation", "CORE VALUE PROPOSITION")

    cards3 = [
        {
            "tag": "CLOSED ECOSYSTEM",
            "title": "Gated Industrial Park",
            "desc": "Built strictly for registered park tenants with zoned infrastructure (Zone A, B, C), removing external noise and optimizing internal logistics.",
            "color": COLOR_COBALT
        },
        {
            "tag": "AUTONOMOUS TELEMETRY",
            "title": "Sensor-Driven Dispatch",
            "desc": "Bins autonomously stream fill telemetry every 3 seconds. Crossing ≥ 80% automatically dispatches a prioritized collector task without human manual input.",
            "color": COLOR_EMERALD
        },
        {
            "tag": "INDUSTRIAL SYMBIOSIS",
            "title": "Waste Becomes a Resource",
            "desc": "Peer-to-peer circular engine continuously matches one factory's active waste output against neighboring factories' raw material input needs.",
            "color": COLOR_TEAL
        }
    ]

    for i, c in enumerate(cards3):
        left = Inches(0.8 + i * 3.95)
        top = Inches(1.6)
        width = Inches(3.75)
        height = Inches(4.8)

        card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_LIGHT
        card.line.color.rgb = COLOR_BORDER_LIGHT

        acc = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
        acc.fill.solid()
        acc.fill.fore_color.rgb = c["color"]
        acc.line.color.rgb = c["color"]

        tb = slide3.shapes.add_textbox(left + Inches(0.2), top + Inches(0.3), width - Inches(0.4), height - Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True

        ptag = tf.paragraphs[0]
        ptag.text = c["tag"]
        ptag.font.size = Pt(10)
        ptag.font.bold = True
        ptag.font.color.rgb = c["color"]
        ptag.space_after = Pt(10)

        pt = tf.add_paragraph()
        pt.text = c["title"]
        pt.font.size = Pt(18)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_TEXT_PRIMARY
        pt.space_after = Pt(14)

        pb = tf.add_paragraph()
        pb.text = c["desc"]
        pb.font.size = Pt(13)
        pb.font.color.rgb = COLOR_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 4: Three Operational Roles & Perspectives
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Unified Operations: Three Perspectives in One Dashboard", "ROLES & WORKFLOWS")

    roles = [
        {
            "role": "Park Manager / Admin",
            "focus": "Macro Park Governance & ESG Compliance",
            "tasks": [
                "Monitors real-time status of all 11 smart bins across industrial park zones.",
                "Tracks aggregate sustainability KPIs: Landfill Diversion Rate (%) and CO₂e Avoided.",
                "Maintains certified compliance audit trail for regulatory and environmental filings."
            ],
            "accent": COLOR_COBALT
        },
        {
            "role": "Collector (Driver)",
            "focus": "Prioritized Task Dispatch & Execution",
            "tasks": [
                "Live priority dispatch queue sorted automatically by hazardous status and age.",
                "P1 Hazardous pickups (solvents, oils) are pinned to the top of the route queue.",
                "One-click 'Mark Collected' completes task, resets bin to 0%, and records weight."
            ],
            "accent": COLOR_EMERALD
        },
        {
            "role": "Tenant (Factory)",
            "focus": "Internal Bin Tracking & Circular Exchange",
            "tasks": [
                "Tracks proprietary factory bins and real-time fill rates.",
                "Views active Industrial Symbiosis reuse opportunities with neighboring factories.",
                "Offsets raw material procurement costs by adopting peer factory byproducts."
            ],
            "accent": COLOR_TEAL
        }
    ]

    for i, r in enumerate(roles):
        left = Inches(0.8 + i * 3.95)
        top = Inches(1.6)
        width = Inches(3.75)
        height = Inches(4.8)

        card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_LIGHT
        card.line.color.rgb = COLOR_BORDER_LIGHT

        acc = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
        acc.fill.solid()
        acc.fill.fore_color.rgb = r["accent"]
        acc.line.color.rgb = r["accent"]

        tb = slide4.shapes.add_textbox(left + Inches(0.2), top + Inches(0.25), width - Inches(0.4), height - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True

        pr = tf.paragraphs[0]
        pr.text = r["role"]
        pr.font.size = Pt(17)
        pr.font.bold = True
        pr.font.color.rgb = COLOR_TEXT_PRIMARY
        pr.space_after = Pt(4)

        pf = tf.add_paragraph()
        pf.text = r["focus"]
        pf.font.size = Pt(11)
        pf.font.bold = True
        pf.font.color.rgb = r["accent"]
        pf.space_after = Pt(14)

        for t in r["tasks"]:
            ptk = tf.add_paragraph()
            ptk.text = "• " + t
            ptk.font.size = Pt(11)
            ptk.font.color.rgb = COLOR_TEXT_MUTED
            ptk.space_after = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 5: Technical Architecture & Zero-Dependency Stack
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Technical Architecture & Dual-Engine Stack", "ENGINEERING & DEPLOYMENT")

    tech_blocks = [
        ("Zero-Dependency Backend", "Python standard library (http.server, sqlite3, threading). Runs on any terminal via 'python server.py' on port 8000 with 0 pip installs required.", COLOR_COBALT),
        ("Background IoT Sensor Daemon", "Multithreaded background daemon updating bin fill percentages every 3 seconds based on waste category physics (capped at 100%).", COLOR_EMERALD),
        ("Normalized Relational DB", "Self-contained SQLite schema: tenants, bins, and pickups. Full relational integrity with automated reseed lifecycle.", COLOR_TEAL),
        ("Vercel-Ready Hybrid Frontend", "Dual-engine architecture: links to backend when /api/state is reachable; gracefully runs an in-browser simulation on static hosts (Vercel) with 0 blank screens.", COLOR_AMBER)
    ]

    for i, (title, desc, color) in enumerate(tech_blocks):
        row = i // 2
        col = i % 2
        left = Inches(0.8 + col * 5.95)
        top = Inches(1.6 + row * 2.5)
        width = Inches(5.75)
        height = Inches(2.2)

        card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_LIGHT
        card.line.color.rgb = COLOR_BORDER_LIGHT

        # Left border stripe
        acc = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(0.08), height)
        acc.fill.solid()
        acc.fill.fore_color.rgb = color
        acc.line.color.rgb = color

        tb = slide5.shapes.add_textbox(left + Inches(0.3), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.size = Pt(16)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_TEXT_PRIMARY
        pt.space_after = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(12)
        pd.font.color.rgb = COLOR_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 6: Logic Rules & Autonomous Dispatch Engine
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "System Logic Rules: Autonomous Dispatch & Sorting", "ALGORITHMS & LOGIC")

    rules = [
        ("Sensor Telemetry Rate", "Fill rates vary realistically by stream: Cardboard (+1.2%/3s), Organic (+1.5%/3s), Plastic (+1.1%/3s), Metal (+0.8%/3s), Oil (+0.7%/3s), Solvent (+0.6%/3s).", COLOR_COBALT),
        ("Autonomous Alert Trigger", "Whenever bin fill level reaches ≥ 80% AND no open pickup exists for that bin, the engine autonomously creates a pickup record with status 'open'.", COLOR_CRIMSON),
        ("Hazardous Priority Sorting", "Dispatches with hazardous categories (solvent, oil) are automatically pinned to the top of the driver queue (P1), followed by standard tasks ordered oldest-to-newest.", COLOR_AMBER),
        ("Pickup Completion Math", "When marked 'done', kg_collected = (fill_pct / 100) * capacity_kg. Bin resets to 0% and record enters immutable compliance ledger.", COLOR_EMERALD)
    ]

    for i, (title, desc, color) in enumerate(rules):
        row = i // 2
        col = i % 2
        left = Inches(0.8 + col * 5.95)
        top = Inches(1.6 + row * 2.5)
        width = Inches(5.75)
        height = Inches(2.2)

        card = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_LIGHT
        card.line.color.rgb = COLOR_BORDER_LIGHT

        acc = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(0.08), height)
        acc.fill.solid()
        acc.fill.fore_color.rgb = color
        acc.line.color.rgb = color

        tb = slide6.shapes.add_textbox(left + Inches(0.3), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.size = Pt(16)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_TEXT_PRIMARY
        pt.space_after = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(12)
        pd.font.color.rgb = COLOR_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 7: Industrial Symbiosis & ESG Sustainability Model
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Industrial Symbiosis & Lifecycle Emissions Model", "CIRCULAR IMPACT METRICS")

    # Left Card: Symbiosis Logic
    left_card = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.75), Inches(4.8))
    left_card.fill.solid()
    left_card.fill.fore_color.rgb = COLOR_CARD_LIGHT
    left_card.line.color.rgb = COLOR_BORDER_LIGHT
    l_acc = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.75), Inches(0.08))
    l_acc.fill.solid()
    l_acc.fill.fore_color.rgb = COLOR_TEAL
    l_acc.line.color.rgb = COLOR_TEAL

    tb_l = slide7.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.15), Inches(4.2))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p_sym_t = tf_l.paragraphs[0]
    p_sym_t.text = "Industrial Symbiosis Matching Rule"
    p_sym_t.font.size = Pt(18)
    p_sym_t.font.bold = True
    p_sym_t.font.color.rgb = COLOR_TEXT_PRIMARY
    p_sym_t.space_after = Pt(12)

    p_sym_d = tf_l.add_paragraph()
    p_sym_d.text = "A reuse match is autonomously surfaced whenever a bin's waste stream appears in another tenant's needs list AND that bin's fill level is at least ≥ 30%."
    p_sym_d.font.size = Pt(13)
    p_sym_d.font.color.rgb = COLOR_TEXT_MUTED
    p_sym_d.space_after = Pt(14)

    p_sym_e = tf_l.add_paragraph()
    p_sym_e.text = "Example Match:\n\"AutoParts Co (Zone A) has 225 kg of metal, SteelWorks Ltd (Zone A) needs it.\""
    p_sym_e.font.size = Pt(13)
    p_sym_e.font.bold = True
    p_sym_e.font.color.rgb = COLOR_TEAL

    # Right Card: Carbon Avoidance Factors
    right_card = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.75), Inches(4.8))
    right_card.fill.solid()
    right_card.fill.fore_color.rgb = COLOR_CARD_LIGHT
    right_card.line.color.rgb = COLOR_BORDER_LIGHT
    r_acc = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.75), Inches(0.08))
    r_acc.fill.solid()
    r_acc.fill.fore_color.rgb = COLOR_EMERALD
    r_acc.line.color.rgb = COLOR_EMERALD

    tb_r = slide7.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.15), Inches(4.2))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p_co2_t = tf_r.paragraphs[0]
    p_co2_t.text = "CO₂e Avoidance Lifecycle Factors"
    p_co2_t.font.size = Pt(18)
    p_co2_t.font.bold = True
    p_co2_t.font.color.rgb = COLOR_TEXT_PRIMARY
    p_co2_t.space_after = Pt(10)

    factors = [
        ("Metal Reclamation", "2.1 kg CO₂e / kg", "Avoids high-emission bauxite/iron smelting"),
        ("Waste Oil Regeneration", "1.8 kg CO₂e / kg", "Replaces virgin crude distillation"),
        ("Chemical Solvent Recovery", "1.6 kg CO₂e / kg", "Fractional distillation petrochem avoidance"),
        ("Polymer Remelting", "1.5 kg CO₂e / kg", "Prevents hydrocarbon cracking"),
        ("Cardboard Pulping", "1.2 kg CO₂e / kg", "Saves forestry biomass processing"),
        ("Organic Composting", "0.5 kg CO₂e / kg", "Prevents anaerobic methane emission")
    ]

    for name, factor, note in factors:
        pf = tf_r.add_paragraph()
        pf.text = f"• {name}: {factor} — {note}"
        pf.font.size = Pt(10.5)
        pf.font.color.rgb = COLOR_TEXT_MUTED
        pf.space_after = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 8: Two-Minute Live Demonstration Walkthrough
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Two-Minute Live Evaluator Demonstration Script", "DEMONSTRATION WALKTHROUGH")

    demo_steps = [
        ("Step 1: Live Overview", "Present the 6 factories and 11 bins streaming telemetry every 3s alongside top-level KPIs.", COLOR_COBALT),
        ("Step 2: Trigger Alert", "Click '+25% Dump Waste' on a solvent bin until it crosses ≥ 80%, triggering autonomous dispatch.", COLOR_CRIMSON),
        ("Step 3: Hazardous Priority", "Observe the solvent pickup automatically jump to the very top as 'P1 HAZARDOUS'.", COLOR_AMBER),
        ("Step 4: Collect & Audit", "Click 'Mark Collected': bin resets to 0% and immutable weight record enters compliance ledger.", COLOR_EMERALD),
        ("Step 5: Symbiosis Match", "Inspect the Reuse Board showing cross-factory circular material fulfillment.", COLOR_TEAL),
        ("Step 6: Impact Close", "Highlight updated Landfill Diversion Rate (87%+) and estimated CO₂e emissions avoided.", COLOR_COBALT)
    ]

    for i, (title, desc, color) in enumerate(demo_steps):
        row = i // 3
        col = i % 3
        left = Inches(0.8 + col * 3.95)
        top = Inches(1.6 + row * 2.5)
        width = Inches(3.75)
        height = Inches(2.2)

        card = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_LIGHT
        card.line.color.rgb = COLOR_BORDER_LIGHT

        acc = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
        acc.fill.solid()
        acc.fill.fore_color.rgb = color
        acc.line.color.rgb = color

        tb = slide8.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2), width - Inches(0.4), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.size = Pt(15)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_TEXT_PRIMARY
        pt.space_after = Pt(6)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11.5)
        pd.font.color.rgb = COLOR_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 9: Roadmap & Conclusion
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Future Roadmap: Post-MVP Upgrade Path", "SCALABILITY & FUTURE VISION")

    roadmap_items = [
        ("Physical ESP32 IoT Sensors", "Deploy ultrasonic distance sensors over LoRaWAN / cellular posting directly to LoopYard REST API endpoints."),
        ("Role-Based Access Control", "JWT-authenticated portals for Park Admins, Driver Mobile UI, and Tenant Accounting Managers."),
        ("Interactive GIS Park Map", "Spatial 2D/3D map displaying bin fill statuses grouped by industrial zone and collection routes."),
        ("B2B Waste Trading Marketplace", "Dynamic byproduct pricing, smart contract transfer approvals, and automated billing invoices.")
    ]

    for i, (title, desc) in enumerate(roadmap_items):
        top = Inches(1.6 + i * 1.25)
        card = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top, Inches(11.75), Inches(1.05))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_LIGHT
        card.line.color.rgb = COLOR_BORDER_LIGHT

        acc = slide9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top, Inches(0.08), Inches(1.05))
        acc.fill.solid()
        acc.fill.fore_color.rgb = COLOR_EMERALD
        acc.line.color.rgb = COLOR_EMERALD

        tb = slide9.shapes.add_textbox(Inches(1.1), top + Inches(0.12), Inches(11.2), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True

        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.size = Pt(15)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_TEXT_PRIMARY
        pt.space_after = Pt(2)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11.5)
        pd.font.color.rgb = COLOR_TEXT_MUTED

    # Save presentation
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LoopYard_Presentation.pptx")
    prs.save(output_path)
    print(f"✓ Successfully generated presentation at: {output_path}")

if __name__ == "__main__":
    create_presentation()
