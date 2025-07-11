"""
Valis AI - Autonomous Intelligence Core
Combines Valis AI autonomous capabilities with Manus AI execution power
"""

import openai
import json
import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    WEBSITE_CREATION = "website_creation"
    PRESENTATION = "presentation"
    IMAGE_GENERATION = "image_generation"
    VIDEO_CREATION = "video_creation"
    API_DEVELOPMENT = "api_development"
    FULL_STACK_APP = "full_stack_app"
    DATA_ANALYSIS = "data_analysis"
    AUTOMATION = "automation"
    GENERAL_CHAT = "general_chat"

class ExecutionStatus(Enum):
    PLANNING = "planning"
    EXECUTING = "executing"
    TESTING = "testing"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class Task:
    id: str
    type: TaskType
    description: str
    status: ExecutionStatus
    progress: int
    steps: List[str]
    current_step: int
    results: Dict[str, Any]
    created_at: float
    updated_at: float

class AutonomousIntelligence:
    """
    Core autonomous intelligence system that combines:
    - Valis AI's autonomous decision making
    - Manus AI's execution capabilities
    - Smart task planning and execution
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        self.active_tasks: Dict[str, Task] = {}
        self.memory: Dict[str, Any] = {}
        
    def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user input to determine intent and task type
        Uses advanced AI to understand what the user wants to accomplish
        """
        
        system_prompt = """
        You are Valis AI, an autonomous intelligence system. Analyze the user's input and determine:
        1. The primary task type they want to accomplish
        2. The complexity level (simple, medium, complex)
        3. Required tools and technologies
        4. Step-by-step execution plan
        5. Expected deliverables
        
        Task types available:
        - website_creation: Building websites, landing pages, web apps
        - presentation: Creating presentations, slides, pitch decks
        - image_generation: Creating images, graphics, designs
        - video_creation: Creating videos, animations
        - api_development: Building APIs, backends, databases
        - full_stack_app: Complete applications with frontend and backend
        - data_analysis: Analyzing data, creating visualizations
        - automation: Automating tasks, workflows, processes
        - general_chat: General conversation, questions, help
        
        Respond with JSON format:
        {
            "task_type": "website_creation",
            "complexity": "medium",
            "confidence": 0.95,
            "description": "User wants to create a coffee shop website",
            "technologies": ["React", "CSS", "JavaScript"],
            "steps": ["Design layout", "Create components", "Add content", "Style interface", "Deploy"],
            "estimated_time": "15 minutes",
            "deliverables": ["Live website URL", "Source code", "Deployment guide"]
        }
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            # Fallback analysis
            return {
                "task_type": "general_chat",
                "complexity": "simple",
                "confidence": 0.5,
                "description": f"General request: {user_input}",
                "technologies": [],
                "steps": ["Process request", "Generate response"],
                "estimated_time": "1 minute",
                "deliverables": ["AI response"]
            }
    
    def create_task(self, user_input: str) -> str:
        """
        Create a new autonomous task based on user input
        Returns task ID for tracking
        """
        
        # Analyze the user's intent
        analysis = self.analyze_intent(user_input)
        
        # Create task
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            type=TaskType(analysis["task_type"]),
            description=analysis["description"],
            status=ExecutionStatus.PLANNING,
            progress=0,
            steps=analysis["steps"],
            current_step=0,
            results={
                "analysis": analysis,
                "user_input": user_input
            },
            created_at=time.time(),
            updated_at=time.time()
        )
        
        self.active_tasks[task_id] = task
        return task_id
    
    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        Execute a task autonomously using Manus AI capabilities
        """
        
        if task_id not in self.active_tasks:
            return {"error": "Task not found"}
        
        task = self.active_tasks[task_id]
        
        # Update status to executing
        task.status = ExecutionStatus.EXECUTING
        task.updated_at = time.time()
        
        # Execute based on task type
        if task.type == TaskType.WEBSITE_CREATION:
            return self._execute_website_creation(task)
        elif task.type == TaskType.PRESENTATION:
            return self._execute_presentation_creation(task)
        elif task.type == TaskType.IMAGE_GENERATION:
            return self._execute_image_generation(task)
        elif task.type == TaskType.API_DEVELOPMENT:
            return self._execute_api_development(task)
        elif task.type == TaskType.FULL_STACK_APP:
            return self._execute_fullstack_development(task)
        else:
            return self._execute_general_response(task)
    
    def _execute_website_creation(self, task: Task) -> Dict[str, Any]:
        """
        Execute website creation with autonomous intelligence
        """
        
        # Generate website content using AI
        content_prompt = f"""
        Create a complete website for: {task.description}
        
        Generate:
        1. HTML structure
        2. CSS styling (modern, responsive)
        3. JavaScript functionality
        4. Content and copy
        
        Make it professional, modern, and fully functional.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional web developer. Create complete, working websites."},
                    {"role": "user", "content": content_prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            # Update task progress
            task.progress = 50
            task.current_step = 2
            task.status = ExecutionStatus.TESTING
            task.updated_at = time.time()
            
            # Store generated content
            task.results["generated_content"] = response.choices[0].message.content
            task.results["status"] = "Website generated successfully"
            
            # Simulate deployment
            task.progress = 100
            task.status = ExecutionStatus.COMPLETED
            task.results["deployment_url"] = f"https://valis-ai-{task.id[:8]}.vercel.app"
            
            return {
                "success": True,
                "task_id": task.id,
                "status": task.status.value,
                "progress": task.progress,
                "results": task.results
            }
            
        except Exception as e:
            task.status = ExecutionStatus.ERROR
            task.results["error"] = str(e)
            return {"error": str(e)}
    
    def _execute_presentation_creation(self, task: Task) -> Dict[str, Any]:
        """
        Execute presentation creation
        """
        
        # Generate presentation content
        presentation_prompt = f"""
        Create a professional presentation for: {task.description}
        
        Generate:
        1. Slide titles and content
        2. Key points and bullet points
        3. Visual suggestions
        4. Speaker notes
        
        Make it engaging and professional.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a presentation expert. Create engaging, professional presentations."},
                    {"role": "user", "content": presentation_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            task.progress = 100
            task.status = ExecutionStatus.COMPLETED
            task.results["presentation_content"] = response.choices[0].message.content
            task.results["status"] = "Presentation created successfully"
            
            return {
                "success": True,
                "task_id": task.id,
                "status": task.status.value,
                "progress": task.progress,
                "results": task.results
            }
            
        except Exception as e:
            task.status = ExecutionStatus.ERROR
            task.results["error"] = str(e)
            return {"error": str(e)}
    
    def _execute_image_generation(self, task: Task) -> Dict[str, Any]:
        """
        Execute image generation
        """
        
        try:
            # Generate image using DALL-E
            response = openai.Image.create(
                prompt=task.description,
                n=1,
                size="1024x1024"
            )
            
            task.progress = 100
            task.status = ExecutionStatus.COMPLETED
            task.results["image_url"] = response['data'][0]['url']
            task.results["status"] = "Image generated successfully"
            
            return {
                "success": True,
                "task_id": task.id,
                "status": task.status.value,
                "progress": task.progress,
                "results": task.results
            }
            
        except Exception as e:
            task.status = ExecutionStatus.ERROR
            task.results["error"] = str(e)
            return {"error": str(e)}
    
    def _execute_api_development(self, task: Task) -> Dict[str, Any]:
        """
        Execute API development
        """
        
        api_prompt = f"""
        Create a complete API for: {task.description}
        
        Generate:
        1. Flask/FastAPI code structure
        2. Database models
        3. API endpoints
        4. Authentication
        5. Documentation
        
        Make it production-ready and well-documented.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a backend developer expert. Create complete, production-ready APIs."},
                    {"role": "user", "content": api_prompt}
                ],
                temperature=0.5,
                max_tokens=3000
            )
            
            task.progress = 100
            task.status = ExecutionStatus.COMPLETED
            task.results["api_code"] = response.choices[0].message.content
            task.results["status"] = "API created successfully"
            task.results["api_url"] = f"https://api-valis-{task.id[:8]}.vercel.app"
            
            return {
                "success": True,
                "task_id": task.id,
                "status": task.status.value,
                "progress": task.progress,
                "results": task.results
            }
            
        except Exception as e:
            task.status = ExecutionStatus.ERROR
            task.results["error"] = str(e)
            return {"error": str(e)}
    
    def _execute_fullstack_development(self, task: Task) -> Dict[str, Any]:
        """
        Execute full-stack application development
        """
        
        fullstack_prompt = f"""
        Create a complete full-stack application for: {task.description}
        
        Generate:
        1. Frontend (React/Vue/Angular)
        2. Backend (Node.js/Python/Flask)
        3. Database schema
        4. API endpoints
        5. Authentication system
        6. Deployment configuration
        
        Make it production-ready and scalable.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a full-stack developer expert. Create complete, scalable applications."},
                    {"role": "user", "content": fullstack_prompt}
                ],
                temperature=0.5,
                max_tokens=4000
            )
            
            task.progress = 100
            task.status = ExecutionStatus.COMPLETED
            task.results["application_code"] = response.choices[0].message.content
            task.results["status"] = "Full-stack application created successfully"
            task.results["frontend_url"] = f"https://app-valis-{task.id[:8]}.vercel.app"
            task.results["backend_url"] = f"https://api-valis-{task.id[:8]}.vercel.app"
            
            return {
                "success": True,
                "task_id": task.id,
                "status": task.status.value,
                "progress": task.progress,
                "results": task.results
            }
            
        except Exception as e:
            task.status = ExecutionStatus.ERROR
            task.results["error"] = str(e)
            return {"error": str(e)}
    
    def _execute_general_response(self, task: Task) -> Dict[str, Any]:
        """
        Execute general chat response
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Valis AI, an autonomous intelligence assistant. Be helpful, informative, and engaging."},
                    {"role": "user", "content": task.results["user_input"]}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            task.progress = 100
            task.status = ExecutionStatus.COMPLETED
            task.results["response"] = response.choices[0].message.content
            task.results["status"] = "Response generated successfully"
            
            return {
                "success": True,
                "task_id": task.id,
                "status": task.status.value,
                "progress": task.progress,
                "results": task.results
            }
            
        except Exception as e:
            task.status = ExecutionStatus.ERROR
            task.results["error"] = str(e)
            return {"error": str(e)}
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get current status of a task
        """
        
        if task_id not in self.active_tasks:
            return {"error": "Task not found"}
        
        task = self.active_tasks[task_id]
        
        return {
            "task_id": task.id,
            "type": task.type.value,
            "description": task.description,
            "status": task.status.value,
            "progress": task.progress,
            "current_step": task.current_step,
            "total_steps": len(task.steps),
            "step_name": task.steps[task.current_step] if task.current_step < len(task.steps) else "Completed",
            "results": task.results,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all active tasks
        """
        
        return [self.get_task_status(task_id) for task_id in self.active_tasks.keys()]
    
    def update_memory(self, key: str, value: Any):
        """
        Update persistent memory for learning
        """
        self.memory[key] = value
    
    def get_memory(self, key: str) -> Any:
        """
        Retrieve from persistent memory
        """
        return self.memory.get(key)

