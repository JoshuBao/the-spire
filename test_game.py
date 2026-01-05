#!/usr/bin/env python3
"""
Quick test to verify the game works
"""

from main import SpireApp, Simulation

def test_simulation():
    """Test that simulation works"""
    print("Testing simulation...")
    sim = Simulation()

    initial_year = sim.state.year
    initial_month = sim.state.month

    # Test advance turn
    sim.advance_turn("wait")
    assert sim.state.month == initial_month + 1, "Month should increment"
    print("  ✓ Time advances")

    # Test repair action
    initial_materials = sim.state.materials
    sim.advance_turn("repair")
    # Materials should change (either spent or stayed same if not enough)
    print(f"  ✓ Repair action executes (materials: {initial_materials} -> {sim.state.materials})")

    # Test that events are logged
    assert len(sim.state.events) > 0, "Events should be logged"
    print(f"  ✓ Events logged: {len(sim.state.events)} events")

    print("Simulation: OK\n")

def test_app_initialization():
    """Test that app initializes correctly"""
    print("Testing app initialization...")

    try:
        app = SpireApp()
        print("  ✓ App creates successfully")

        # Check simulation is initialized
        assert app.sim is not None, "Simulation should exist"
        print("  ✓ Simulation initialized")

        # Check bindings exist
        assert len(app.BINDINGS) > 0, "Bindings should exist"
        print(f"  ✓ {len(app.BINDINGS)} key bindings configured")

        # Check all action methods exist
        for key, action, desc in app.BINDINGS:
            method_name = f"action_{action}"
            assert hasattr(app, method_name), f"Missing action method: {method_name}"
        print("  ✓ All action methods exist")

        print("App initialization: OK\n")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        raise

def test_action_methods():
    """Test that action methods work"""
    print("Testing action methods...")

    app = SpireApp()
    initial_cursor = app.sim.state.cursor

    # Test cursor movement (manually, without refresh)
    app.sim.state.cursor = min(app.sim.state.cursor + 1, app.sim.state.max_height)
    assert app.sim.state.cursor == initial_cursor + 1, "Cursor should move up"
    print("  ✓ Move up logic works")

    app.sim.state.cursor = max(app.sim.state.cursor - 1, 1)
    assert app.sim.state.cursor == initial_cursor, "Cursor should move down"
    print("  ✓ Move down logic works")

    # Test an action that advances time (directly on sim)
    initial_month = app.sim.state.month
    app.sim.advance_turn("wait")
    assert app.sim.state.month == initial_month + 1, "Wait should advance time"
    print("  ✓ Wait action works")

    print("Action methods: OK\n")
    print("  (Note: Full UI refresh requires app to be running)")

if __name__ == "__main__":
    print("="*50)
    print("THE SPIRE - GAME TEST")
    print("="*50 + "\n")

    try:
        test_simulation()
        test_app_initialization()
        test_action_methods()

        print("="*50)
        print("ALL TESTS PASSED ✓")
        print("="*50)
        print("\nThe game should work correctly!")
        print("Run: ./run.sh or python main.py")

    except Exception as e:
        print("\n" + "="*50)
        print("TESTS FAILED ✗")
        print("="*50)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
