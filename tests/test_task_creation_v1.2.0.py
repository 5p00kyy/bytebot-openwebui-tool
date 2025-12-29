"""Test ByteBot task creation with model field fix (v1.2.0)."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool import Tools


async def test_basic_task_creation():
    """Test basic task creation without waiting."""
    print("=" * 60)
    print("TEST 1: Basic Task Creation")
    print("=" * 60)

    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"
    tools.user_valves.default_wait_for_completion = False

    result = await tools.execute_task("Test task creation with model field")
    print(result)
    print()

    if "Task submitted successfully" in result and "Task ID" in result:
        print("PASS: Task creation successful")
        return True
    else:
        print("FAIL: Task creation failed")
        return False


async def test_high_priority_task():
    """Test task creation with HIGH priority."""
    print("=" * 60)
    print("TEST 2: High Priority Task")
    print("=" * 60)

    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"
    tools.user_valves.default_wait_for_completion = False

    result = await tools.execute_task("High priority test task", priority="HIGH")
    print(result)
    print()

    if "Task submitted successfully" in result:
        print("PASS: High priority task created")
        return True
    else:
        print("FAIL: High priority task creation failed")
        return False


async def test_model_discovery():
    """Test get_available_models function."""
    print("=" * 60)
    print("TEST 3: Model Discovery")
    print("=" * 60)

    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"

    result = await tools.get_available_models()
    print(result)
    print()

    if "Available Models" in result or "model" in result.lower():
        print("PASS: Model discovery successful")
        return True
    else:
        print("FAIL: Model discovery failed")
        return False


async def test_custom_model():
    """Test task creation with custom model override."""
    print("=" * 60)
    print("TEST 4: Custom Model Override")
    print("=" * 60)

    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"
    tools.user_valves.default_wait_for_completion = False
    tools.user_valves.preferred_model_name = "openai/Browser-Use"

    result = await tools.execute_task("Test with Browser-Use model")
    print(result)
    print()

    if "Task submitted successfully" in result:
        print("PASS: Custom model task created")
        return True
    else:
        print("FAIL: Custom model task creation failed")
        return False


async def main():
    """Run all tests."""
    print("\nByteBot Task Creation Tests (v1.2.0)")
    print(f"Target: http://192.168.0.102:9991\n")

    results = []

    try:
        results.append(await test_basic_task_creation())
    except Exception as e:
        print(f"FAIL: Test 1 exception: {e}\n")
        results.append(False)

    try:
        results.append(await test_high_priority_task())
    except Exception as e:
        print(f"FAIL: Test 2 exception: {e}\n")
        results.append(False)

    try:
        results.append(await test_model_discovery())
    except Exception as e:
        print(f"FAIL: Test 3 exception: {e}\n")
        results.append(False)

    try:
        results.append(await test_custom_model())
    except Exception as e:
        print(f"FAIL: Test 4 exception: {e}\n")
        results.append(False)

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("\nAll tests passed - task creation working")
    else:
        print(f"\n{total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
