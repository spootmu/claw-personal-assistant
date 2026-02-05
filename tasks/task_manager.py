"""
Task Manager for Claw Personal Assistant

Implements high-level task management and orchestration based on community insights
about autonomous systems and task scheduling best practices.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any, Optional
from enum import Enum

from .intelligent_scheduler import IntelligentScheduler, TaskPriority, ScheduledTask


class TaskCategory(Enum):
    """Categories of tasks for better organization"""
    SYSTEM = "system"
    COMMUNITY = "community"
    LEARNING = "learning"
    MONITORING = "monitoring"
    MAINTENANCE = "maintenance"
    DEVELOPMENT = "development"


class TaskManager:
    """High-level task management and orchestration"""
    
    def __init__(self, assistant):
        self.assistant = assistant
        self.logger = logging.getLogger(f"{assistant.name}.TaskManager")
        self.scheduler = assistant.intelligent_scheduler
        self.task_categories = {}
        self.performance_metrics = {}
        
    async def create_adaptive_task(
        self,
        name: str,
        coroutine: Callable,
        category: TaskCategory,
        priority: TaskPriority = TaskPriority.NORMAL,
        estimated_duration: int = 30,
        tags: List[str] = None,
        dependencies: List[str] = None,
        auto_reschedule: bool = True
    ) -> str:
        """Create a task with adaptive scheduling based on performance"""
        # Register the task category
        if category not in self.task_categories:
            self.task_categories[category] = []
        
        # Schedule the task
        task_id = self.scheduler.schedule_task(
            name=name,
            coroutine=coroutine,
            priority=priority,
            delay_seconds=0,
            tags=tags or [],
            dependencies=dependencies or [],
            max_attempts=3
        )
        
        # Record task in category
        self.task_categories[category].append(task_id)
        
        # Initialize performance metrics
        self.performance_metrics[task_id] = {
            "created_at": datetime.now(),
            "attempts": 0,
            "success_count": 0,
            "failure_count": 0,
            "avg_duration": 0,
            "estimated_duration": estimated_duration
        }
        
        self.logger.info(f"Created adaptive task '{name}' (ID: {task_id}) in category {category.value}")
        return task_id
    
    async def optimize_task_priorities(self):
        """Dynamically adjust task priorities based on performance and community insights"""
        self.logger.info("Optimizing task priorities based on performance metrics")
        
        for task_id, metrics in self.performance_metrics.items():
            task = self.scheduler.get_task_status(task_id)
            if not task:
                continue
                
            # Calculate performance score
            success_rate = 0
            if (metrics["success_count"] + metrics["failure_count"]) > 0:
                success_rate = metrics["success_count"] / (metrics["success_count"] + metrics["failure_count"])
            
            # Adjust priority based on various factors
            new_priority = task.priority
            
            # Increase priority if task is critical and has high success rate
            if "critical" in task.tags and success_rate > 0.9:
                new_priority = TaskPriority.HIGH
            
            # Decrease priority if task frequently fails
            if metrics["failure_count"] > metrics["success_count"] and metrics["failure_count"] > 2:
                new_priority = TaskPriority.LOW
            
            # Adjust based on deadline urgency (if applicable)
            if hasattr(task, 'deadline'):
                time_to_deadline = (task.deadline - datetime.now()).total_seconds()
                if 0 < time_to_deadline < 300:  # Less than 5 minutes
                    new_priority = TaskPriority.CRITICAL
            
            # Apply the new priority if it changed
            if new_priority != task.priority:
                self.scheduler.adjust_priority(task_id, new_priority)
                self.logger.info(f"Adjusted priority for '{task.name}' from {task.priority.name} to {new_priority.name}")
    
    async def schedule_nightly_builds(self):
        """Schedule proactive tasks to run during off-hours (nightly builds concept from community)"""
        self.logger.info("Scheduling nightly build tasks")
        
        # Example nightly tasks based on community best practices
        
        # Task 1: Memory consolidation and cleanup
        async def nightly_memory_cleanup():
            self.logger.info("Starting nightly memory consolidation")
            
            # Consolidate recent learnings
            learnings = self.assistant.memory_system.database.search_learnings("", limit=50)
            if learnings:
                # Store consolidated learnings
                self.assistant.memory_system.store_learning(
                    f"Consolidated {len(learnings)} learnings from the day",
                    source="nightly_cleanup",
                    tags=["consolidation", "memory"]
                )
            
            # Clean up old interactions to prevent bloat
            # (would implement actual cleanup logic here)
            
            self.logger.info("Completed nightly memory consolidation")
            return {"status": "completed", "task": "memory_cleanup"}
        
        # Schedule for 2 AM (off-hours)
        now = datetime.now()
        # Calculate time until next 2 AM
        target_time = now.replace(hour=2, minute=0, second=0, microsecond=0)
        if target_time <= now:  # If we've passed 2 AM today, schedule for tomorrow
            target_time += timedelta(days=1)
        
        delay_seconds = int((target_time - now).total_seconds())
        
        await self.create_adaptive_task(
            name="nightly_memory_cleanup",
            coroutine=nightly_memory_cleanup,
            category=TaskCategory.MAINTENANCE,
            priority=TaskPriority.NORMAL,
            tags=["nightly", "cleanup", "memory"]
        )
        
        # Task 2: Community insight processing
        async def nightly_community_processing():
            self.logger.info("Starting nightly community insight processing")
            
            async with self.assistant.community_integration as ci:
                # Process community insights
                await ci.process_community_insights()
                
                # Apply insights to improve functionality
                topics_to_check = ["autonomous", "ai", "agent", "task", "scheduling", "memory", "learning", "security"]
                
                for topic in topics_to_check:
                    await self.assistant.apply_community_insights(topic)
            
            self.logger.info("Completed nightly community processing")
            return {"status": "completed", "task": "community_processing"}
        
        # Schedule for 3 AM
        target_time_2 = now.replace(hour=3, minute=0, second=0, microsecond=0)
        if target_time_2 <= now:
            target_time_2 += timedelta(days=1)
        
        delay_seconds_2 = int((target_time_2 - now).total_seconds())
        
        await self.create_adaptive_task(
            name="nightly_community_processing",
            coroutine=nightly_community_processing,
            category=TaskCategory.LEARNING,
            priority=TaskPriority.NORMAL,
            tags=["nightly", "community", "learning"]
        )
        
        self.logger.info("Scheduled nightly build tasks")
    
    async def monitor_task_performance(self):
        """Monitor and record task performance metrics"""
        while True:
            try:
                # Process completed tasks to update metrics
                completed_tasks = self.scheduler.get_completed_tasks()
                
                for task in completed_tasks:
                    if task.id in self.performance_metrics:
                        metrics = self.performance_metrics[task.id]
                        
                        # Update success counter
                        metrics["success_count"] += 1
                        metrics["attempts"] += 1
                        
                        # Would calculate duration if we had start/end timestamps
                        # For now, we'll just log the completion
                        self.logger.debug(f"Updated metrics for completed task: {task.name}")
                
                # Process failed tasks
                failed_tasks = self.scheduler.get_failed_tasks()
                
                for task in failed_tasks:
                    if task.id in self.performance_metrics:
                        metrics = self.performance_metrics[task.id]
                        
                        # Update failure counter
                        metrics["failure_count"] += 1
                        metrics["attempts"] += 1
                        
                        self.logger.warning(f"Updated metrics for failed task: {task.name}")
                
                # Optimize priorities periodically
                await self.optimize_task_priorities()
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in task performance monitoring: {e}")
                await asyncio.sleep(60)
    
    async def start_background_services(self):
        """Start background services for task management"""
        self.logger.info("Starting background task management services")
        
        # Start performance monitoring in background
        asyncio.create_task(self.monitor_task_performance())
        
        # Schedule nightly builds
        await self.schedule_nightly_builds()
        
        self.logger.info("Background services started")