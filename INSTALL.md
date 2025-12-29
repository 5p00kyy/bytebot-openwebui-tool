# ByteBot OpenWebUI Tool - Installation Guide

## Quick Start

### Step 1: Copy Tool Code

```bash
cat bytebot-integration/tool.py
```

Copy the entire output.

### Step 2: Import to OpenWebUI

1. Open your OpenWebUI instance in a web browser
2. Navigate to **Workspace > Tools**
3. Click **+ Create Tool** button
4. Paste the copied code into the editor
5. Click **Save**

### Step 3: Configure Connection

1. Click on the tool's settings (gear icon)
2. Configure **Valves** (Admin Settings):
   - **bytebot_url**: Set to your ByteBot instance (e.g., `http://192.168.0.102:9991`)
   - Leave other settings at defaults initially
3. Click **Save**

### Step 4: Test Connection

In an OpenWebUI chat, try:

```
check_connection()
```

You should see:
```
Connection successful (0.15s)
Status: 200 OK
Active tasks: 0
```

If you see connection errors, verify:
- ByteBot container is running: `docker ps | grep bytebot`
- Network connectivity: `ping 192.168.0.102`
- Port accessibility: `curl http://192.168.0.102:9991/tasks`

### Step 5: Execute Your First Task

Try a simple task:

```
execute_task("Open Firefox and navigate to example.com")
```

## Advanced Configuration

### Custom Timeout for Long Tasks

If your automation tasks take longer than 10 minutes:

1. Go to tool settings (gear icon)
2. Under **Valves**, set `task_timeout_seconds` to desired value (e.g., 1800 for 30 minutes)
3. Save changes

### File Upload Limits

To adjust file upload limits:

1. Tool settings > **Valves**
2. Set `max_file_size_mb` (default: 100MB)
3. Set `max_files_per_task` (default: 20)
4. Save changes

### User Preferences

Each user can customize their experience:

1. Tool settings > **UserValves**
2. Adjust:
   - `default_priority`: MEDIUM (or LOW, HIGH, URGENT)
   - `default_wait_for_completion`: True (or False to get task ID immediately)
   - `show_execution_logs`: True (or False for cleaner output)
   - `notification_verbosity`: normal (or minimal, verbose)
3. Save changes

## Troubleshooting Installation

### Tool Not Appearing

**Issue:** Tool doesn't show up in chat

**Solution:**
1. Refresh browser
2. Check tool is enabled in Workspace > Tools
3. Verify no syntax errors in tool code

### Connection Failed

**Issue:** "Could not reach ByteBot" error

**Solution:**
1. Verify ByteBot URL in Valves is correct
2. Check ByteBot is running: `docker ps | grep bytebot`
3. Test connection manually: `curl http://192.168.0.102:9991/tasks`
4. Check firewall rules allow access to port 9991

### Import Errors

**Issue:** "aiohttp" import error

**Solution:**
- OpenWebUI automatically installs dependencies from the `requirements` field in tool metadata
- Verify the requirements line in tool.py: `requirements: aiohttp>=3.9.0`
- Check OpenWebUI logs for dependency installation issues

## Usage Examples

Once installed, you can use the tool in any chat:

### Basic Task
```
execute_task("Download invoices from vendor portal")
```

### With Files
Attach PDFs to your message, then:
```
execute_task_with_files("Extract payment terms from these contracts")
```

### Check Status
```
list_tasks()
get_task_status("task-abc123")
cancel_task("task-abc123")
```

## Next Steps

- Read [README.md](README.md) for complete feature documentation
- Review [automation_examples.md](examples/automation_examples.md) for use case ideas
- Test with simple tasks before complex workflows
- Join ByteBot Discord for community support

## Support

- ByteBot Docs: https://docs.bytebot.ai
- ByteBot Discord: https://discord.gg/zcb5wA2t4u
- OpenWebUI Docs: https://docs.openwebui.com

## Version

Current Version: 1.0.0

License: MIT
