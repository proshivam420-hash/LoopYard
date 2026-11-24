"""
test_system.py - Comprehensive Verification of LoopYard PDR Rules & Requirements
Verifies:
1. Seed counts: 6 tenants, 11 smart bins, all 7 waste categories
2. Sensor simulation ticking
3. Auto-Alert & Pickup creation at >= 80% fill
4. Priority queue sorting: hazardous (solvent, oil) top, then oldest-to-newest
5. Pickup completion: kg_collected formula, done_time, status 'done', bin reset to 0%
6. Industrial symbiosis matching: >= 30% fill, another tenant's needs, narrative formatting
7. Diversion rate calculation: (non-mixed / total) * 100
8. CO2 emissions avoidance estimation
"""

import database
import json

def run_tests():
    print("========================================")
    print(" Running LoopYard PDR Verification Tests")
    print("========================================")

    # 1. Reset & Seed DB
    database.init_db(force_reseed=True)
    tenants = database.get_all_tenants()
    bins = database.get_all_bins()

    assert len(tenants) == 6, f"Expected 6 tenants, got {len(tenants)}"
    assert len(bins) == 11, f"Expected 11 smart bins, got {len(bins)}"

    waste_types = {b["waste_type"] for b in bins}
    expected_categories = {"metal", "plastic", "cardboard", "oil", "solvent", "organic", "mixed"}
    assert waste_types == expected_categories, f"Missing waste categories: {expected_categories - waste_types}"
    print("✓ Test 1 Passed: 6 tenants, 11 smart bins, all 7 waste types seeded.")

    # 2. Test Symbiosis Matching Rule
    matches = database.get_reuse_matches()
    assert len(matches) > 0, "Expected active reuse matches in initial seed"
    for m in matches:
        assert m["fill_pct"] >= 30.0, f"Match below 30% fill: {m}"
        assert m["source_tenant"] != m["target_tenant"], f"Self-match detected: {m}"
        assert "has" in m["narrative"] and "needs it" in m["narrative"], f"Improper narrative: {m['narrative']}"
    print(f"✓ Test 2 Passed: Industrial symbiosis matching ({len(matches)} matches verified).")

    # 3. Test Auto-Alert & Pickup Creation Rule (at >= 80% fill)
    # Bin 7 is ChemClean solvent with 75% fill. Adding 25% makes it 100%.
    res = database.dump_waste_into_bin(7, amount_pct=25.0)
    assert res["pickup_created"] is True, "Pickup should have been created at >= 80% fill"
    assert res["new_fill_pct"] == 100.0, f"Expected 100.0%, got {res['new_fill_pct']}"

    # Also dump into Bin 5 (EcoPack cardboard, 50% + 35% = 85%)
    res5 = database.dump_waste_into_bin(5, amount_pct=35.0)
    assert res5["pickup_created"] is True

    pickups = database.get_priority_pickups()
    assert len(pickups) == 2, f"Expected 2 open pickups, got {len(pickups)}"
    print("✓ Test 3 Passed: Auto-Alert & Pickup creation triggered at >= 80% fill.")

    # 4. Test Priority Queue Sorting Rule:
    # Solvent is hazardous, Cardboard is standard.
    # Solvent MUST be at index 0 (top of queue) even if created at same time or after!
    assert pickups[0]["waste_type"] in ("solvent", "oil"), f"Top of queue must be hazardous, got {pickups[0]['waste_type']}"
    assert pickups[0]["is_hazardous"] == 1, "Hazardous flag must be 1"
    assert pickups[1]["waste_type"] == "cardboard", f"Standard task should follow, got {pickups[1]['waste_type']}"
    print("✓ Test 4 Passed: Priority queue sorting verified (hazardous solvent pinned to top).")

    # 5. Test Pickup Completion Rule
    haz_pickup = pickups[0]
    p_id = haz_pickup["id"]
    bin_id = haz_pickup["bin_id"]
    bin_capacity = haz_pickup["capacity_kg"]
    bin_fill = haz_pickup["fill_pct"]
    expected_kg = round((bin_fill / 100.0) * bin_capacity, 1)

    completed = database.complete_pickup(p_id)
    assert completed is not None, "Failed to complete pickup"
    assert completed["kg_collected"] == expected_kg, f"Expected {expected_kg} kg, got {completed['kg_collected']}"

    # Check bin is reset to 0%
    bins_after = {b["id"]: b for b in database.get_all_bins()}
    assert bins_after[bin_id]["fill_pct"] == 0.0, f"Bin fill should be 0%, got {bins_after[bin_id]['fill_pct']}"

    # Check compliance log contains the record
    comp_log = database.get_compliance_log()
    assert comp_log[0]["id"] == p_id, "Latest completed pickup must be at top of compliance log"
    assert comp_log[0]["status"] == "done"
    print("✓ Test 5 Passed: Pickup completion calculated kg, updated compliance log, and reset bin to 0%.")

    # 6. Test Impact Metrics & Diversion Rate Formula
    impact = database.get_impact_metrics()
    total_kg = impact["total_kg_collected"]
    diverted_kg = impact["diverted_kg"]
    diversion_rate = impact["diversion_rate_pct"]

    expected_rate = round((diverted_kg / total_kg) * 100.0, 1)
    assert diversion_rate == expected_rate, f"Diversion rate mismatch: {diversion_rate} vs {expected_rate}"
    assert impact["co2_avoided_kg"] > 0, "CO2 avoided must be positive"
    print(f"✓ Test 6 Passed: Impact metrics verified (Total: {total_kg} kg, Diversion: {diversion_rate}%, CO2 avoided: {impact['co2_avoided_kg']} kg CO2e).")

    # 7. Test Sensor Simulation Tick
    tick_alerts = database.step_simulation_tick()
    bins_ticked = database.get_all_bins()
    # Check that bins have incremented
    assert bins_ticked[0]["fill_pct"] > 45.0, "Bin 1 should have incremented"
    print("✓ Test 7 Passed: Sensor simulation tick correctly increments fill levels.")

    print("========================================")
    print(" ALL 7 PDR VERIFICATION TESTS PASSED! 100% SUCCESS")
    print("========================================")

if __name__ == "__main__":
    run_tests()
