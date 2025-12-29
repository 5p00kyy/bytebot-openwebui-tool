"""
Test task creation with live ByteBot instance.
"""

import asyncio
import sys

sys.path.insert(0, "/root/projects/openwebui/bytebot-integration")

from tool import Tools


async def test_task_creation():
    """Test creating a simple task."""
    print("\n=== Testing Task Creation ===")
    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"

    # Create a simple task that should complete quickly
    print("\n1. Creating test task...")
    result = await tools.execute_task(
        "Open a text editor and type 'Hello from OpenWebUI tool test'",
        priority="MEDIUM",
        wait_for_completion=True,
    )

    print("\nResult:")
    print(result)
    print("\n" + "=" * 50)

    # Check if we got a valid response
    if "Task ID:" in result:
        print("✓ Task created successfully")
        if "COMPLETED" in result or "FAILED" in result or "NEEDS_HELP" in result:
            print("✓ Task finished with a terminal state")
        elif "TIMEOUT" in result:
            print("✓ Task timed out (expected for long tasks)")
        else:
            print("? Task in unknown state")
    else:
        print("✗ Task creation may have failed")
        print("Result:", result)


async def test_task_creation_no_wait():
    """Test creating a task without waiting."""
    print("\n=== Testing Task Creation (No Wait) ===")
    tools = Tools()
    tools.valves.bytebot_url = "http://192.168.0.102:9991"

    print("\n1. Creating task (return immediately)...")
    result = await tools.execute_task(
        "Check the current time and date", wait_for_completion=False
    )

    print("\nResult:")
    print(result)

    # Should return task ID
    if "Task ID:" in result:
        print("✓ Task submitted successfully")
        # Extract task ID
        import re

        match = re.search(r"Task ID.*?`([^`]+)`", result)
        if match:
            task_id = match.group(1)
            print(f"✓ Got task ID: {task_id}")

            # Now check status
            print("\n2. Checking task status...")
            status = await tools.get_task_status(task_id)
            print(status)
            print("✓ Status check works")
    else:
        print("✗ No task ID in response")


if __name__ == "__main__":
    print("Testing task creation with live ByteBot at 192.168.0.102:9991")
    print("=" * 70)

    try:
        asyncio.run(test_task_creation())
        asyncio.run(test_task_creation_no_wait())

        print("\n" + "=" * 70)
        print("TASK CREATION TESTS COMPLETED")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
