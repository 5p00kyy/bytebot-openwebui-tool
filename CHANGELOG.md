# ByteBot Automation Tool - Changelog

## Version 1.2.0 (2025-12-29)

### 🎉 Major Fix: Task Creation Now Working!

**Problem:** Task creation (POST /tasks) was returning HTTP 500 errors, preventing any new tasks from being created.

**Root Cause:** The ByteBot instance at http://192.168.0.102:9991 requires a `model` field in the task creation payload, but the tool wasn't including it.

**Solution:** Added complete model configuration support to the tool.

### New Features

#### 1. Model Configuration System
**Admin Configuration (Valves):**
- `default_model_name` - Default AI model (e.g., "openai/Qwen3-VL-32B-Instruct")
- `default_model_provider` - Model provider ("proxy", "openai", "anthropic")

**User Preferences (UserValves):**
- `preferred_model_name` - Override admin default on a per-user basis

#### 2. New Function: `get_available_models()`
Discovers available AI models by scanning recent tasks:
```python
await tools.get_available_models()
```

Returns formatted list showing:
- Model name and title
- Provider
- Context window size
- Which model is currently selected

#### 3. Automatic Model Injection
Both `execute_task()` and `execute_task_with_files()` now automatically include:
- `model` - Full model configuration object
- `type` - Task type ("IMMEDIATE")
- `control` - Control mode ("ASSISTANT")

### Technical Changes

#### Updated Functions
1. **`execute_task()`** - Now includes model field in task_data
2. **`execute_task_with_files()`** - Adds model as JSON in multipart form data
3. **Added `_get_model_config()`** - Helper to get model config with user override

#### Task Creation Payload (Before)
```json
{
  "description": "task description",
  "priority": "MEDIUM"
}
```

#### Task Creation Payload (After)
```json
{
  "description": "task description",
  "priority": "MEDIUM",
  "type": "IMMEDIATE",
  "control": "ASSISTANT",
  "model": {
    "name": "openai/Qwen3-VL-32B-Instruct",
    "title": "Qwen3-VL-32B-Instruct",
    "provider": "proxy",
    "contextWindow": 128000
  }
}
```

### Test Results
All task creation tests now passing (4/4):
- ✅ Basic task creation
- ✅ Task with HIGH priority
- ✅ Model discovery
- ✅ Custom model override (Browser-Use)

### Breaking Changes
None - fully backward compatible. Existing configurations will use the new defaults automatically.

### Upgrade Notes
1. No action required for most users - defaults work out of the box
2. To use a different model:
   - **Admin:** Set `default_model_name` in Valves
   - **User:** Set `preferred_model_name` in UserValves
3. Use `get_available_models()` to see what models are available

---

## Version 1.1.0 (2025-12-29)

### Critical Fixes

#### Fixed Incorrect Task Counting in check_connection()
**Problem:** The function reported all tasks (including completed/cancelled) as "Active tasks: X", which was misleading.

**Fix:** Now correctly distinguishes between:
- **Running tasks:** Only tasks with status PENDING, IN_PROGRESS, or QUEUED
- **Total tasks (all time):** Complete historical count from API

**Before:**
```
Connection successful (0.02s)
Status: 200 OK
Active tasks: 3
```

**After:**
```
Connection successful (0.01s)
Status: 200 OK
Running tasks: 0
Needs attention: 0
Total tasks (all time): 68
```

#### Fixed API Response Structure Handling
**Problem:** Code expected tasks as an array, but ByteBot API returns `{"tasks": [...], "total": X, "totalPages": Y}`.

**Fix:** All functions now properly extract the `tasks` array from the response object and use pagination metadata.

**Functions Updated:**
- `list_tasks()` - Now extracts tasks array and handles pagination
- `check_connection()` - Properly parses response structure
- `list_active_tasks()` (new) - Uses correct response format

### New Features

#### Task Status Summary
All task lists now include a comprehensive summary:

```
Task Summary:
Running: 0
CANCELLED: 5
FAILED: 2
```

The summary categorizes tasks into:
- **Running:** Currently executing (PENDING, IN_PROGRESS, QUEUED)
- **Needs Attention:** NEEDS_HELP, NEEDS_REVIEW
- **Terminal States:** COMPLETED, FAILED, CANCELLED

#### Pagination Support
`list_tasks()` now supports proper pagination with the ByteBot API:

```python
# Navigate through pages
list_tasks(limit=5, page=1)  # Page 1 of 14 (Total: 68 tasks)
list_tasks(limit=5, page=2)  # Page 2 of 14 (Total: 68 tasks)
```

**Features:**
- Manual page navigation (page parameter)
- Displays current page / total pages
- Shows total task count across all pages
- Per-page task limits

#### list_active_tasks() Convenience Function
New function to quickly view only running tasks:

```python
list_active_tasks()
# Returns: "No active tasks currently running."
# or shows tasks with PENDING, IN_PROGRESS, QUEUED status
```

**Use Case:** Quickly check current system load without seeing historical tasks.

### Improvements

#### Enhanced Error Messages
Retry attempts now show detailed progress:

**Before:**
```
Request failed, retrying in 1.0s (attempt 1/3)
```

**After:**
```
Request failed (attempt 1/3), retrying in 1.0s...
All 3 retry attempts failed
```

#### API Response Validation
Added `_validate_api_response()` helper to detect API format changes:

```python
if not self._validate_api_response(response_data, ["tasks"]):
    return "Error: Unexpected API response format. Please check ByteBot version compatibility."
```

This provides early warning if ByteBot API changes.

#### Task Summary Formatting
Tasks are now organized by category in listings:
1. Running tasks shown first
2. Tasks needing attention highlighted
3. Terminal states (completed/failed/cancelled)

### Technical Changes

#### Dependencies
- Added `from collections import Counter` for status counting

#### Version
- Updated from 1.0.0 to 1.1.0

#### New Helper Methods
- `_validate_api_response()` - Validates API response structure
- `_format_task_summary()` - Generates status count summary

#### Updated Methods
- `_format_task_list()` - Now accepts pagination parameters (page, total_pages, total)
- `list_tasks()` - Added page parameter, handles pagination
- `check_connection()` - Accurate active task counting
- `_retry_request()` - Enhanced error context in status updates

#### New Public Methods
- `list_active_tasks()` - List only running tasks

### Testing

All changes tested against live ByteBot instance at 192.168.0.102:9991

**Test Results:**
- ✓ Connection check shows correct task counts
- ✓ Task list includes summary
- ✓ Pagination information displayed correctly
- ✓ Active tasks list works correctly
- ✓ Status filtering works
- ✓ API response validation working

**Test Environment:**
- ByteBot with 68 total tasks
- 0 active tasks
- Multiple pages of task history

### Migration Guide

#### For Existing Users

**No Breaking Changes!** The tool remains fully backwards compatible.

**What's New:**
1. `check_connection()` now shows more accurate information
2. `list_tasks()` accepts optional `page` parameter (defaults to 1)
3. New `list_active_tasks()` function available

**Optional Updates:**

If you were using `check_connection()` output programmatically:
- Change `"Active tasks:"` checks to `"Running tasks:"`
- Add handling for `"Total tasks (all time):"`

### Bug Fixes

- Fixed task count showing total tasks instead of active tasks
- Fixed missing tasks array extraction from paginated responses
- Fixed status filtering applying client-side fallback when needed
- Fixed missing pagination metadata in task lists

### Known Issues

None identified in this release.

### Roadmap

#### Planned for v1.2.0
- WebSocket support for real-time task updates
- Task result caching
- Bulk task operations
- Export task history to CSV/JSON

#### Under Consideration
- Server-side status filtering (if ByteBot adds support)
- Task search by description
- Scheduled task support
- Task templates

---

## Version 1.0.0 (2025-12-29)

Initial release with core functionality:
- Task execution and monitoring
- File upload support
- Task management (list, status, cancel)
- Health checks
- Retry logic with exponential backoff
- Comprehensive error handling

---

For questions or issues, please refer to:
- README.md for usage documentation
- INSTALL.md for installation instructions
- tests/test_live_bytebot.py for test examples
