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
from typing import Dict, Any, Callable


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
    
    def __init__(self, storage_path: str = "./memory.json"):
        self.storage_path = storage_path
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memory: {e}")
        return {"interactions": [], "learnings": [], "preferences": {}}
        
    def _save_memory(self):
        """Save memory to storage"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving memory: {e}")
            
    def store_interaction(self, interaction: Dict[str, Any]):
        """Store an interaction in memory"""
        self.memory["interactions"].append({
            "timestamp": datetime.now().isoformat(),
            **interaction
        })
        # Keep only last 100 interactions to prevent memory bloat
        if len(self.memory["interactions"]) > 100:
            self.memory["interactions"] = self.memory["interactions"][-100:]
        self._save_memory()
        
    def store_learning(self, learning: str):
        """Store a learning in memory"""
        self.memory["learnings"].append({
            "timestamp": datetime.now().isoformat(),
            "learning": learning
        })
        self._save_memory()


class ClawAssistant:
    """
    Main class for the Claw Personal Assistant
    """
    
    def __init__(self):
        self.name = "Claw"
        self.version = "0.2.0"
        self.created_at = datetime.now()
        self.logger = self._setup_logger()
        self.task_engine = TaskEngine(self)
        self.memory_system = MemorySystem()
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
        
    async def _register_default_tasks(self):
        """Register default tasks"""
        # Example task: periodic health check
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        await self.task_engine.register_task("health_check", health_check, "every_5_minutes")
        
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


async def main():
    """Main entry point"""
    assistant = ClawAssistant()
    try:
        await assistant.run()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")


if __name__ == "__main__":
    asyncio.run(main())