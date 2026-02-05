"""
Learning System for Claw Personal Assistant

Implements continuous learning and improvement based on task execution results,
community insights, and autonomous decision making.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from database import DatabaseManager


@dataclass
class LearningExperience:
    """Represents a learning experience from task execution or other activities"""
    id: str
    timestamp: datetime
    experience_type: str  # 'task_result', 'community_insight', 'user_interaction', etc.
    content: str
    source: str
    tags: List[str]
    relevance_score: float = 1.0
    applicability_score: float = 1.0
    improvement_opportunities: List[str] = None


class LearningSystem:
    """Continuous learning and improvement system"""
    
    def __init__(self, assistant, db_path: str = "./learning_data.db"):
        self.assistant = assistant
        self.logger = logging.getLogger(f"{assistant.name}.LearningSystem")
        self.database = DatabaseManager(db_path)
        self.learning_experiences = []
        self.knowledge_graph = {}  # Simple knowledge graph representation
        self.improvement_strategies = []
        self.is_active = True
        
    async def process_task_result(self, task_id: str, result: Any, success: bool):
        """Process the result of a task execution to extract learning"""
        if not self.is_active:
            return
            
        self.logger.info(f"Processing task result for task {task_id}, success: {success}")
        
        # Get task details
        task = self.assistant.intelligent_scheduler.get_task_status(task_id)
        if not task:
            self.logger.warning(f"Could not find task {task_id} for learning")
            return
            
        # Create learning experience based on task result
        content = f"Task '{task.name}' executed with result: {result}. Success: {success}."
        if task.error:
            content += f" Error: {str(task.error)}"
            
        experience = LearningExperience(
            id=f"task_{task_id}_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            experience_type="task_result",
            content=content,
            source="task_execution",
            tags=["task", "execution", "result"] + task.tags,
            relevance_score=1.0 if success else 0.7,
            applicability_score=0.8 if success else 0.5
        )
        
        # Add improvement opportunities if task failed
        if not success and task.error:
            error_msg = str(task.error)
            improvement_opps = self._identify_improvements_from_error(error_msg, task.name)
            experience.improvement_opportunities = improvement_opps
            
            # Log the improvement opportunities
            for opp in improvement_opps:
                self.logger.info(f"Identified improvement opportunity: {opp}")
        
        # Store the learning experience
        await self._store_learning_experience(experience)
        
        # Update knowledge graph
        await self._update_knowledge_graph(experience)
        
        # Apply learnings if applicable
        await self._apply_learnings(experience)
    
    def _identify_improvements_from_error(self, error_message: str, task_name: str) -> List[str]:
        """Identify potential improvements based on error messages"""
        improvements = []
        
        error_lower = error_message.lower()
        
        if "timeout" in error_lower:
            improvements.append(f"Increase timeout threshold for task '{task_name}'")
        if "memory" in error_lower or "oom" in error_lower:
            improvements.append(f"Optimize memory usage for task '{task_name}'")
        if "connection" in error_lower or "network" in error_lower:
            improvements.append(f"Improve network error handling for task '{task_name}'")
        if "permission" in error_lower:
            improvements.append(f"Verify permissions for task '{task_name}'")
        if "not found" in error_lower:
            improvements.append(f"Validate input parameters for task '{task_name}'")
            
        return improvements
    
    async def process_community_insight(self, insight_source: str, topic: str, content: str):
        """Process community insights for learning"""
        if not self.is_active:
            return
            
        self.logger.info(f"Processing community insight from {insight_source} about {topic}")
        
        # Create learning experience from community insight
        experience = LearningExperience(
            id=f"community_{insight_source}_{topic}_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            experience_type="community_insight",
            content=content,
            source=insight_source,
            tags=["community", "insight", topic],
            relevance_score=0.9,  # Community insights are generally valuable
            applicability_score=0.7
        )
        
        # Store the learning experience
        await self._store_learning_experience(experience)
        
        # Update knowledge graph
        await self._update_knowledge_graph(experience)
        
        # Apply learnings if applicable
        await self._apply_learnings(experience)
    
    async def process_user_interaction(self, user_input: str, assistant_response: str, context: Dict[str, Any]):
        """Process user interactions for learning"""
        if not self.is_active:
            return
            
        self.logger.info(f"Processing user interaction: {user_input[:50]}...")
        
        # Create learning experience from user interaction
        content = f"User asked: '{user_input}'. Response: '{assistant_response}'. Context: {json.dumps(context)}"
        
        experience = LearningExperience(
            id=f"interaction_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            experience_type="user_interaction",
            content=content,
            source="user_interaction",
            tags=["user", "interaction", "conversation"],
            relevance_score=0.8,
            applicability_score=0.6
        )
        
        # Store the learning experience
        await self._store_learning_experience(experience)
        
        # Update knowledge graph
        await self._update_knowledge_graph(experience)
    
    async def _store_learning_experience(self, experience: LearningExperience):
        """Store a learning experience in the database"""
        # Store in database
        self.database.store_learning(
            learning_content=experience.content,
            source=experience.source,
            tags=experience.tags,
            relevance_score=experience.relevance_score
        )
        
        # Keep in memory for quick access (limit to last 100 experiences)
        self.learning_experiences.append(experience)
        if len(self.learning_experiences) > 100:
            self.learning_experiences = self.learning_experiences[-100:]
        
        self.logger.debug(f"Stored learning experience: {experience.id}")
    
    async def _update_knowledge_graph(self, experience: LearningExperience):
        """Update the knowledge graph with new information"""
        # Simplified knowledge graph update
        # In a real implementation, this would use more sophisticated graph structures
        
        # Extract key concepts from the experience
        content_lower = experience.content.lower()
        
        # Update knowledge graph based on tags
        for tag in experience.tags:
            if tag not in self.knowledge_graph:
                self.knowledge_graph[tag] = []
            
            # Add the experience to the tag's knowledge
            self.knowledge_graph[tag].append({
                "id": experience.id,
                "timestamp": experience.timestamp.isoformat(),
                "content_preview": experience.content[:100],
                "relevance_score": experience.relevance_score
            })
            
            # Keep only the most relevant experiences for each tag (top 10)
            self.knowledge_graph[tag] = sorted(
                self.knowledge_graph[tag],
                key=lambda x: x["relevance_score"],
                reverse=True
            )[:10]
    
    async def _apply_learnings(self, experience: LearningExperience):
        """Apply learnings to improve system performance"""
        if experience.experience_type == "task_result":
            # If task failed, consider adjusting its priority or rescheduling
            if experience.applicability_score < 0.6:  # Indicates likely failure
                # Could implement logic to adjust task parameters
                self.logger.info(f"Learning applied: Task may need parameter adjustment based on experience {experience.id}")
        
        elif experience.experience_type == "community_insight":
            # Apply community best practices
            content_lower = experience.content.lower()
            
            if "performance" in content_lower and "optimization" in content_lower:
                self.logger.info("Learning applied: Performance optimization strategy noted")
                
            if "security" in content_lower or "credential" in content_lower:
                self.logger.info("Learning applied: Security best practice noted")
                
            if "memory" in content_lower or "database" in content_lower:
                self.logger.info("Learning applied: Memory/database strategy noted")
    
    async def get_relevant_learnings(self, topic: str, limit: int = 5) -> List[LearningExperience]:
        """Get relevant learnings for a specific topic"""
        relevant_learnings = []
        
        # Search in learning experiences
        for exp in self.learning_experiences:
            if topic.lower() in exp.content.lower() or topic.lower() in exp.tags:
                relevant_learnings.append(exp)
        
        # Sort by timestamp (most recent first) and limit
        relevant_learnings.sort(key=lambda x: x.timestamp, reverse=True)
        return relevant_learnings[:limit]
    
    async def generate_improvement_report(self) -> Dict[str, Any]:
        """Generate a report on improvement opportunities"""
        self.logger.info("Generating improvement report")
        
        # Collect improvement opportunities from various sources
        improvement_ops = []
        
        # From task failures
        failed_tasks = self.assistant.intelligent_scheduler.get_failed_tasks()
        for task in failed_tasks:
            if task.error:
                error_msg = str(task.error)
                ops = self._identify_improvements_from_error(error_msg, task.name)
                for op in ops:
                    improvement_ops.append({
                        "type": "task_failure",
                        "description": op,
                        "related_task": task.name,
                        "timestamp": datetime.now().isoformat()
                    })
        
        # From knowledge graph patterns
        for tag, entries in self.knowledge_graph.items():
            if len(entries) > 5:  # If we have many entries for this tag
                improvement_ops.append({
                    "type": "pattern_recognition",
                    "description": f"High activity in '{tag}' area - consider optimization",
                    "related_topic": tag,
                    "timestamp": datetime.now().isoformat()
                })
        
        # From community insights
        community_learnings = await self.get_relevant_learnings("improvement", limit=10)
        for exp in community_learnings:
            if "improv" in exp.content.lower() or "better" in exp.content.lower():
                improvement_ops.append({
                    "type": "community_insight",
                    "description": exp.content[:200],
                    "source": exp.source,
                    "timestamp": exp.timestamp.isoformat()
                })
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_improvements_identified": len(improvement_ops),
            "improvements": improvement_ops,
            "knowledge_domains": list(self.knowledge_graph.keys()),
            "recent_learnings_count": len(self.learning_experiences)
        }
        
        self.logger.info(f"Improvement report generated with {len(improvement_ops)} opportunities")
        return report
    
    async def run_continuous_learning_cycle(self):
        """Run a continuous learning cycle"""
        self.logger.info("Starting continuous learning cycle")
        
        while self.is_active:
            try:
                # Perform periodic learning tasks
                await self._periodic_learning_tasks()
                
                # Wait before next cycle
                await asyncio.sleep(3600)  # 1 hour
            except Exception as e:
                self.logger.error(f"Error in continuous learning cycle: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _periodic_learning_tasks(self):
        """Perform periodic learning-related tasks"""
        # Generate and review improvement report
        report = await self.generate_improvement_report()
        
        if report["total_improvements_identified"] > 0:
            self.logger.info(f"Found {report['total_improvements_identified']} improvement opportunities")
            
            # Store the most important improvements as learnings
            for imp in report["improvements"][:3]:  # Top 3 improvements
                content = f"Improvement opportunity: {imp['description']}"
                source = imp.get("source", "system_analysis")
                
                experience = LearningExperience(
                    id=f"improvement_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    experience_type="system_improvement",
                    content=content,
                    source=source,
                    tags=["improvement", "system", "optimization"],
                    relevance_score=0.9,
                    applicability_score=0.8
                )
                
                await self._store_learning_experience(experience)
                await self._update_knowledge_graph(experience)
    
    def start_learning_cycle(self):
        """Start the continuous learning cycle in the background"""
        if self.is_active:
            asyncio.create_task(self.run_continuous_learning_cycle())
            self.logger.info("Continuous learning cycle started in background")
    
    def stop_learning(self):
        """Stop the learning system"""
        self.is_active = False
        self.logger.info("Learning system stopped")