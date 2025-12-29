# ByteBot Tool v1.1.0 - Quick Reference

## What's New in v1.1.0

### Accurate Task Counting
```python
check_connection()
# Now shows:
# - Running tasks: 0 (only active)
# - Total tasks (all time): 68 (historical)
```

### Task Summary in Lists
```python
list_tasks()
# Output includes:
# Task Summary:
# Running: 0
# CANCELLED: 5
# FAILED: 2
```

### Pagination Support
```python
list_tasks(limit=10, page=1)  # First 10 tasks
list_tasks(limit=10, page=2)  # Next 10 tasks
# Shows: Page 1 of 7 (Total: 68 tasks)
```

### Active Tasks Filter
```python
list_active_tasks()
# Quick view of running tasks only
# Returns: "No active tasks currently running." or list of active tasks
```

---

## Function Reference

### check_connection()
**Purpose:** Verify ByteBot connectivity

**Returns:**
- Connection speed
- Running task count (currently executing)
- Tasks needing attention
- Total historical tasks
- Configured models
- Configuration settings

**Example:**
```python
check_connection()
```

---

### list_tasks(status_filter=None, limit=None, page=1)
**Purpose:** List tasks with summary and pagination

**Parameters:**
- `status_filter`: Filter by status (PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED, NEEDS_HELP, NEEDS_REVIEW)
- `limit`: Tasks per page (default: 20)
- `page`: Page number (default: 1)

**Returns:**
- Task summary (counts by status)
- Pagination info
- List of tasks with details

**Examples:**
```python
# All recent tasks (page 1)
list_tasks()

# Filter by status
list_tasks(status_filter="COMPLETED")
list_tasks(status_filter="FAILED")

# Pagination
list_tasks(limit=5, page=1)
list_tasks(limit=5, page=2)

# Combined
list_tasks(status_filter="CANCELLED", limit=10, page=1)
```

---

### list_active_tasks()
**Purpose:** Show only running tasks (convenience function)

**Returns:**
- Summary of running tasks
- List of PENDING, IN_PROGRESS, QUEUED tasks
- Or: "No active tasks currently running."

**Example:**
```python
list_active_tasks()
```

**Use Case:** Quick check of current system load

---

### execute_task(task_description, priority=None, wait_for_completion=None)
**Purpose:** Execute automation task

**Parameters:**
- `task_description`: Natural language task (string)
- `priority`: LOW, MEDIUM, HIGH, URGENT (default: MEDIUM)
- `wait_for_completion`: True (wait for result) or False (return task ID)

**Returns:**
- Task results (if wait_for_completion=True)
- Task ID (if wait_for_completion=False)

**Examples:**
```python
# Simple task
execute_task("Open Firefox and navigate to google.com")

# High priority
execute_task("Download urgent invoices", priority="HIGH")

# Submit and check later
task_id = execute_task("Long data migration", wait_for_completion=False)
```

---

### execute_task_with_files(task_description, priority=None, wait_for_completion=None)
**Purpose:** Execute task with file uploads

**Parameters:**
- Same as execute_task
- Files automatically included from OpenWebUI attachments

**Usage:**
1. Attach files in OpenWebUI chat
2. Call function with task description

**Example:**
```python
# User attaches PDFs, then:
execute_task_with_files("Extract payment terms from these contracts")
```

---

### get_task_status(task_id, include_messages=None)
**Purpose:** Check task status and progress

**Parameters:**
- `task_id`: Task ID (from execute_task)
- `include_messages`: Include execution logs (default: True)

**Returns:**
- Task status
- Duration
- Execution logs (if include_messages=True)

**Example:**
```python
get_task_status("task-abc123")
get_task_status("task-abc123", include_messages=False)
```

---

### cancel_task(task_id)
**Purpose:** Cancel running/pending task

**Parameters:**
- `task_id`: Task ID to cancel

**Returns:**
- Cancellation confirmation

**Example:**
```python
cancel_task("task-abc123")
```

---

## Status Values

### Active Statuses (Running)
- `PENDING` - Waiting to start
- `IN_PROGRESS` - Currently executing
- `QUEUED` - In queue

### Attention Required
- `NEEDS_HELP` - Requires human assistance
- `NEEDS_REVIEW` - Awaiting approval

### Terminal Statuses (Done)
- `COMPLETED` - Finished successfully
- `FAILED` - Ended with error
- `CANCELLED` - Stopped by user

---

## Priority Levels

- `URGENT` - Time-critical, business-critical
- `HIGH` - Important, quick execution needed
- `MEDIUM` - Standard tasks (default)
- `LOW` - Background, non-urgent

---

## Configuration

### Admin (Valves)
- `bytebot_url` - ByteBot API URL (default: http://192.168.0.102:9991)
- `task_timeout_seconds` - Max execution time (default: 600)
- `polling_interval_seconds` - Status check interval (default: 3)
- `max_retries` - Retry attempts (default: 3)
- `max_file_size_mb` - File upload limit (default: 100)
- `max_files_per_task` - Max files per task (default: 20)

### User (UserValves)
- `default_priority` - Default task priority (default: MEDIUM)
- `default_wait_for_completion` - Wait for results (default: True)
- `show_execution_logs` - Include logs (default: True)
- `task_history_limit` - Tasks per page (default: 20)
- `notification_verbosity` - Update frequency (default: normal)

---

## Common Patterns

### Check System Load
```python
check_connection()
# or
list_active_tasks()
```

### View Recent Activity
```python
list_tasks(limit=10)
```

### Find Failed Tasks
```python
list_tasks(status_filter="FAILED")
```

### Monitor Long Task
```python
# Submit task
result = execute_task("Long process", wait_for_completion=False)
# Extract task ID from result

# Check status later
get_task_status("task-xyz789")
```

### Browse All Tasks
```python
# Page through all tasks
list_tasks(page=1)
list_tasks(page=2)
list_tasks(page=3)
# ... etc
```

---

## Troubleshooting

### "No active tasks" when tasks are running
- Old version behavior showed total tasks as "active"
- Update to v1.1.0 for accurate counts
- Use `list_tasks()` to see all tasks with summary

### Tasks not appearing
- Check pagination: may be on later pages
- Try: `list_tasks(limit=50, page=1)`

### Connection errors
- Verify ByteBot is running: `docker ps | grep bytebot`
- Check network: `ping 192.168.0.102`
- Test API: `curl http://192.168.0.102:9991/tasks`

---

## Version Info

**Current Version:** 1.1.0  
**Release Date:** 2025-12-29  
**Compatibility:** ByteBot API with pagination support  
**Breaking Changes:** None (fully backwards compatible)

---

## Quick Examples

```python
# System health check
check_connection()

# What's running now?
list_active_tasks()

# Last 5 tasks
list_tasks(limit=5)

# All failed tasks
list_tasks(status_filter="FAILED", limit=100)

# Execute simple task
execute_task("Take a screenshot of the desktop")

# Process documents (attach files first)
execute_task_with_files("Summarize these reports")

# Cancel stuck task
cancel_task("task-abc123")
```

---

For detailed documentation, see [README.md](README.md)  
For installation, see [INSTALL.md](INSTALL.md)  
For changes, see [CHANGELOG.md](CHANGELOG.md)
