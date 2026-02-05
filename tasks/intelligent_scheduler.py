"""
Intelligent Task Scheduler for Claw Personal Assistant

Implements an advanced task scheduling system with dynamic priority adjustment
based on community best practices and autonomous decision making.
"""

import asyncio
import heapq
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from uuid import uuid4


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """Represents a scheduled task with metadata"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    coroutine: Callable = None
    priority: TaskPriority = TaskPriority.NORMAL
    scheduled_time: datetime = field(default_factory=datetime.now)
    created_time: datetime = field(default_factory=datetime.now)
    estimated_duration: int = 0  # in seconds
    dependencies: List[str] = field(default_factory=list)  # task IDs this task depends on
    max_attempts: int = 3
    current_attempt: int = 0
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Exception = None
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # Priority queue uses min-heap, so we negate the priority value
        # Higher priority value gets lower numeric value for heap ordering
        self.heap_priority = -self.priority.value
        self.heap_time = self.scheduled_time.timestamp()

    def __lt__(self, other):
        """Compare tasks for priority queue ordering"""
        # Primary sort: priority (higher priority first)
        # Secondary sort: scheduled time (earlier time first)
        if self.heap_priority != other.heap_priority:
            return self.heap_priority < other.heap_priority
        return self.heap_time < other.heap_time


class IntelligentScheduler:
    """Advanced task scheduler with dynamic priority adjustment"""
    
    def __init__(self, assistant):
        self.assistant = assistant
        self.logger = logging.getLogger(f"{assistant.name}.IntelligentScheduler")
        self.task_queue = []  # Min-heap for priority scheduling
        self.active_tasks = {}  # Currently executing tasks
        self.completed_tasks = {}  # Completed tasks
        self.failed_tasks = {}  # Failed tasks
        self.task_registry = {}  # All known tasks
        self.is_running = False
        self.scheduler_task = None
        
    def schedule_task(
        self,
        name: str,
        coroutine: Callable,
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: int = 0,
        tags: List[str] = None,
        dependencies: List[str] = None,
        max_attempts: int = 3
    ) -> str:
        """Schedule a task for execution"""
        scheduled_time = datetime.now() + timedelta(seconds=delay_seconds)
        
        task = ScheduledTask(
            name=name,
            coroutine=coroutine,
            priority=priority,
            scheduled_time=scheduled_time,
            max_attempts=max_attempts,
            tags=tags or [],
            dependencies=dependencies or []
        )
        
        self.task_registry[task.id] = task
        
        # Add to priority queue if no dependencies or dependencies are satisfied
        if not self._has_unmet_dependencies(task):
            heapq.heappush(self.task_queue, task)
            self.logger.info(f"Scheduled task '{name}' (ID: {task.id}) for execution at {scheduled_time}")
        else:
            self.logger.info(f"Task '{name}' (ID: {task.id}) waiting for dependencies")
        
        return task.id
    
    def _has_unmet_dependencies(self, task: ScheduledTask) -> bool:
        """Check if a task has unmet dependencies"""
        for dep_id in task.dependencies:
            dep_task = self.task_registry.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return True
        return False
    
    def adjust_priority(self, task_id: str, new_priority: TaskPriority):
        """Dynamically adjust task priority"""
        task = self.task_registry.get(task_id)
        if not task:
            self.logger.warning(f"Cannot adjust priority: task {task_id} not found")
            return False
            
        old_priority = task.priority
        task.priority = new_priority
        task.heap_priority = -new_priority.value
        
        # If task is in the queue, we need to rebuild the heap
        # (simple approach: recreate the heap with updated priorities)
        if task in [item for item in self.task_queue]:
            # Remove and re-add to update heap position
            self.task_queue = [t for t in self.task_queue if t.id != task_id]
            heapq.heappush(self.task_queue, task)
            heapq.heapify(self.task_queue)  # Re-heapify to maintain heap property
        
        self.logger.info(f"Adjusted priority for task '{task.name}' from {old_priority.name} to {new_priority.name}")
        return True
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        task = self.task_registry.get(task_id)
        if not task:
            self.logger.warning(f"Cannot cancel task: task {task_id} not found")
            return False
            
        if task.status == TaskStatus.RUNNING:
            self.logger.warning(f"Cannot cancel task '{task.name}' as it is currently running")
            return False
            
        # Remove from queue if present
        self.task_queue = [t for t in self.task_queue if t.id != task_id]
        
        task.status = TaskStatus.CANCELLED
        self.logger.info(f"Cancelled task '{task.name}' (ID: {task_id})")
        return True
    
    async def _execute_task(self, task: ScheduledTask) -> bool:
        """Execute a single task"""
        if task.id in self.active_tasks:
            self.logger.warning(f"Task {task.id} is already running")
            return False
            
        task.status = TaskStatus.RUNNING
        self.active_tasks[task.id] = task
        
        self.logger.info(f"Starting execution of task '{task.name}' (ID: {task.id})")
        
        try:
            # Execute the task coroutine
            start_time = datetime.now()
            result = await task.coroutine()
            duration = (datetime.now() - start_time).total_seconds()
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            self.completed_tasks[task.id] = task
            self.logger.info(f"Completed task '{task.name}' (ID: {task.id}) in {duration:.2f}s")
            
            # Check if any dependent tasks can now be scheduled
            self._check_dependent_tasks(task.id)
            
            return True
            
        except Exception as e:
            task.error = e
            task.current_attempt += 1
            
            if task.current_attempt < task.max_attempts:
                self.logger.warning(f"Task '{task.name}' (ID: {task.id}) failed (attempt {task.current_attempt}/{task.max_attempts}): {str(e)}")
                # Re-schedule with exponential backoff
                delay = 2 ** task.current_attempt  # Exponential backoff
                self.schedule_task(
                    name=task.name,
                    coroutine=task.coroutine,
                    priority=TaskPriority.HIGH if task.priority == TaskPriority.CRITICAL else task.priority,
                    delay_seconds=delay,
                    tags=task.tags,
                    max_attempts=task.max_attempts
                )
            else:
                task.status = TaskStatus.FAILED
                self.failed_tasks[task.id] = task
                self.logger.error(f"Task '{task.name}' (ID: {task.id}) failed permanently after {task.max_attempts} attempts: {str(e)}")
            
            return False
        finally:
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
    
    def _check_dependent_tasks(self, completed_task_id: str):
        """Check if any tasks were waiting for this task to complete"""
        for task_id, task in self.task_registry.items():
            if task.status == TaskStatus.PENDING and completed_task_id in task.dependencies:
                # Check if all dependencies are now satisfied
                if not self._has_unmet_dependencies(task):
                    # Add to queue since dependencies are met
                    heapq.heappush(self.task_queue, task)
                    self.logger.info(f"Dependencies satisfied for task '{task.name}', adding to queue")
    
    async def run_scheduler(self):
        """Main scheduler loop"""
        self.logger.info("Starting intelligent task scheduler")
        self.is_running = True
        
        try:
            while self.is_running:
                # Process all eligible tasks
                await self._process_ready_tasks()
                
                # Wait a bit before checking again
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            self.logger.info("Task scheduler was cancelled")
        except Exception as e:
            self.logger.error(f"Error in task scheduler: {e}")
        finally:
            self.is_running = False
            self.logger.info("Task scheduler stopped")
    
    async def _process_ready_tasks(self):
        """Process tasks that are ready for execution"""
        # Get current time
        now = datetime.now()
        
        # Process all tasks that are scheduled for now or earlier
        ready_tasks = []
        
        # Temporarily clear the queue to check all tasks
        temp_queue = []
        while self.task_queue:
            task = heapq.heappop(self.task_queue)
            if task.scheduled_time <= now:
                ready_tasks.append(task)
            else:
                temp_queue.append(task)
        
        # Put back the non-ready tasks
        for task in temp_queue:
            heapq.heappush(self.task_queue, task)
        
        # Execute ready tasks
        for task in ready_tasks:
            # Execute task in the background
            asyncio.create_task(self._execute_task(task))
    
    def get_task_status(self, task_id: str) -> Optional[ScheduledTask]:
        """Get status of a specific task"""
        return self.task_registry.get(task_id)
    
    def get_all_tasks(self) -> List[ScheduledTask]:
        """Get all tasks"""
        return list(self.task_registry.values())
    
    def get_active_tasks(self) -> List[ScheduledTask]:
        """Get currently active tasks"""
        return list(self.active_tasks.values())
    
    def get_completed_tasks(self) -> List[ScheduledTask]:
        """Get completed tasks"""
        return list(self.completed_tasks.values())
    
    def get_failed_tasks(self) -> List[ScheduledTask]:
        """Get failed tasks"""
        return list(self.failed_tasks.values())
    
    def start(self):
        """Start the scheduler in the background"""
        if not self.is_running:
            self.scheduler_task = asyncio.create_task(self.run_scheduler())
            self.logger.info("Task scheduler started in background")
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            self.logger.info("Task scheduler stopping")