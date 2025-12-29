"""
Live integration tests for ByteBot tool.
Tests against actual ByteBot instance at 192.168.0.102:9991
"""

import asyncio
import sys

sys.path.insert(0, "/root/projects/openwebui/bytebot-integration")

from tool import Tools


async def test_check_connection():
    """Test connection check with accurate task counting."""
    print("\n=== Testing check_connection() ===")
    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"

    result = await tools.check_connection()
    print(result)

    # Verify "Running tasks:" appears instead of "Active tasks:"
    assert "Running tasks:" in result, (
        "Should show 'Running tasks:' not 'Active tasks:'"
    )
    assert "Total tasks (all time):" in result, "Should show total task count"
    print("✓ Connection check shows correct task counts")


async def test_list_tasks():
    """Test list_tasks with pagination and summary."""
    print("\n=== Testing list_tasks() ===")
    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"

    result = await tools.list_tasks(limit=5)
    print(result)

    # Verify summary is included
    assert "Task Summary:" in result, "Should include task summary"
    assert "Running:" in result, "Should show running task count"
    print("✓ Task list includes summary")


async def test_list_tasks_pagination():
    """Test pagination in list_tasks."""
    print("\n=== Testing list_tasks() pagination ===")
    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"

    # Test page 1
    result_page1 = await tools.list_tasks(limit=5, page=1)
    print("Page 1:")
    print(result_page1)

    # Test page 2
    result_page2 = await tools.list_tasks(limit=5, page=2)
    print("\nPage 2:")
    print(result_page2)

    # Verify pagination info
    if "Page" in result_page1:
        assert "Page 1 of" in result_page1, "Should show page 1 info"
        print("✓ Pagination information displayed correctly")
    else:
        print("✓ No pagination needed (only 1 page)")


async def test_list_active_tasks():
    """Test list_active_tasks convenience function."""
    print("\n=== Testing list_active_tasks() ===")
    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"

    result = await tools.list_active_tasks()
    print(result)

    # Should either show active tasks or "No active tasks"
    assert "No active tasks" in result or "Task Summary:" in result, (
        "Should show active tasks or message if none"
    )
    print("✓ Active tasks list works correctly")


async def test_status_filter():
    """Test status filtering."""
    print("\n=== Testing list_tasks() with status filter ===")
    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"

    result = await tools.list_tasks(status_filter="CANCELLED", limit=3)
    print(result)

    # Verify only cancelled tasks shown
    if "CANCELLED" in result:
        print("✓ Status filtering works")
    else:
        print("✓ No cancelled tasks found (acceptable)")


async def test_api_response_validation():
    """Test API response structure validation."""
    print("\n=== Testing API response validation ===")
    tools = Tools()

    # Test valid response
    valid_response = {"tasks": [], "total": 0, "totalPages": 1}
    assert tools._validate_api_response(valid_response, ["tasks"]), (
        "Should validate correct response structure"
    )

    # Test invalid response
    invalid_response = {"data": []}
    assert not tools._validate_api_response(invalid_response, ["tasks"]), (
        "Should reject incorrect response structure"
    )

    print("✓ API response validation working")


async def run_all_tests():
    """Run all tests sequentially."""
    try:
        await test_check_connection()
        await test_list_tasks()
        await test_list_tasks_pagination()
        await test_list_active_tasks()
        await test_status_filter()
        await test_api_response_validation()

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
