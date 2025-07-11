"""
Valis AI - Autonomous Routes
Main API endpoints for autonomous intelligence and execution
"""

from flask import Blueprint, request, jsonify
import os
import time
import json
from core.autonomous_intelligence import AutonomousIntelligence
from core.execution_engine import ExecutionEngine, ExecutionEnvironment

# Initialize blueprint
autonomous_bp = Blueprint('autonomous', __name__)

# Initialize core systems
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
ai_intelligence = AutonomousIntelligence(OPENAI_API_KEY)
execution_engine = ExecutionEngine()

@autonomous_bp.route('/chat', methods=['POST'])
def autonomous_chat():
    """
    Main chat endpoint for autonomous intelligence
    Handles user input and creates autonomous tasks
    """
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create autonomous task
        task_id = ai_intelligence.create_task(user_input)
        
        # Get initial task status
        task_status = ai_intelligence.get_task_status(task_id)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': f"I'll help you with that! I've detected this as a {task_status['type'].replace('_', ' ')} request. Let me work on this autonomously...",
            'task_status': task_status
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/execute/<task_id>', methods=['POST'])
def execute_autonomous_task(task_id):
    """
    Execute an autonomous task
    """
    try:
        # Execute the task
        result = ai_intelligence.execute_task(task_id)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Get current status of a task
    """
    try:
        status = ai_intelligence.get_task_status(task_id)
        
        if 'error' in status:
            return jsonify(status), 404
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/tasks', methods=['GET'])
def get_all_tasks():
    """
    Get all active tasks
    """
    try:
        tasks = ai_intelligence.get_all_tasks()
        return jsonify({'tasks': tasks})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspace/create', methods=['POST'])
def create_workspace():
    """
    Create a new execution workspace
    """
    try:
        data = request.get_json()
        environment = data.get('environment', 'python')
        
        # Map string to enum
        env_mapping = {
            'python': ExecutionEnvironment.PYTHON,
            'node': ExecutionEnvironment.NODE,
            'react': ExecutionEnvironment.REACT,
            'flask': ExecutionEnvironment.FLASK,
            'docker': ExecutionEnvironment.DOCKER,
            'shell': ExecutionEnvironment.SHELL
        }
        
        env = env_mapping.get(environment, ExecutionEnvironment.PYTHON)
        workspace_id = execution_engine.create_workspace(env)
        
        return jsonify({
            'success': True,
            'workspace_id': workspace_id,
            'environment': environment
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspace/<workspace_id>/status', methods=['GET'])
def get_workspace_status(workspace_id):
    """
    Get workspace status
    """
    try:
        status = execution_engine.get_workspace_status(workspace_id)
        
        if 'error' in status:
            return jsonify(status), 404
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspace/<workspace_id>/files', methods=['POST'])
def write_workspace_file(workspace_id):
    """
    Write a file to workspace
    """
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        content = data.get('content', '')
        
        if not file_path:
            return jsonify({'error': 'file_path is required'}), 400
        
        success = execution_engine.write_file(workspace_id, file_path, content)
        
        if success:
            return jsonify({'success': True, 'message': 'File written successfully'})
        else:
            return jsonify({'error': 'Failed to write file'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspace/<workspace_id>/files/<path:file_path>', methods=['GET'])
def read_workspace_file(workspace_id, file_path):
    """
    Read a file from workspace
    """
    try:
        content = execution_engine.read_file(workspace_id, file_path)
        
        if content is None:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify({'content': content})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspace/<workspace_id>/execute', methods=['POST'])
def execute_workspace_command(workspace_id):
    """
    Execute a command in workspace
    """
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'command is required'}), 400
        
        result = execution_engine.execute_command(workspace_id, command)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspace/<workspace_id>/install', methods=['POST'])
def install_workspace_dependencies(workspace_id):
    """
    Install dependencies in workspace
    """
    try:
        result = execution_engine.install_dependencies(workspace_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspace/<workspace_id>/start', methods=['POST'])
def start_workspace_server(workspace_id):
    """
    Start development server in workspace
    """
    try:
        result = execution_engine.start_development_server(workspace_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspace/<workspace_id>/build', methods=['POST'])
def build_workspace_project(workspace_id):
    """
    Build project in workspace
    """
    try:
        result = execution_engine.build_project(workspace_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspace/<workspace_id>/deploy', methods=['POST'])
def deploy_workspace_project(workspace_id):
    """
    Deploy project from workspace
    """
    try:
        result = execution_engine.deploy_to_vercel(workspace_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspace/<workspace_id>/files/list', methods=['GET'])
def list_workspace_files(workspace_id):
    """
    List all files in workspace
    """
    try:
        files = execution_engine.list_files(workspace_id)
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspaces', methods=['GET'])
def get_all_workspaces():
    """
    Get all active workspaces
    """
    try:
        workspaces = execution_engine.get_all_workspaces()
        return jsonify({'workspaces': workspaces})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/workspace/<workspace_id>', methods=['DELETE'])
def cleanup_workspace(workspace_id):
    """
    Clean up and delete workspace
    """
    try:
        success = execution_engine.cleanup_workspace(workspace_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Workspace cleaned up successfully'})
        else:
            return jsonify({'error': 'Failed to cleanup workspace'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/analyze', methods=['POST'])
def analyze_user_intent():
    """
    Analyze user intent without creating a task
    """
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({'error': 'Message is required'}), 400
        
        analysis = ai_intelligence.analyze_intent(user_input)
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/memory', methods=['POST'])
def update_memory():
    """
    Update AI memory for learning
    """
    try:
        data = request.get_json()
        key = data.get('key', '')
        value = data.get('value', '')
        
        if not key:
            return jsonify({'error': 'key is required'}), 400
        
        ai_intelligence.update_memory(key, value)
        return jsonify({'success': True, 'message': 'Memory updated'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/memory/<key>', methods=['GET'])
def get_memory(key):
    """
    Get value from AI memory
    """
    try:
        value = ai_intelligence.get_memory(key)
        return jsonify({'key': key, 'value': value})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomous_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Valis AI Autonomous Intelligence',
        'version': '1.0.0',
        'timestamp': time.time()
    })

# Error handlers
@autonomous_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@autonomous_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

