"""Test ByteBot task creation with model field fix."""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool import Tools


async def test_basic_task_creation():
    """Test basic task creation without waiting."""
    print("=" * 60)
    print("TEST 1: Basic Task Creation (No Wait)")
    print("=" * 60)

    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"
    tools.user_valves.default_wait_for_completion = False

    result = await tools.execute_task("Test task creation with model field fix")
    print(result)
    print()

    # Check if task was created successfully
    if "Task submitted successfully" in result and "Task ID" in result:
        print("✅ Task creation SUCCESSFUL")
        return True
    else:
        print("❌ Task creation FAILED")
        return False


async def test_task_with_priority():
    """Test task creation with HIGH priority."""
    print("=" * 60)
    print("TEST 2: Task Creation with HIGH Priority")
    print("=" * 60)

    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"
    tools.user_valves.default_wait_for_completion = False

    result = await tools.execute_task("High priority test task", priority="HIGH")
    print(result)
    print()

    if "Task submitted successfully" in result:
        print("✅ HIGH priority task creation SUCCESSFUL")
        return True
    else:
        print("❌ HIGH priority task creation FAILED")
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
        print("✅ Model discovery SUCCESSFUL")
        return True
    else:
        print("❌ Model discovery FAILED")
        return False


async def test_custom_model():
    """Test task creation with custom model override."""
    print("=" * 60)
    print("TEST 4: Task Creation with Custom Model")
    print("=" * 60)

    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"
    tools.user_valves.default_wait_for_completion = False
    tools.user_valves.preferred_model_name = "openai/Browser-Use"

    result = await tools.execute_task("Test task with Browser-Use model")
    print(result)
    print()

    if "Task submitted successfully" in result:
        print("✅ Custom model task creation SUCCESSFUL")
        return True
    else:
        print("❌ Custom model task creation FAILED")
        return False


async def main():
    """Run all tests."""
    print("\n🚀 Starting ByteBot Task Creation Tests (v1.2.0)")
    print(f"Target: http://192.168.0.102:9991\n")

    results = []

    # Test 1: Basic task creation
    try:
        results.append(await test_basic_task_creation())
    except Exception as e:
        print(f"❌ Test 1 FAILED with exception: {e}\n")
        results.append(False)

    # Test 2: Priority task
    try:
        results.append(await test_task_with_priority())
    except Exception as e:
        print(f"❌ Test 2 FAILED with exception: {e}\n")
        results.append(False)

    # Test 3: Model discovery
    try:
        results.append(await test_model_discovery())
    except Exception as e:
        print(f"❌ Test 3 FAILED with exception: {e}\n")
        results.append(False)

    # Test 4: Custom model
    try:
        results.append(await test_custom_model())
    except Exception as e:
        print(f"❌ Test 4 FAILED with exception: {e}\n")
        results.append(False)

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Task creation is now working!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
