"""
title: ByteBot Automation Tool
author: OpenWebUI Development Team
author_url: https://github.com/open-webui
git_url: https://github.com/bytebot-ai/bytebot
description: Execute automation tasks on ByteBot AI desktop agent with complete task management
required_open_webui_version: 0.4.0
requirements: aiohttp>=3.9.0
version: 1.2.0
license: MIT
"""

import asyncio
import json
import time
from collections import Counter
from datetime import datetime
from typing import Callable, Any, Optional, List, Dict
from pydantic import BaseModel, Field
import aiohttp


class EventEmitter:
    """Helper class for emitting status events to OpenWebUI."""

    def __init__(
        self,
        event_emitter: Optional[Callable[[dict], Any]] = None,
        verbosity: str = "normal",
    ):
        self.event_emitter = event_emitter
        self.verbosity = verbosity
        self.last_emit_time = 0
        self.emit_count = 0

    async def emit(self, description: str, done: bool = False):
        """Emit a status update event."""
        if not self.event_emitter:
            return

        # Throttle based on verbosity
        current_time = time.time()
        time_since_last = current_time - self.last_emit_time

        if not done:
            if self.verbosity == "minimal" and time_since_last < 10:
                return  # Only emit every 10 seconds for minimal
            elif (
                self.verbosity == "normal"
                and time_since_last < 3
                and self.emit_count > 0
            ):
                return  # Every 3 seconds for normal (except first)

        await self.event_emitter(
            {"type": "status", "data": {"description": description, "done": done}}
        )

        self.last_emit_time = current_time
        self.emit_count += 1


class ErrorFormatter:
    """Format errors into user-friendly messages."""

    @staticmethod
    def format_connection_error(url: str) -> str:
        return f"""Connection Failed

Could not reach ByteBot at {url}

Troubleshooting Steps:
1. Verify ByteBot is running: docker ps | grep bytebot
2. Check network connectivity: ping 192.168.0.102
3. Confirm port 9991 is accessible: curl {url}/tasks
4. Review ByteBot logs for errors

Need help? Visit https://docs.bytebot.ai"""

    @staticmethod
    def format_api_error(error: Exception, operation: str) -> str:
        """Format API errors with user-friendly messages."""
        if isinstance(error, asyncio.TimeoutError):
            return f"{operation} timed out. The service may be busy - please try again later."

        elif isinstance(error, aiohttp.ClientResponseError):
            status = error.status
            if status == 404:
                return f"{operation} failed - resource not found (404)."
            elif status >= 500:
                return f"Server error during {operation}. The service may be experiencing issues."
            else:
                return f"{operation} failed with status {status}: {error.message}"

        elif isinstance(error, aiohttp.ClientError):
            return f"Network error during {operation}. Please check your connection."

        else:
            return f"Unexpected error during {operation}: {str(error)}"

    @staticmethod
    def format_task_failed(task_id: str, messages: List[dict]) -> str:
        """Format task failure message."""
        error_msg = "No error details available"

        # Extract error from last message if available
        if messages:
            last_msg = messages[-1]
            content_blocks = last_msg.get("content", [])
            for block in content_blocks:
                if block.get("type") == "text":
                    error_msg = block.get("text", error_msg)

        return f"""Task Failed

Task ID: {task_id}
Error: {error_msg}

Next Steps:
1. Review task description for clarity
2. Check ByteBot logs at http://192.168.0.102:6080
3. Verify credentials in password manager
4. Try simplifying the task into smaller steps

Tip: Start with simpler tasks to verify ByteBot is working correctly."""

    @staticmethod
    def format_needs_help(task_id: str) -> str:
        """Format needs help message."""
        return f"""Human Assistance Required

Task ID: {task_id}

ByteBot needs clarification or manual input to continue.

How to Help:
1. Open ByteBot UI: http://192.168.0.102:6080
2. Review the task messages
3. Provide requested information or take manual action
4. ByteBot will resume automatically

Tip: Common reasons include ambiguous instructions, authentication prompts, or CAPTCHAs."""


class Tools:
    """ByteBot Automation Tool - Execute and manage automation tasks on ByteBot AI desktop agent."""

    class Valves(BaseModel):
        """Admin-level configuration for ByteBot integration."""

        bytebot_url: str = Field(
            default="http://192.168.0.102:9991", description="ByteBot Agent API URL"
        )

        litellm_proxy_url: str = Field(
            default="",
            description="LiteLLM proxy URL for model info (optional, e.g., http://localhost:4000)",
        )

        task_timeout_seconds: int = Field(
            default=600,
            description="Maximum time to wait for task completion (10 minutes)",
        )

        polling_interval_seconds: int = Field(
            default=3, description="Initial polling interval for task status checks"
        )

        max_retries: int = Field(
            default=3, description="Maximum retry attempts for failed API requests"
        )

        max_file_size_mb: int = Field(
            default=100, description="Maximum file size for uploads (MB)"
        )

        max_files_per_task: int = Field(
            default=20, description="Maximum number of files per task"
        )

        configured_models: str = Field(
            default="Qwen3-VL-32B-Instruct",
            description="Comma-separated list of configured models (for documentation)",
        )

        default_model_name: str = Field(
            default="openai/Qwen3-VL-32B-Instruct",
            description="Default AI model name for task execution",
        )

        default_model_provider: str = Field(
            default="proxy",
            description="AI model provider (proxy, openai, anthropic, etc.)",
        )

    class UserValves(BaseModel):
        """User-specific preferences for ByteBot automation."""

        default_priority: str = Field(
            default="MEDIUM",
            description="Default task priority (LOW, MEDIUM, HIGH, URGENT)",
        )

        default_wait_for_completion: bool = Field(
            default=True,
            description="Wait for task completion by default (True) or return task ID (False)",
        )

        show_execution_logs: bool = Field(
            default=True, description="Include detailed message logs in task results"
        )

        task_history_limit: int = Field(
            default=20, description="Number of tasks to show in list_tasks()"
        )

        notification_verbosity: str = Field(
            default="normal",
            description="Progress update frequency (minimal, normal, verbose)",
        )

        preferred_model_name: str = Field(
            default="",
            description="Override default model (leave empty to use admin default)",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.user_valves = self.UserValves()
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with connection pooling."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.valves.task_timeout_seconds)
            connector = aiohttp.TCPConnector(
                limit=10, limit_per_host=5, ttl_dns_cache=300
            )
            self._session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self._session

    async def _retry_request(
        self, method: str, url: str, emitter: Optional[Any] = None, **kwargs
    ) -> dict:
        """Make HTTP request with exponential backoff retry."""
        last_exception = None

        for attempt in range(self.valves.max_retries):
            try:
                session = await self._get_session()
                async with session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()

            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                last_exception = e

                if attempt < self.valves.max_retries - 1:
                    delay = 1.0 * (2**attempt)  # Exponential backoff
                    if emitter:
                        await emitter.emit(
                            f"Request failed (attempt {attempt + 1}/{self.valves.max_retries}), "
                            f"retrying in {delay:.1f}s...",
                            done=False,
                        )
                    await asyncio.sleep(delay)
                else:
                    # Last attempt failed
                    if emitter:
                        await emitter.emit(
                            f"All {self.valves.max_retries} retry attempts failed",
                            done=False,
                        )

        # All retries exhausted
        if last_exception:
            raise last_exception

    async def _poll_task_completion(
        self, task_id: str, emitter: Optional[Any] = None
    ) -> dict:
        """Poll task with adaptive intervals until completion or timeout."""
        intervals = [2, 3, 5, 8, 13, 20]  # Fibonacci-like progression
        poll_count = 0
        start_time = time.time()

        while True:
            # Determine current interval
            interval = intervals[min(poll_count, len(intervals) - 1)]

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > self.valves.task_timeout_seconds:
                if emitter:
                    await emitter.emit(
                        f"Task timeout after {elapsed:.0f}s. Task still running.",
                        done=True,
                    )
                return {
                    "status": "TIMEOUT",
                    "task_id": task_id,
                    "timeout_info": f"Exceeded {self.valves.task_timeout_seconds}s timeout",
                }

            # Poll status
            try:
                task = await self._retry_request(
                    "GET", f"{self.valves.bytebot_url}/tasks/{task_id}", emitter=emitter
                )
            except Exception as e:
                if emitter:
                    await emitter.emit(
                        f"Error polling task status: {str(e)}", done=True
                    )
                raise

            status = task.get("status")

            # Emit progress update based on verbosity
            if emitter:
                latest_message = self._get_latest_message_text(task)
                if latest_message:
                    description = f"{status}: {latest_message[:80]}..."
                else:
                    description = f"Task status: {status}"
                await emitter.emit(description, done=False)

            # Check terminal states
            if status in ["COMPLETED", "FAILED", "CANCELLED"]:
                return task

            if status == "NEEDS_HELP":
                if emitter:
                    await emitter.emit("Task needs human assistance", done=True)
                return task

            if status == "NEEDS_REVIEW":
                if emitter:
                    await emitter.emit("Task needs review", done=True)
                return task

            # Wait before next poll
            await asyncio.sleep(interval)
            poll_count += 1

    def _get_latest_message_text(self, task: dict) -> str:
        """Extract latest message text from task."""
        messages = task.get("messages", [])
        if not messages:
            return ""

        for msg in reversed(messages):
            if msg.get("role") == "ASSISTANT":
                content_blocks = msg.get("content", [])
                for block in content_blocks:
                    if block.get("type") == "text":
                        return block.get("text", "")

        return ""

    def _format_task_result(self, task: dict) -> str:
        """Format completed task as markdown."""
        status = task.get("status", "UNKNOWN")
        task_id = task.get("id", "N/A")
        description = task.get("description", "No description")
        created = task.get("createdAt", "")
        updated = task.get("updatedAt", "")

        # Calculate duration
        try:
            start = datetime.fromisoformat(created.replace("Z", "+00:00"))
            end = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            duration = (end - start).total_seconds()
            duration_str = f"{duration:.0f} seconds"
        except:
            duration_str = "Unknown"

        # Build output
        output = [
            f"**Task {status.title()}**",
            "",
            f"**Task ID:** `{task_id}`",
            f"**Description:** {description}",
            f"**Duration:** {duration_str}",
            "",
        ]

        # Handle timeout status
        if status == "TIMEOUT":
            timeout_info = task.get("timeout_info", "")
            output.append(f"**Status:** Task timed out - {timeout_info}")
            output.append(f"**Task ID for manual check:** `{task_id}`")
            output.append(f"Use get_task_status('{task_id}') to check current status.")
            return "\n".join(output)

        # Include messages if enabled
        if self.user_valves.show_execution_logs and "messages" in task:
            messages = task.get("messages", [])
            if messages:
                output.append("**Execution Log:**")
                for msg in messages:
                    if msg.get("role") == "ASSISTANT":
                        content_blocks = msg.get("content", [])
                        for block in content_blocks:
                            if block.get("type") == "text":
                                text = block.get("text", "")
                                # Truncate very long messages
                                if len(text) > 200:
                                    text = text[:200] + "..."
                                output.append(f"- {text}")
                output.append("")

        # Action items based on status
        if status == "NEEDS_HELP":
            output.append(
                "**Action Required:** Check ByteBot UI at http://192.168.0.102:6080"
            )
        elif status == "NEEDS_REVIEW":
            output.append(
                "**Action Required:** Review and approve task at http://192.168.0.102:6080"
            )
        elif status == "FAILED":
            output.append("**Next Steps:** Review logs and try simplifying the task")

        return "\n".join(output)

    def _validate_api_response(self, data: Any, expected_keys: List[str]) -> bool:
        """Validate API response structure."""
        if not isinstance(data, dict):
            return False
        return all(key in data for key in expected_keys)

    def _get_model_config(self) -> dict:
        """Get model configuration with user preference override."""
        model_name = (
            self.user_valves.preferred_model_name.strip()
            if self.user_valves.preferred_model_name.strip()
            else self.valves.default_model_name
        )

        model_title = model_name.split("/")[-1] if "/" in model_name else model_name

        return {
            "name": model_name,
            "title": model_title,
            "provider": self.valves.default_model_provider,
            "contextWindow": 128000,
        }

    def _format_task_summary(self, tasks: List[dict]) -> str:
        """Generate status summary from task list."""
        if not tasks:
            return ""

        status_counts = Counter(t.get("status", "UNKNOWN") for t in tasks)

        summary_lines = ["**Task Summary:**"]

        # Active tasks first (currently running)
        active_statuses = ["PENDING", "IN_PROGRESS", "QUEUED"]
        active_total = sum(status_counts.get(s, 0) for s in active_statuses)
        if active_total > 0:
            summary_lines.append(f"Running: {active_total}")
            for status in active_statuses:
                count = status_counts.get(status, 0)
                if count > 0:
                    summary_lines.append(f"  - {status}: {count}")
        else:
            summary_lines.append("Running: 0")

        # Tasks needing attention
        attention_statuses = ["NEEDS_HELP", "NEEDS_REVIEW"]
        attention_total = sum(status_counts.get(s, 0) for s in attention_statuses)
        if attention_total > 0:
            summary_lines.append(f"Needs Attention: {attention_total}")
            for status in attention_statuses:
                count = status_counts.get(status, 0)
                if count > 0:
                    summary_lines.append(f"  - {status}: {count}")

        # Terminal states
        terminal_statuses = ["COMPLETED", "FAILED", "CANCELLED"]
        for status in terminal_statuses:
            count = status_counts.get(status, 0)
            if count > 0:
                summary_lines.append(f"{status}: {count}")

        return "\n".join(summary_lines)

    def _format_task_list(
        self, tasks: List[dict], page: int = 1, total_pages: int = 1, total: int = 0
    ) -> str:
        """Format task list as markdown with summary and pagination."""
        if not tasks:
            return "No tasks found."

        output = []

        # Add summary
        summary = self._format_task_summary(tasks)
        if summary:
            output.append(summary)
            output.append("")

        # Pagination info
        if total_pages > 1:
            output.append(f"**Page {page} of {total_pages}** (Total: {total} tasks)")
            output.append("")

        output.append(f"**Recent Tasks ({len(tasks)}):**")
        output.append("")

        for task in tasks:
            status = task.get("status", "UNKNOWN")
            desc = task.get("description", "No description")
            if len(desc) > 60:
                desc = desc[:60] + "..."

            created = task.get("createdAt", "")
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                created_str = created_dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                created_str = created[:19].replace("T", " ") if created else "Unknown"

            priority = task.get("priority", "MEDIUM")

            output.append(f"**{status}** (Priority: {priority})")
            output.append(f"  - ID: `{task.get('id', 'N/A')}`")
            output.append(f"  - {desc}")
            output.append(f"  - Created: {created_str}")
            output.append("")

        return "\n".join(output)

    async def execute_task(
        self,
        task_description: str,
        priority: Optional[str] = None,
        wait_for_completion: Optional[bool] = None,
        __event_emitter__: Optional[Callable[[dict], Any]] = None,
        __user__: dict = {},
    ) -> str:
        """
        Execute an automation task on ByteBot.

        :param task_description: Natural language task description (e.g., "Download invoices from vendor portal")
        :param priority: Task urgency - LOW, MEDIUM, HIGH, or URGENT (defaults to user preference)
        :param wait_for_completion: Poll until done (True) or return task ID immediately (False)
        :return: Task execution results or task ID
        """
        # Use defaults from user preferences
        if priority is None:
            priority = self.user_valves.default_priority
        if wait_for_completion is None:
            wait_for_completion = self.user_valves.default_wait_for_completion

        emitter = EventEmitter(
            __event_emitter__, self.user_valves.notification_verbosity
        )

        # Validate inputs
        if not task_description or len(task_description.strip()) < 5:
            return "Error: Task description must be at least 5 characters."

        if priority not in ["LOW", "MEDIUM", "HIGH", "URGENT"]:
            return f"Error: Invalid priority '{priority}'. Must be LOW, MEDIUM, HIGH, or URGENT."

        await emitter.emit("Connecting to ByteBot...", done=False)

        # Submit task
        try:
            task_data = {
                "description": task_description,
                "priority": priority,
                "type": "IMMEDIATE",
                "control": "ASSISTANT",
                "model": self._get_model_config(),
            }

            task = await self._retry_request(
                "POST",
                f"{self.valves.bytebot_url}/tasks",
                emitter=emitter,
                json=task_data,
            )

            task_id = task.get("id")

            await emitter.emit(f"Task created: {task_id}", done=False)

            # Return immediately if not waiting
            if not wait_for_completion:
                await emitter.emit("Task submitted successfully", done=True)
                return f"Task submitted successfully.\n\n**Task ID:** `{task_id}`\n\nUse get_task_status('{task_id}') to check progress."

            # Poll for completion
            await emitter.emit("Monitoring task progress...", done=False)
            completed_task = await self._poll_task_completion(task_id, emitter)

            await emitter.emit("Task monitoring complete", done=True)

            # Handle special statuses
            if completed_task.get("status") == "TIMEOUT":
                return self._format_task_result(completed_task)
            elif completed_task.get("status") == "NEEDS_HELP":
                return ErrorFormatter.format_needs_help(task_id)
            elif completed_task.get("status") == "FAILED":
                messages = completed_task.get("messages", [])
                return ErrorFormatter.format_task_failed(task_id, messages)

            return self._format_task_result(completed_task)

        except aiohttp.ClientError as e:
            error_msg = ErrorFormatter.format_api_error(e, "task execution")
            await emitter.emit(error_msg, done=True)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            await emitter.emit(error_msg, done=True)
            return error_msg

    async def list_tasks(
        self,
        status_filter: Optional[str] = None,
        limit: Optional[int] = None,
        page: int = 1,
        __event_emitter__: Optional[Callable[[dict], Any]] = None,
    ) -> str:
        """
        List recent ByteBot automation tasks with pagination.

        :param status_filter: Filter by status (PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED, NEEDS_HELP, NEEDS_REVIEW)
        :param limit: Maximum tasks to return per page (defaults to user preference)
        :param page: Page number (1-based, default: 1)
        :return: Formatted list of tasks with summary and pagination
        """
        if limit is None:
            limit = self.user_valves.task_history_limit

        emitter = EventEmitter(
            __event_emitter__, self.user_valves.notification_verbosity
        )

        await emitter.emit("Fetching task list...", done=False)

        try:
            # Build query parameters
            params = {"page": str(page), "limit": str(limit)}
            if status_filter:
                params["status"] = status_filter.upper()

            response_data = await self._retry_request(
                "GET",
                f"{self.valves.bytebot_url}/tasks",
                emitter=emitter,
                params=params,
            )

            # Validate response structure
            if not self._validate_api_response(response_data, ["tasks"]):
                return "Error: Unexpected API response format. Please check ByteBot version compatibility."

            tasks = response_data.get("tasks", [])
            total = response_data.get("total", len(tasks))
            total_pages = response_data.get("totalPages", 1)

            # Client-side filtering if needed (server may not support status filter)
            if status_filter and "status" not in params:
                status_filter_upper = status_filter.upper()
                tasks = [t for t in tasks if t.get("status") == status_filter_upper]

            await emitter.emit(
                f"Found {len(tasks)} tasks (page {page}/{total_pages})", done=True
            )

            return self._format_task_list(tasks, page, total_pages, total)

        except aiohttp.ClientError as e:
            error_msg = ErrorFormatter.format_api_error(e, "listing tasks")
            await emitter.emit(error_msg, done=True)
            return error_msg
        except Exception as e:
            error_msg = f"Error listing tasks: {str(e)}"
            await emitter.emit(error_msg, done=True)
            return error_msg

    async def list_active_tasks(
        self,
        __event_emitter__: Optional[Callable[[dict], Any]] = None,
    ) -> str:
        """
        List only currently running tasks (PENDING, IN_PROGRESS, QUEUED).

        This is a convenience function that filters to show only tasks that are actively executing.

        :return: Formatted list of active tasks with summary
        """
        emitter = EventEmitter(
            __event_emitter__, self.user_valves.notification_verbosity
        )

        await emitter.emit("Fetching active tasks...", done=False)

        try:
            response_data = await self._retry_request(
                "GET", f"{self.valves.bytebot_url}/tasks", emitter=emitter
            )

            # Validate response structure
            if not self._validate_api_response(response_data, ["tasks"]):
                return "Error: Unexpected API response format. Please check ByteBot version compatibility."

            tasks = response_data.get("tasks", [])
            active_statuses = ["PENDING", "IN_PROGRESS", "QUEUED"]
            active_tasks = [t for t in tasks if t.get("status") in active_statuses]

            await emitter.emit(f"Found {len(active_tasks)} active tasks", done=True)

            if not active_tasks:
                return "No active tasks currently running."

            return self._format_task_list(active_tasks)

        except aiohttp.ClientError as e:
            error_msg = ErrorFormatter.format_api_error(e, "fetching active tasks")
            await emitter.emit(error_msg, done=True)
            return error_msg
        except Exception as e:
            error_msg = f"Error fetching active tasks: {str(e)}"
            await emitter.emit(error_msg, done=True)
            return error_msg

    async def get_available_models(
        self,
        __event_emitter__: Optional[Callable[[dict], Any]] = None,
    ) -> str:
        """
        Discover available AI models from recent ByteBot tasks.

        :return: Formatted list of available model configurations
        """
        emitter = EventEmitter(
            __event_emitter__, self.user_valves.notification_verbosity
        )

        try:
            await emitter.emit("Scanning tasks for available models...", done=False)

            response_data = await self._retry_request(
                "GET", f"{self.valves.bytebot_url}/tasks?page=1", emitter=emitter
            )

            if not self._validate_api_response(response_data, ["tasks"]):
                return "Error: Unexpected API response format."

            tasks = response_data.get("tasks", [])
            models = []
            seen = set()

            for task in tasks:
                model = task.get("model")
                if model and model.get("name") not in seen:
                    seen.add(model.get("name"))
                    models.append(
                        {
                            "name": model.get("name"),
                            "title": model.get("title"),
                            "provider": model.get("provider"),
                            "contextWindow": model.get("contextWindow"),
                        }
                    )

            await emitter.emit(f"Found {len(models)} model(s)", done=True)

            if not models:
                return f"""No model configurations found in recent tasks.

Current Default: {self.valves.default_model_name}

To set a custom model, update user preferences:
preferred_model_name: "openai/YourModelName"
"""

            output = ["Available Models:\n"]
            current_model = self._get_model_config()["name"]

            for i, model in enumerate(models, 1):
                is_current = model["name"] == current_model
                marker = " (Currently Selected)" if is_current else ""
                output.append(f"{i}. {model['title']}{marker}")
                output.append(f"   Name: {model['name']}")
                output.append(f"   Provider: {model['provider']}")
                output.append(f"   Context: {model['contextWindow']:,} tokens\n")

            output.append("\nTo use a different model:")
            output.append("Set preferred_model_name in user preferences")
            output.append(f"\nAdmin Default: {self.valves.default_model_name}")

            return "\n".join(output)

        except aiohttp.ClientError as e:
            error_msg = ErrorFormatter.format_api_error(e, "fetching models")
            await emitter.emit(error_msg, done=True)
            return error_msg
        except Exception as e:
            error_msg = f"Error discovering models: {str(e)}"
            await emitter.emit(error_msg, done=True)
            return error_msg

    async def get_task_status(
        self,
        task_id: str,
        include_messages: Optional[bool] = None,
        __event_emitter__: Optional[Callable[[dict], Any]] = None,
    ) -> str:
        """
        Check the status of a specific automation task.

        :param task_id: The task ID to check
        :param include_messages: Include execution message logs (defaults to user preference)
        :return: Current status and progress information
        """
        if include_messages is None:
            include_messages = self.user_valves.show_execution_logs

        emitter = EventEmitter(
            __event_emitter__, self.user_valves.notification_verbosity
        )

        await emitter.emit(f"Retrieving status for task {task_id}...", done=False)

        try:
            task = await self._retry_request(
                "GET", f"{self.valves.bytebot_url}/tasks/{task_id}", emitter=emitter
            )

            await emitter.emit("Status retrieved successfully", done=True)

            # Format based on include_messages preference
            if not include_messages:
                # Remove messages for cleaner output
                task_copy = task.copy()
                task_copy.pop("messages", None)
                return self._format_task_result(task_copy)

            return self._format_task_result(task)

        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                error_msg = f"Task not found: {task_id}"
            else:
                error_msg = ErrorFormatter.format_api_error(e, "retrieving task status")
            await emitter.emit(error_msg, done=True)
            return error_msg
        except aiohttp.ClientError as e:
            error_msg = ErrorFormatter.format_api_error(e, "retrieving task status")
            await emitter.emit(error_msg, done=True)
            return error_msg
        except Exception as e:
            error_msg = f"Error retrieving task status: {str(e)}"
            await emitter.emit(error_msg, done=True)
            return error_msg

    async def cancel_task(
        self,
        task_id: str,
        __event_emitter__: Optional[Callable[[dict], Any]] = None,
    ) -> str:
        """
        Cancel a running or pending ByteBot task.

        :param task_id: The task ID to cancel
        :return: Cancellation confirmation or error message
        """
        emitter = EventEmitter(
            __event_emitter__, self.user_valves.notification_verbosity
        )

        await emitter.emit(f"Cancelling task {task_id}...", done=False)

        try:
            session = await self._get_session()
            async with session.delete(
                f"{self.valves.bytebot_url}/tasks/{task_id}"
            ) as response:
                if response.status == 204:
                    await emitter.emit("Task cancelled successfully", done=True)
                    return f"Task cancelled successfully.\n\n**Task ID:** `{task_id}`"
                else:
                    response.raise_for_status()
                    return f"Task cancelled (status: {response.status}).\n\n**Task ID:** `{task_id}`"

        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                error_msg = f"Task not found: {task_id}"
            else:
                error_msg = ErrorFormatter.format_api_error(e, "cancelling task")
            await emitter.emit(error_msg, done=True)
            return error_msg
        except aiohttp.ClientError as e:
            error_msg = ErrorFormatter.format_api_error(e, "cancelling task")
            await emitter.emit(error_msg, done=True)
            return error_msg
        except Exception as e:
            error_msg = f"Error cancelling task: {str(e)}"
            await emitter.emit(error_msg, done=True)
            return error_msg

    async def execute_task_with_files(
        self,
        task_description: str,
        priority: Optional[str] = None,
        wait_for_completion: Optional[bool] = None,
        __files__: Optional[List] = None,
        __event_emitter__: Optional[Callable[[dict], Any]] = None,
        __user__: dict = {},
    ) -> str:
        """
        Execute a task with file uploads for processing.

        :param task_description: Task description (e.g., "Extract payment terms from these contracts")
        :param priority: Task urgency - LOW, MEDIUM, HIGH, URGENT (defaults to user preference)
        :param wait_for_completion: Poll until done (True) or return task ID immediately (False)
        :param __files__: List of uploaded FileModel objects from OpenWebUI
        :return: Task execution results with uploaded file processing outputs
        """
        # Use defaults from user preferences
        if priority is None:
            priority = self.user_valves.default_priority
        if wait_for_completion is None:
            wait_for_completion = self.user_valves.default_wait_for_completion

        emitter = EventEmitter(
            __event_emitter__, self.user_valves.notification_verbosity
        )

        if not __files__:
            return "Error: No files uploaded. Please attach files to your message."

        # Validate inputs
        if not task_description or len(task_description.strip()) < 5:
            return "Error: Task description must be at least 5 characters."

        if priority not in ["LOW", "MEDIUM", "HIGH", "URGENT"]:
            return f"Error: Invalid priority '{priority}'. Must be LOW, MEDIUM, HIGH, or URGENT."

        # Validate files
        validation_errors = []
        total_size = 0

        for file in __files__:
            # Get file size from content
            content = file.data.get("content", "")
            if isinstance(content, str):
                file_size_mb = len(content.encode("utf-8")) / (1024 * 1024)
            else:
                file_size_mb = len(content) / (1024 * 1024)

            total_size += file_size_mb

            if file_size_mb > self.valves.max_file_size_mb:
                validation_errors.append(
                    f"- {file.filename}: {file_size_mb:.1f}MB exceeds limit ({self.valves.max_file_size_mb}MB)"
                )

        if len(__files__) > self.valves.max_files_per_task:
            validation_errors.append(
                f"- Too many files ({len(__files__)}). Maximum: {self.valves.max_files_per_task}"
            )

        if validation_errors:
            return "File validation failed:\n" + "\n".join(validation_errors)

        await emitter.emit(
            f"Uploading {len(__files__)} files ({total_size:.1f}MB)...", done=False
        )

        try:
            # Build multipart form data
            form_data = aiohttp.FormData()
            form_data.add_field("description", task_description)
            form_data.add_field("priority", priority)
            form_data.add_field("type", "IMMEDIATE")
            form_data.add_field("control", "ASSISTANT")
            form_data.add_field("model", json.dumps(self._get_model_config()))

            for file in __files__:
                content = file.data.get("content", "")
                if isinstance(content, str):
                    content = content.encode("utf-8")

                content_type = file.meta.get("content_type", "application/octet-stream")

                form_data.add_field(
                    "files", content, filename=file.filename, content_type=content_type
                )

            # Submit task with files
            session = await self._get_session()
            async with session.post(
                f"{self.valves.bytebot_url}/tasks", data=form_data
            ) as response:
                response.raise_for_status()
                task = await response.json()

            task_id = task.get("id")

            await emitter.emit(f"Files uploaded. Task created: {task_id}", done=False)

            # Return immediately if not waiting
            if not wait_for_completion:
                await emitter.emit("Task submitted successfully", done=True)
                return f"Task with files submitted successfully.\n\n**Task ID:** `{task_id}`\n**Files:** {len(__files__)}\n\nUse get_task_status('{task_id}') to check progress."

            # Poll for completion
            await emitter.emit("Monitoring task progress...", done=False)
            completed_task = await self._poll_task_completion(task_id, emitter)

            await emitter.emit("Task monitoring complete", done=True)

            # Handle special statuses
            if completed_task.get("status") == "TIMEOUT":
                return self._format_task_result(completed_task)
            elif completed_task.get("status") == "NEEDS_HELP":
                return ErrorFormatter.format_needs_help(task_id)
            elif completed_task.get("status") == "FAILED":
                messages = completed_task.get("messages", [])
                return ErrorFormatter.format_task_failed(task_id, messages)

            result = self._format_task_result(completed_task)
            return f"**Files Processed:** {len(__files__)} files\n\n{result}"

        except aiohttp.ClientError as e:
            error_msg = ErrorFormatter.format_api_error(e, "task execution with files")
            await emitter.emit(error_msg, done=True)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            await emitter.emit(error_msg, done=True)
            return error_msg

    async def check_connection(
        self,
        __event_emitter__: Optional[Callable[[dict], Any]] = None,
    ) -> str:
        """
        Verify ByteBot connectivity and display available information.

        :return: Connection status, API availability, configured models
        """
        emitter = EventEmitter(
            __event_emitter__, self.user_valves.notification_verbosity
        )

        await emitter.emit("Checking ByteBot connection...", done=False)

        diagnostics = []

        # Test ByteBot Agent API
        try:
            session = await self._get_session()
            start_time = time.time()

            async with session.get(f"{self.valves.bytebot_url}/tasks") as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    response_data = await response.json()

                    # Validate response structure
                    if self._validate_api_response(response_data, ["tasks"]):
                        tasks_list = response_data.get("tasks", [])
                        total_tasks = response_data.get("total", len(tasks_list))

                        # Count actually active tasks (running now)
                        active_statuses = ["PENDING", "IN_PROGRESS", "QUEUED"]
                        active_count = sum(
                            1 for t in tasks_list if t.get("status") in active_statuses
                        )

                        # Count tasks needing attention
                        attention_statuses = ["NEEDS_HELP", "NEEDS_REVIEW"]
                        attention_count = sum(
                            1
                            for t in tasks_list
                            if t.get("status") in attention_statuses
                        )

                        diagnostics.append(
                            f"Connection successful ({response_time:.2f}s)"
                        )
                        diagnostics.append(f"Status: {response.status} OK")
                        diagnostics.append(f"Running tasks: {active_count}")
                        if attention_count > 0:
                            diagnostics.append(f"Needs attention: {attention_count}")
                        diagnostics.append(f"Total tasks (all time): {total_tasks}")
                    else:
                        # Fallback for older API format
                        diagnostics.append(
                            f"Connection successful ({response_time:.2f}s)"
                        )
                        diagnostics.append(f"Status: {response.status} OK")
                        diagnostics.append(
                            "Note: Unable to parse task count (API format changed)"
                        )
                else:
                    diagnostics.append(
                        f"Connection established but returned status {response.status}"
                    )

        except asyncio.TimeoutError:
            diagnostics.append("Connection timeout (>10s)")
            diagnostics.append("Possible causes:")
            diagnostics.append("- Slow network connection")
            diagnostics.append("- Service overload")
            diagnostics.append("- Firewall blocking requests")

        except aiohttp.ClientConnectorError as e:
            diagnostics.append(f"Connection failed: {str(e)}")
            diagnostics.append("Possible causes:")
            diagnostics.append("- ByteBot not running")
            diagnostics.append("- Network unreachable")
            diagnostics.append("- Incorrect URL configuration")

        except Exception as e:
            diagnostics.append(f"Unexpected error: {str(e)}")

        # Check LiteLLM proxy if configured
        if self.valves.litellm_proxy_url:
            diagnostics.append("")
            diagnostics.append("**LiteLLM Proxy Check:**")
            try:
                async with session.get(
                    f"{self.valves.litellm_proxy_url}/model/info"
                ) as response:
                    if response.status == 200:
                        model_info = await response.json()
                        diagnostics.append(f"LiteLLM proxy available")
                        # Extract model names if available
                        if isinstance(model_info, dict):
                            diagnostics.append(f"Response: {str(model_info)[:100]}")
                    else:
                        diagnostics.append(
                            f"LiteLLM proxy returned status {response.status}"
                        )
            except Exception as e:
                diagnostics.append(f"LiteLLM proxy not accessible: {str(e)}")

        # Show configured models
        diagnostics.append("")
        diagnostics.append("**Configured Models:**")
        diagnostics.append(self.valves.configured_models)

        # Show configuration
        diagnostics.append("")
        diagnostics.append("**Configuration:**")
        diagnostics.append(f"ByteBot URL: {self.valves.bytebot_url}")
        diagnostics.append(f"Task timeout: {self.valves.task_timeout_seconds}s")
        diagnostics.append(f"Max retries: {self.valves.max_retries}")

        await emitter.emit("Connection check complete", done=True)

        return "\n".join(diagnostics)
