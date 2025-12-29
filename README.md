# ByteBot Automation Tool for OpenWebUI

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/5p00kyy/bytebot-openwebui-tool/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenWebUI](https://img.shields.io/badge/OpenWebUI-0.4.0+-orange.svg)](https://openwebui.com)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

Connect OpenWebUI to your ByteBot AI desktop agent for powerful automation task execution and management.

## Overview

ByteBot is a self-hosted AI desktop agent that automates computer tasks through natural language commands in a containerized Linux environment. This OpenWebUI tool provides complete integration with ByteBot's Agent API, allowing you to:

- Execute automation tasks with natural language descriptions
- Monitor task progress in real-time with status updates
- Upload and process files (PDFs, documents, spreadsheets)
- Manage task lifecycle (list, status check, cancellation)
- Verify connectivity and health of ByteBot instance

## Features

### Core Capabilities

1. **Task Execution** - Submit natural language automation tasks
2. **Real-time Monitoring** - Adaptive polling with progress updates
3. **File Processing** - Upload documents for ByteBot to analyze
4. **Task Management** - List, filter, and track automation tasks
5. **Health Checks** - Verify ByteBot connectivity and configuration

### Key Benefits

- **No Screenshots** - Focuses on automation, not desktop control
- **Adaptive Polling** - Smart intervals reduce API load
- **Retry Logic** - Automatic retry with exponential backoff
- **Error Handling** - Clear, actionable error messages
- **File Validation** - Prevents upload failures
- **Timeout Management** - Configurable timeouts for long-running tasks

## Prerequisites

- ByteBot instance running and accessible
- ByteBot Agent API endpoint (default: port 9991)
- Network connectivity to ByteBot server
- OpenWebUI version 0.4.0 or higher

## Installation

### 1. Import to OpenWebUI

1. Navigate to **Workspace > Tools** in OpenWebUI
2. Click **+ Create Tool** or **Import Tool**
3. Copy the contents of `tool.py`
4. Paste into the tool editor
5. Click **Save**

### 2. Configure Valves (Admin Settings)

Navigate to tool settings and configure:

| Setting | Default | Description |
|---------|---------|-------------|
| `bytebot_url` | `http://192.168.0.102:9991` | ByteBot Agent API URL |
| `litellm_proxy_url` | _(empty)_ | LiteLLM proxy URL (optional) |
| `task_timeout_seconds` | `600` | Max task execution time (10 min) |
| `polling_interval_seconds` | `3` | Initial polling interval |
| `max_retries` | `3` | Retry attempts for failed requests |
| `max_file_size_mb` | `100` | Maximum file size for uploads |
| `max_files_per_task` | `20` | Maximum files per task |
| `configured_models` | `Qwen3-VL-32B-Instruct` | Available AI models (documentation) |
| `default_model_name` | `openai/Qwen3-VL-32B-Instruct` | Default AI model for task execution |
| `default_model_provider` | `proxy` | AI model provider (proxy, openai, anthropic) |

### 3. Configure UserValves (User Preferences)

Each user can customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `default_priority` | `MEDIUM` | Default task priority |
| `default_wait_for_completion` | `True` | Wait for results vs return task ID |
| `show_execution_logs` | `True` | Include detailed logs in results |
| `task_history_limit` | `20` | Tasks shown in list |
| `notification_verbosity` | `normal` | Progress update frequency |
| `preferred_model_name` | _(empty)_ | Override default model (e.g., "openai/Browser-Use") |

## Usage

### Basic Task Execution

```python
# Execute a simple automation task
execute_task("Download all invoices from the vendor portal")

# With priority
execute_task("Process urgent expense reports", priority="HIGH")

# Return task ID immediately (don't wait)
execute_task("Long-running data migration", wait_for_completion=False)
```

**Example Output:**
```
Task Completed

Task ID: task-abc123
Description: Download all invoices from the vendor portal
Duration: 45 seconds

Execution Log:
- Opened Firefox browser
- Navigated to vendor.example.com
- Logged in successfully
- Found 12 invoices from December
- Downloaded all files to ~/Downloads/invoices/
```

### File Processing

```python
# Upload files and process them
# (Attach files to your OpenWebUI message first)
execute_task_with_files(
    "Extract payment terms from these contracts and create a comparison table"
)

# With custom priority
execute_task_with_files(
    "Analyze these financial reports for anomalies",
    priority="HIGH"
)
```

**Example Output:**
```
Files Processed: 3 files

Task Completed

Task ID: task-xyz789
Description: Extract payment terms from these contracts...
Duration: 120 seconds

Execution Log:
- Received 3 PDF files
- Extracted text from contract1.pdf
- Identified payment terms: Net 30 days
- Extracted text from contract2.pdf
- Identified payment terms: Net 45 days
- Created comparison table
```

### Task Management

```python
# List all recent tasks
list_tasks()

# Filter by status
list_tasks(status_filter="IN_PROGRESS")
list_tasks(status_filter="COMPLETED")

# Limit results
list_tasks(limit=10)

# Check specific task status
get_task_status("task-abc123")

# Cancel a running task
cancel_task("task-abc123")

# Discover available AI models
get_available_models()
```

### Health Check

```python
# Verify ByteBot connectivity
check_connection()
```

**Example Output:**
```
Connection successful (0.15s)
Status: 200 OK
Active tasks: 3

Configured Models:
Qwen3-VL-32B-Instruct

Configuration:
ByteBot URL: http://192.168.0.102:9991
Task timeout: 600s
Max retries: 3
```

## Function Reference

### execute_task()

Execute an automation task on ByteBot.

**Parameters:**
- `task_description` (str, required): Natural language task description
- `priority` (str, optional): LOW, MEDIUM, HIGH, or URGENT (default: user preference)
- `wait_for_completion` (bool, optional): Poll until done or return task ID (default: user preference)

**Returns:** Task execution results or task ID

**Example:**
```python
execute_task(
    "Log into CRM and export last month's leads",
    priority="HIGH",
    wait_for_completion=True
)
```

---

### execute_task_with_files()

Execute a task with file uploads for processing.

**Parameters:**
- `task_description` (str, required): Task description
- `priority` (str, optional): LOW, MEDIUM, HIGH, or URGENT
- `wait_for_completion` (bool, optional): Poll until done or return task ID
- `__files__` (list, optional): Uploaded files from OpenWebUI (automatically provided)

**Returns:** Task execution results with file processing outputs

**Example:**
```python
# User attaches files in OpenWebUI chat, then:
execute_task_with_files(
    "Read these contracts and extract key dates"
)
```

---

### list_tasks()

List recent ByteBot automation tasks.

**Parameters:**
- `status_filter` (str, optional): Filter by status (PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED, NEEDS_HELP, NEEDS_REVIEW)
- `limit` (int, optional): Maximum tasks to return (default: user preference)

**Returns:** Formatted list of tasks

**Example:**
```python
list_tasks(status_filter="IN_PROGRESS", limit=5)
```

---

### get_task_status()

Check the status of a specific automation task.

**Parameters:**
- `task_id` (str, required): The task ID to check
- `include_messages` (bool, optional): Include execution logs (default: user preference)

**Returns:** Current status and progress information

**Example:**
```python
get_task_status("task-abc123", include_messages=True)
```

---

### cancel_task()

Cancel a running or pending ByteBot task.

**Parameters:**
- `task_id` (str, required): The task ID to cancel

**Returns:** Cancellation confirmation or error message

**Example:**
```python
cancel_task("task-abc123")
```

---

### get_available_models()

Discover available AI models from recent ByteBot tasks.

**Parameters:** None

**Returns:** Formatted list of available models with details

**Example:**
```python
get_available_models()
```

**Output:**
```
**Available Models from Recent Tasks:**

1. **Qwen3-VL-32B-Instruct** ← **Currently Selected**
   - Name: `openai/Qwen3-VL-32B-Instruct`
   - Provider: proxy
   - Context: 128,000 tokens

2. **Browser-Use**
   - Name: `openai/Browser-Use`
   - Provider: proxy
   - Context: 128,000 tokens
```

---

### check_connection()

Verify ByteBot connectivity and display configuration.

**Parameters:** None

**Returns:** Connection status, API availability, configured models

**Example:**
```python
check_connection()
```

## Automation Use Cases

### Invoice Processing
```python
execute_task(
    "Log into vendor.example.com, navigate to invoices, "
    "download all invoices from December 2024, "
    "and organize by vendor name in ~/Downloads/invoices/",
    priority="HIGH"
)
```

### Document Analysis
```python
# Attach 3 contract PDFs to message, then:
execute_task_with_files(
    "Compare these contracts and create a table showing "
    "payment terms, delivery dates, and penalty clauses"
)
```

### Research Automation
```python
execute_task(
    "Search arXiv for papers on quantum error correction from 2024, "
    "download the top 5 by citation count, "
    "and create a summary of the main approaches"
)
```

### Data Reconciliation
```python
execute_task(
    "Open the ERP system and CRM, "
    "compare customer records, "
    "identify discrepancies, "
    "and generate a reconciliation report"
)
```

## Task Status States

ByteBot tasks progress through the following states:

| Status | Description | Terminal? |
|--------|-------------|-----------|
| `PENDING` | Task created, waiting to start | No |
| `IN_PROGRESS` | Task currently executing | No |
| `NEEDS_HELP` | Requires human assistance | Yes* |
| `NEEDS_REVIEW` | Awaiting user approval | Yes* |
| `COMPLETED` | Finished successfully | Yes |
| `FAILED` | Ended with error | Yes |
| `CANCELLED` | Stopped by user | Yes |

*Requires user action via ByteBot UI

## Error Handling

### Common Errors

#### Connection Failed
```
Connection Failed

Could not reach ByteBot at http://192.168.0.102:9991

Troubleshooting Steps:
1. Verify ByteBot is running: docker ps | grep bytebot
2. Check network connectivity: ping 192.168.0.102
3. Confirm port 9991 is accessible
4. Review ByteBot logs for errors
```

**Resolution:** Ensure ByteBot container is running and network is accessible.

---

#### Task Failed
```
Task Failed

Task ID: task-abc123
Error: Authentication failed - invalid credentials

Next Steps:
1. Review task description for clarity
2. Check ByteBot logs at http://192.168.0.102:6080
3. Verify credentials in password manager
4. Try simplifying the task
```

**Resolution:** Check credentials, review logs, simplify task description.

---

#### Human Assistance Required
```
Human Assistance Required

Task ID: task-abc123

ByteBot needs clarification or manual input to continue.

How to Help:
1. Open ByteBot UI: http://192.168.0.102:6080
2. Review the task messages
3. Provide requested information
4. ByteBot will resume automatically
```

**Resolution:** Open ByteBot UI and provide the requested information.

---

#### File Validation Failed
```
File validation failed:
- contract.pdf: 150.5MB exceeds limit (100MB)
- Too many files (25). Maximum: 20
```

**Resolution:** Reduce file sizes or number of files, adjust limits in Valves.

## Advanced Configuration

### Network Configuration

If ByteBot is on a different network:

1. Update `bytebot_url` in Valves to point to ByteBot's IP/hostname
2. Ensure firewall allows access to port 9991
3. Test connectivity with `check_connection()`

### LiteLLM Integration

If using LiteLLM proxy for model management:

1. Set `litellm_proxy_url` in Valves (e.g., `http://localhost:4000`)
2. ByteBot will query proxy for available models
3. Use `check_connection()` to verify proxy accessibility

### Timeout Adjustments

For long-running tasks:

1. Increase `task_timeout_seconds` in Valves (e.g., 1800 for 30 minutes)
2. Or set `wait_for_completion=False` to return task ID immediately
3. Check status later with `get_task_status(task_id)`

### Performance Tuning

- **Verbosity:** Set `notification_verbosity` to `minimal` for less frequent updates
- **Polling:** Increase `polling_interval_seconds` to reduce API load
- **Retries:** Adjust `max_retries` based on network reliability

## Troubleshooting

### ByteBot Not Responding

**Symptom:** Connection timeouts or slow responses

**Solutions:**
1. Check ByteBot container status: `docker ps | grep bytebot`
2. Review ByteBot logs: `docker logs bytebot-desktop`
3. Restart ByteBot: `docker-compose restart`
4. Check system resources (CPU, memory)

### Tasks Stuck in IN_PROGRESS

**Symptom:** Tasks never complete

**Solutions:**
1. Check ByteBot UI at http://192.168.0.102:6080 for details
2. Look for NEEDS_HELP status requiring user input
3. Cancel stuck task: `cancel_task(task_id)`
4. Review task description for clarity

### File Upload Failures

**Symptom:** File upload errors

**Solutions:**
1. Verify file size < max_file_size_mb (default 100MB)
2. Check file count < max_files_per_task (default 20)
3. Ensure files are attached before calling function
4. Try uploading files individually

### Rate Limiting

**Symptom:** Too many requests errors

**Solutions:**
1. Increase `polling_interval_seconds` in Valves
2. Reduce concurrent task submissions
3. Set `wait_for_completion=False` for batch operations
4. Monitor with `list_tasks()` to track load

## Best Practices

### Task Descriptions

**Good:**
```python
execute_task(
    "Log into vendor.acme.com using 1Password credentials, "
    "navigate to Invoices > December 2024, "
    "download all PDF invoices, "
    "save to ~/Downloads/acme_invoices/"
)
```

**Bad:**
```python
execute_task("Get invoices")  # Too vague
```

**Tips:**
- Be specific about actions and locations
- Include credentials source (e.g., 1Password)
- Specify exact paths and dates
- Break complex workflows into steps

### Priority Usage

- **URGENT:** Time-sensitive, business-critical tasks
- **HIGH:** Important tasks requiring quick execution
- **MEDIUM:** Standard automation tasks (default)
- **LOW:** Background tasks, non-urgent operations

### File Processing

- Keep files under 100MB for faster processing
- Use descriptive filenames
- Group related files together
- Specify output format in task description

### Task Management

- Use `list_tasks()` regularly to monitor automation
- Cancel unnecessary tasks to free resources
- Review failed tasks for patterns
- Archive or clean up old completed tasks

## Security Considerations

### Credential Management

ByteBot integrates with password managers (1Password, Bitwarden):

- **Do not** include credentials in task descriptions
- **Use** password manager references (e.g., "using 1Password")
- **Enable** 2FA for sensitive systems
- **Create** dedicated service accounts for automation

### Network Security

- Run ByteBot on a private network when possible
- Use firewall rules to restrict access to port 9991
- Monitor ByteBot logs for unauthorized access
- Review task history regularly

### Data Privacy

- All processing happens on your ByteBot instance
- No data sent to external services (except as instructed in tasks)
- Files uploaded are stored in ByteBot's container
- Review task descriptions before submission

## Support & Resources

### ByteBot Documentation
- Official Docs: https://docs.bytebot.ai
- API Reference: https://docs.bytebot.ai/api-reference
- GitHub: https://github.com/bytebot-ai/bytebot
- Discord: https://discord.gg/zcb5wA2t4u

### OpenWebUI Resources
- OpenWebUI Docs: https://docs.openwebui.com
- Tool Development: https://docs.openwebui.com/features/plugin/tools/

### Common Issues
- Review task logs in ByteBot UI
- Check network connectivity
- Verify ByteBot container status
- Consult ByteBot Discord for community support

## Version History

### v1.0.0 (Current)
- Initial release
- Core task execution and monitoring
- File upload support
- Task management (list, status, cancel)
- Health check and diagnostics
- Retry logic with exponential backoff
- Adaptive polling strategy
- Comprehensive error handling

## License

MIT License - See tool metadata for details

## Contributing

To contribute improvements:

1. Test changes with live ByteBot instance
2. Ensure all functions have docstrings
3. Add examples to documentation
4. Submit issues or pull requests to OpenWebUI

---

**Ready to automate?** Start with `check_connection()` to verify your ByteBot setup, then try a simple task!
