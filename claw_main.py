#!/usr/bin/env python3
"""
Claw Personal Assistant - Main Module

This is the core module for the Claw Personal Assistant project.
Designed to handle autonomous operations and enhanced capabilities.
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Callable, List

# Import the new community integration module
from community_integration import CommunityIntegration
# Import the community monitoring task
from tasks.community_monitor_task import CommunityMonitorTask
# Import the database module
from database import DatabaseManager
# Import the intelligent scheduler
from tasks.intelligent_scheduler import IntelligentScheduler, TaskPriority
# Import the task manager
from tasks.task_manager import TaskManager
# Import the learning system
from learning_system import LearningSystem


class TaskEngine:
    """Handles execution of various tasks"""
    
    def __init__(self, assistant):
        self.assistant = assistant
        self.tasks = {}
        self.running_tasks = []
        
    async def register_task(self, name: str, coroutine: Callable, schedule: str = None):
        """Register a task with optional schedule"""
        self.tasks[name] = {
            'coroutine': coroutine,
            'schedule': schedule,
            'last_run': None
        }
        
    async def execute_task(self, name: str):
        """Execute a registered task"""
        if name in self.tasks:
            task = self.tasks[name]
            self.assistant.logger.info(f"Executing task: {name}")
            try:
                result = await task['coroutine']()
                task['last_run'] = datetime.now()
                return result
            except Exception as e:
                self.assistant.logger.error(f"Task {name} failed: {str(e)}")
                return None


class MemorySystem:
    """Handles persistent memory and learning"""
    
    def __init__(self, storage_path: str = "./memory.json", db_path: str = "./claw_data.db"):
        self.storage_path = storage_path
        self.database = DatabaseManager(db_path)
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memory: {e}")
        return {
            "interactions": [], 
            "learnings": [], 
            "preferences": {},
            "knowledge_base": [],
            "community_insights": []  # New: Store insights from community like Moltbook
        }
        
    def _save_memory(self):
        """Save memory to storage"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving memory: {e}")
            
    def store_interaction(self, interaction: Dict[str, Any]):
        """Store an interaction in memory"""
        # Store in JSON for immediate access
        self.memory["interactions"].append({
            "timestamp": datetime.now().isoformat(),
            **interaction
        })
        # Keep only last 100 interactions to prevent memory bloat
        if len(self.memory["interactions"]) > 100:
            self.memory["interactions"] = self.memory["interactions"][-100:]
        self._save_memory()
        
        # Also store in database for structured access
        user_input = interaction.get('user_input', '')
        assistant_response = interaction.get('assistant_response', '')
        context = {k: v for k, v in interaction.items() if k not in ['user_input', 'assistant_response']}
        self.database.store_interaction(user_input, assistant_response, context)
        
    def store_learning(self, learning: str, source: str = None, tags: List[str] = None):
        """Store a learning in memory"""
        # Store in JSON for immediate access
        self.memory["learnings"].append({
            "timestamp": datetime.now().isoformat(),
            "learning": learning
        })
        self._save_memory()
        
        # Also store in database for structured access
        self.database.store_learning(learning, source, tags)
        
    def store_community_insight(self, source: str, topic: str, insight: str):
        """Store insights from community sources like Moltbook"""
        # Store in JSON for immediate access
        insight_entry = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "topic": topic,
            "insight": insight
        }
        self.memory["community_insights"].append(insight_entry)
        
        # Keep only last 50 insights to prevent memory bloat
        if len(self.memory["community_insights"]) > 50:
            self.memory["community_insights"] = self.memory["community_insights"][-50:]
        
        self._save_memory()
        self.logger.info(f"Stored community insight from {source} about {topic}")
        
        # Also store in database for structured access
        self.database.store_community_insight(source, topic, insight)
        
    def get_relevant_knowledge(self, topic: str) -> list:
        """Retrieve relevant knowledge from memory"""
        relevant_items = []
        
        # Search in JSON memory
        for item in self.memory["learnings"]:
            if topic.lower() in item.get("learning", "").lower():
                relevant_items.append(item)
                
        # Search in community insights
        for item in self.memory["community_insights"]:
            if topic.lower() in item.get("topic", "").lower() or topic.lower() in item.get("insight", "").lower():
                relevant_items.append(item)
        
        # Also search in database for more comprehensive results
        db_results = self.database.search_learnings(topic, limit=5)
        for item in db_results:
            relevant_items.append({
                "timestamp": item["timestamp"],
                "learning": item["learning_content"],
                "source": item["source"],
                "relevance_score": item["relevance_score"]
            })
        
        return relevant_items


class ClawAssistant:
    """
    Main class for the Claw Personal Assistant
    """
    
    def __init__(self):
        self.name = "Claw"
        self.version = "0.6.0"
        self.created_at = datetime.now()
        self.logger = self._setup_logger()
        self.task_engine = TaskEngine(self)
        self.intelligent_scheduler = IntelligentScheduler(self)  # New: Advanced task scheduler
        self.task_manager = None  # Will be initialized in _initialize_components
        self.learning_system = None  # Will be initialized in _initialize_components
        self.memory_system = MemorySystem()
        self.community_integration = None  # Will be initialized in _initialize_components
        self.config = self._load_config()
        
    def _setup_logger(self):
        """Setup basic logging"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = "./config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load config: {e}")
        # Return default config
        return {
            "debug_mode": False,
            "max_workers": 4,
            "auto_update": True
        }
    
    async def initialize(self):
        """Initialize the assistant"""
        self.logger.info(f"Initializing {self.name} v{self.version}")
        
        # Initialize components
        await self._initialize_components()
        
        # Register default tasks
        await self._register_default_tasks()
        
        self.logger.info("Initialization complete")
        
    async def _initialize_components(self):
        """Initialize all components"""
        self.logger.info("Initializing components...")
        
        # Initialize community integration
        self.community_integration = CommunityIntegration(self)
        self.logger.info("Community integration initialized")
        
        # Initialize intelligent scheduler
        self.intelligent_scheduler.start()
        self.logger.info("Intelligent scheduler started")
        
        # Initialize task manager
        self.task_manager = TaskManager(self)
        await self.task_manager.start_background_services()
        self.logger.info("Task manager started with background services")
        
        # Initialize learning system
        self.learning_system = LearningSystem(self)
        self.learning_system.start_learning_cycle()
        self.logger.info("Learning system started with continuous learning cycle")
        
        # Perform initial community insight processing
        async with self.community_integration as ci:
            await ci.process_community_insights()
        
    async def _register_default_tasks(self):
        """Register default tasks"""
        # Example task: periodic health check
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        await self.task_engine.register_task("health_check", health_check, "every_5_minutes")
        
        # Register community monitoring task with intelligent scheduler
        self.community_monitor = CommunityMonitorTask(self)
        async def run_community_monitor():
            # Run the community monitor for a short period then return
            task = asyncio.create_task(self.community_monitor.run())
            # Let it run briefly then return
            await asyncio.sleep(1)  # Short delay to allow task to start
            return {"status": "community_monitor_started", "timestamp": datetime.now().isoformat()}
        
        # Schedule with the intelligent scheduler
        self.intelligent_scheduler.schedule_task(
            name="community_monitor",
            coroutine=run_community_monitor,
            priority=TaskPriority.NORMAL,
            delay_seconds=0,
            tags=["community", "monitoring"]
        )
        
        # Schedule periodic health checks with the intelligent scheduler
        async def scheduled_health_check():
            result = await health_check()
            self.logger.info(f"Health check result: {result}")
            return result
        
        # Schedule health checks to run every 5 minutes
        import threading
        def schedule_periodic_health_checks():
            async def run_periodic():
                while True:
                    try:
                        await scheduled_health_check()
                        await asyncio.sleep(300)  # 5 minutes
                    except Exception as e:
                        self.logger.error(f"Error in periodic health check: {e}")
                        await asyncio.sleep(300)  # Still wait 5 minutes before retry
            
            asyncio.create_task(run_periodic())
        
        # Start the periodic health checks in the background
        schedule_periodic_health_checks()
        
        self.logger.info("Default tasks registered with intelligent scheduler")
        
    async def run(self):
        """Main run loop"""
        await self.initialize()
        self.logger.info("Assistant running...")
        
        # Run startup tasks
        await self.task_engine.execute_task("health_check")
        
        # Main loop would go here
        while True:
            # Perform periodic tasks
            await asyncio.sleep(60)  # Sleep for 1 minute
            
    def status(self):
        """Return current status"""
        return {
            "name": self.name,
            "version": self.version,
            "uptime": datetime.now() - self.created_at,
            "status": "running",
            "components": {
                "task_engine": "loaded",
                "memory_system": "loaded",
                "config": "loaded"
            }
        }
        
    def store_interaction(self, interaction: Dict[str, Any]):
        """Store an interaction in memory"""
        self.memory_system.store_interaction(interaction)
        
    def store_learning(self, learning: str):
        """Store a learning in memory"""
        self.memory_system.store_learning(learning)
        
    async def apply_community_insights(self, topic: str):
        """Apply insights from community to improve functionality"""
        async with self.community_integration as ci:
            relevant_info = await ci.get_relevant_community_info(topic)
            
            if relevant_info:
                self.logger.info(f"Found {len(relevant_info)} relevant insights for topic '{topic}'")
                
                for info in relevant_info:
                    insight_text = f"From {info['source']} - {info['topic']}: {info['content']}"
                    self.store_community_insight(info['source'], info['topic'], info['content'])
                    
                    # Apply the insight to improve functionality
                    if 'modular' in insight_text.lower() and 'architecture' in insight_text.lower():
                        self.logger.info("Applying modular architecture insight to enhance design")
                        # Implementation would go here
                        
                    elif 'task queue' in insight_text.lower() or 'priority' in insight_text.lower():
                        self.logger.info("Applying task scheduling insight to enhance TaskEngine")
                        # Implementation would go here
                        
                    elif 'memory' in insight_text.lower() and 'performance' in insight_text.lower():
                        self.logger.info("Applying memory management insight to enhance MemorySystem")
                        # Implementation would go here
                    
                    # Process the insight through the learning system
                    if self.learning_system:
                        await self.learning_system.process_community_insight(
                            insight_source=info['source'],
                            topic=info['topic'],
                            content=info['content']
                        )
            else:
                self.logger.info(f"No relevant insights found for topic '{topic}'")
                
        # Also apply insights to the learning system
        if self.learning_system:
            await self.learning_system.process_community_insight(
                insight_source="internal",
                topic=topic,
                content=f"Applied community insights for topic: {topic}"
            )
                
    def store_community_insight(self, source: str, topic: str, insight: str):
        """Store community insight in memory"""
        self.memory_system.store_community_insight(source, topic, insight)


async def main():
    """Main entry point"""
    assistant = ClawAssistant()
    try:
        await assistant.run()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")


if __name__ == "__main__":
    asyncio.run(main())