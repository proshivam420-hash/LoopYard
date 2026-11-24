"""
test_partial_collect.py - Verification of Partial Collection Feature in LoopYard
"""

import database

def test_partial_collection():
    print("========================================")
    print(" Running Partial Collection Verification")
    print("========================================")

    database.init_db(force_reseed=True)

    # 1. Test partial collection on Bin 1 (AutoParts Co, metal, 45% of 500kg = 225kg)
    # Remove 25% -> fill becomes 20%, collected_kg = 25% of 500kg = 125.0 kg
    res1 = database.partial_collect_bin(1, remove_pct=25.0)
    assert res1["actual_removed_pct"] == 25.0, f"Expected 25.0%, got {res1['actual_removed_pct']}"
    assert res1["collected_kg"] == 125.0, f"Expected 125.0 kg, got {res1['collected_kg']}"
    assert res1["new_fill_pct"] == 20.0, f"Expected 20.0%, got {res1['new_fill_pct']}"
    print("✓ Test 1 Passed: Standard partial collection (-25%) accurately calculated.")

    # 2. Test auto-resolve open pickup when dropping below 80%
    # Bin 7 (ChemClean solvent, 75% of 250kg) + Dump 25% -> 100% -> creates open pickup!
    dump_res = database.dump_waste_into_bin(7, 25.0)
    assert dump_res["pickup_created"] is True
    open_pickups = database.get_priority_pickups()
    assert any(p["bin_id"] == 7 for p in open_pickups), "Open pickup should exist for Bin 7"

    # Now remove 50% from Bin 7 -> 100% - 50% = 50% (< 80% threshold!)
    # Open pickup should be auto-resolved and removed from active queue!
    res2 = database.partial_collect_bin(7, remove_pct=50.0)
    assert res2["actual_removed_pct"] == 50.0
    assert res2["new_fill_pct"] == 50.0
    assert res2["collected_kg"] == 125.0  # 50% of 250kg

    open_pickups_after = database.get_priority_pickups()
    assert not any(p["bin_id"] == 7 for p in open_pickups_after), "Bin 7 pickup should be auto-resolved from open queue"
    print("✓ Test 2 Passed: Open pickup auto-resolved when bin drops below 80% threshold.")

    # 3. Test clamping when remove_pct > current fill_pct
    # Bin 6 is at 20%. Try to remove 50% -> should clamp to 20%, new fill 0%
    res3 = database.partial_collect_bin(6, remove_pct=50.0)
    assert res3["actual_removed_pct"] == 20.0
    assert res3["new_fill_pct"] == 0.0
    assert res3["collected_kg"] == 60.0  # 20% of 300kg

    # Try removing from now-empty bin -> should be no-op (0kg)
    res3_empty = database.partial_collect_bin(6, remove_pct=25.0)
    assert res3_empty["actual_removed_pct"] == 0
    assert res3_empty["collected_kg"] == 0.0
    print("✓ Test 3 Passed: Clamping and empty-bin protection verified.")

    # 4. Check compliance audit trail and impact metrics
    log = database.get_compliance_log()
    assert log[0]["bin_id"] == 6
    assert log[0]["kg_collected"] == 60.0

    impact = database.get_impact_metrics()
    assert impact["total_kg_collected"] > 1405.0
    print(f"✓ Test 4 Passed: Compliance audit trail and impact metrics verified (Total: {impact['total_kg_collected']} kg).")

    print("========================================")
    print(" ALL PARTIAL COLLECTION TESTS PASSED 100%!")
    print("========================================")

if __name__ == "__main__":
    test_partial_collection()
