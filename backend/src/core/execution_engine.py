"""
Valis AI - Execution Engine
Combines Manus AI execution capabilities with Valis AI intelligence
"""

import subprocess
import os
import json
import time
import uuid
import tempfile
import shutil
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import requests

class WorkspaceType(Enum):
    CLOUD_VM = "cloud_vm"
    CONTAINER = "container"
    LOCAL = "local"

class ExecutionEnvironment(Enum):
    PYTHON = "python"
    NODE = "node"
    REACT = "react"
    FLASK = "flask"
    DOCKER = "docker"
    SHELL = "shell"

@dataclass
class Workspace:
    id: str
    type: WorkspaceType
    environment: ExecutionEnvironment
    status: str
    created_at: float
    files: Dict[str, str]
    processes: List[str]
    ports: List[int]
    url: Optional[str] = None

class ExecutionEngine:
    """
    Execution engine that provides Manus AI-style capabilities:
    - Cloud workspace management
    - Code execution and deployment
    - Real-time process monitoring
    - File system operations
    - API integrations
    """
    
    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.base_workspace_dir = "/tmp/valis_workspaces"
        os.makedirs(self.base_workspace_dir, exist_ok=True)
    
    def create_workspace(self, environment: ExecutionEnvironment) -> str:
        """
        Create a new workspace for code execution
        """
        workspace_id = str(uuid.uuid4())
        workspace_dir = os.path.join(self.base_workspace_dir, workspace_id)
        os.makedirs(workspace_dir, exist_ok=True)
        
        workspace = Workspace(
            id=workspace_id,
            type=WorkspaceType.CONTAINER,
            environment=environment,
            status="active",
            created_at=time.time(),
            files={},
            processes=[],
            ports=[]
        )
        
        self.workspaces[workspace_id] = workspace
        
        # Initialize workspace based on environment
        self._initialize_workspace(workspace_id, environment)
        
        return workspace_id
    
    def _initialize_workspace(self, workspace_id: str, environment: ExecutionEnvironment):
        """
        Initialize workspace with appropriate tools and dependencies
        """
        workspace_dir = os.path.join(self.base_workspace_dir, workspace_id)
        
        if environment == ExecutionEnvironment.REACT:
            self._setup_react_workspace(workspace_dir)
        elif environment == ExecutionEnvironment.FLASK:
            self._setup_flask_workspace(workspace_dir)
        elif environment == ExecutionEnvironment.PYTHON:
            self._setup_python_workspace(workspace_dir)
        elif environment == ExecutionEnvironment.NODE:
            self._setup_node_workspace(workspace_dir)
    
    def _setup_react_workspace(self, workspace_dir: str):
        """
        Set up a React development workspace
        """
        # Create package.json
        package_json = {
            "name": "valis-ai-project",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.0.3",
                "vite": "^4.4.5"
            }
        }
        
        with open(os.path.join(workspace_dir, "package.json"), "w") as f:
            json.dump(package_json, f, indent=2)
        
        # Create basic React structure
        src_dir = os.path.join(workspace_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        
        # Create index.html
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Valis AI Project</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
</body>
</html>"""
        
        with open(os.path.join(workspace_dir, "index.html"), "w") as f:
            f.write(index_html)
    
    def _setup_flask_workspace(self, workspace_dir: str):
        """
        Set up a Flask development workspace
        """
        # Create requirements.txt
        requirements = """Flask==2.3.3
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.0.5
python-dotenv==1.0.0"""
        
        with open(os.path.join(workspace_dir, "requirements.txt"), "w") as f:
            f.write(requirements)
        
        # Create basic Flask structure
        src_dir = os.path.join(workspace_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
    
    def _setup_python_workspace(self, workspace_dir: str):
        """
        Set up a Python development workspace
        """
        # Create requirements.txt
        requirements = """requests==2.31.0
pandas==2.0.3
numpy==1.24.3
matplotlib==3.7.2"""
        
        with open(os.path.join(workspace_dir, "requirements.txt"), "w") as f:
            f.write(requirements)
    
    def _setup_node_workspace(self, workspace_dir: str):
        """
        Set up a Node.js development workspace
        """
        # Create package.json
        package_json = {
            "name": "valis-ai-node-project",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "start": "node index.js",
                "dev": "nodemon index.js"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5"
            },
            "devDependencies": {
                "nodemon": "^3.0.1"
            }
        }
        
        with open(os.path.join(workspace_dir, "package.json"), "w") as f:
            json.dump(package_json, f, indent=2)
    
    def write_file(self, workspace_id: str, file_path: str, content: str) -> bool:
        """
        Write a file to the workspace
        """
        if workspace_id not in self.workspaces:
            return False
        
        workspace_dir = os.path.join(self.base_workspace_dir, workspace_id)
        full_path = os.path.join(workspace_dir, file_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, "w") as f:
                f.write(content)
            
            # Update workspace files
            self.workspaces[workspace_id].files[file_path] = content
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False
    
    def read_file(self, workspace_id: str, file_path: str) -> Optional[str]:
        """
        Read a file from the workspace
        """
        if workspace_id not in self.workspaces:
            return None
        
        workspace_dir = os.path.join(self.base_workspace_dir, workspace_id)
        full_path = os.path.join(workspace_dir, file_path)
        
        try:
            with open(full_path, "r") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    def execute_command(self, workspace_id: str, command: str) -> Dict[str, Any]:
        """
        Execute a command in the workspace
        """
        if workspace_id not in self.workspaces:
            return {"error": "Workspace not found"}
        
        workspace_dir = os.path.join(self.base_workspace_dir, workspace_id)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": str(e)}
    
    def install_dependencies(self, workspace_id: str) -> Dict[str, Any]:
        """
        Install dependencies based on workspace environment
        """
        if workspace_id not in self.workspaces:
            return {"error": "Workspace not found"}
        
        workspace = self.workspaces[workspace_id]
        
        if workspace.environment in [ExecutionEnvironment.REACT, ExecutionEnvironment.NODE]:
            return self.execute_command(workspace_id, "npm install")
        elif workspace.environment in [ExecutionEnvironment.FLASK, ExecutionEnvironment.PYTHON]:
            return self.execute_command(workspace_id, "pip install -r requirements.txt")
        else:
            return {"success": True, "message": "No dependencies to install"}
    
    def start_development_server(self, workspace_id: str) -> Dict[str, Any]:
        """
        Start development server for the workspace
        """
        if workspace_id not in self.workspaces:
            return {"error": "Workspace not found"}
        
        workspace = self.workspaces[workspace_id]
        
        if workspace.environment == ExecutionEnvironment.REACT:
            # Start React dev server
            command = "npm run dev -- --host 0.0.0.0 --port 3000"
        elif workspace.environment == ExecutionEnvironment.FLASK:
            # Start Flask dev server
            command = "python src/main.py"
        elif workspace.environment == ExecutionEnvironment.NODE:
            # Start Node.js server
            command = "npm start"
        else:
            return {"error": "Development server not supported for this environment"}
        
        try:
            # Start process in background
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=os.path.join(self.base_workspace_dir, workspace_id),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            workspace.processes.append(str(process.pid))
            
            # Determine port and URL
            if workspace.environment == ExecutionEnvironment.REACT:
                port = 3000
                workspace.url = f"http://localhost:{port}"
            elif workspace.environment == ExecutionEnvironment.FLASK:
                port = 5000
                workspace.url = f"http://localhost:{port}"
            elif workspace.environment == ExecutionEnvironment.NODE:
                port = 3000
                workspace.url = f"http://localhost:{port}"
            
            workspace.ports.append(port)
            
            return {
                "success": True,
                "process_id": process.pid,
                "url": workspace.url,
                "port": port
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def build_project(self, workspace_id: str) -> Dict[str, Any]:
        """
        Build the project for production
        """
        if workspace_id not in self.workspaces:
            return {"error": "Workspace not found"}
        
        workspace = self.workspaces[workspace_id]
        
        if workspace.environment == ExecutionEnvironment.REACT:
            return self.execute_command(workspace_id, "npm run build")
        elif workspace.environment == ExecutionEnvironment.FLASK:
            # Flask doesn't need building, just ensure dependencies are installed
            return {"success": True, "message": "Flask project ready for deployment"}
        else:
            return {"success": True, "message": "No build step required"}
    
    def deploy_to_vercel(self, workspace_id: str) -> Dict[str, Any]:
        """
        Deploy project to Vercel (simulated)
        """
        if workspace_id not in self.workspaces:
            return {"error": "Workspace not found"}
        
        # Simulate deployment
        deployment_url = f"https://valis-{workspace_id[:8]}.vercel.app"
        
        return {
            "success": True,
            "deployment_url": deployment_url,
            "status": "deployed"
        }
    
    def get_workspace_status(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get current status of workspace
        """
        if workspace_id not in self.workspaces:
            return {"error": "Workspace not found"}
        
        workspace = self.workspaces[workspace_id]
        
        return {
            "id": workspace.id,
            "type": workspace.type.value,
            "environment": workspace.environment.value,
            "status": workspace.status,
            "created_at": workspace.created_at,
            "files": list(workspace.files.keys()),
            "processes": workspace.processes,
            "ports": workspace.ports,
            "url": workspace.url
        }
    
    def list_files(self, workspace_id: str) -> List[str]:
        """
        List all files in workspace
        """
        if workspace_id not in self.workspaces:
            return []
        
        workspace_dir = os.path.join(self.base_workspace_dir, workspace_id)
        files = []
        
        for root, dirs, filenames in os.walk(workspace_dir):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), workspace_dir)
                files.append(rel_path)
        
        return files
    
    def cleanup_workspace(self, workspace_id: str) -> bool:
        """
        Clean up workspace and stop all processes
        """
        if workspace_id not in self.workspaces:
            return False
        
        workspace = self.workspaces[workspace_id]
        
        # Stop all processes
        for pid in workspace.processes:
            try:
                subprocess.run(f"kill {pid}", shell=True)
            except:
                pass
        
        # Remove workspace directory
        workspace_dir = os.path.join(self.base_workspace_dir, workspace_id)
        try:
            shutil.rmtree(workspace_dir)
        except:
            pass
        
        # Remove from active workspaces
        del self.workspaces[workspace_id]
        
        return True
    
    def get_all_workspaces(self) -> List[Dict[str, Any]]:
        """
        Get all active workspaces
        """
        return [self.get_workspace_status(ws_id) for ws_id in self.workspaces.keys()]

