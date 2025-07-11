"""
Valis AI - CodeAct Engine
Implementation of CodeAct architecture for autonomous code execution
Based on research of Manus AI's architecture with Valis enhancements
"""

import ast
import sys
import io
import traceback
import subprocess
import os
import uuid
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from contextlib import redirect_stdout, redirect_stderr
import openai

class CodeActEngine:
    """
    CodeAct Engine for autonomous code execution
    Allows AI agents to write and execute Python code instead of JSON function calls
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        self.sessions = {}
        self.execution_history = {}
        
    def create_session(self, session_id: str = None) -> str:
        """Create a new CodeAct execution session"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            'variables': {},
            'imports': set(),
            'execution_count': 0,
            'created_at': time.time(),
            'last_activity': time.time()
        }
        
        self.execution_history[session_id] = []
        return session_id
    
    def execute_code(self, session_id: str, code: str, context: str = "") -> Dict[str, Any]:
        """
        Execute Python code in a session with full error handling and state management
        """
        if session_id not in self.sessions:
            session_id = self.create_session(session_id)
        
        session = self.sessions[session_id]
        session['last_activity'] = time.time()
        session['execution_count'] += 1
        
        # Prepare execution environment
        exec_globals = {
            '__builtins__': __builtins__,
            'print': print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sorted': sorted,
            'sum': sum,
            'max': max,
            'min': min,
            'abs': abs,
            'round': round,
            'open': open,
            'json': json,
            'os': os,
            'sys': sys,
            'time': time,
            'uuid': uuid,
            'subprocess': subprocess
        }
        
        # Add session variables
        exec_globals.update(session['variables'])
        
        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        result = {
            'session_id': session_id,
            'execution_count': session['execution_count'],
            'code': code,
            'context': context,
            'success': False,
            'output': '',
            'error': '',
            'variables_changed': [],
            'new_imports': [],
            'execution_time': 0,
            'timestamp': time.time()
        }
        
        start_time = time.time()
        
        try:
            # Parse code to check for imports
            tree = ast.parse(code)
            new_imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_name = alias.name
                        if import_name not in session['imports']:
                            session['imports'].add(import_name)
                            new_imports.append(import_name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        import_name = f"{module}.{alias.name}" if module else alias.name
                        if import_name not in session['imports']:
                            session['imports'].add(import_name)
                            new_imports.append(import_name)
            
            result['new_imports'] = new_imports
            
            # Execute code with output capture
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, exec_globals)
            
            # Capture variables that changed
            variables_before = set(session['variables'].keys())
            variables_after = set(exec_globals.keys()) - set(__builtins__.keys()) - {
                'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
                'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'sum', 'max',
                'min', 'abs', 'round', 'open', 'json', 'os', 'sys', 'time', 'uuid', 'subprocess'
            }
            
            # Update session variables
            for var_name in variables_after:
                if var_name not in variables_before or session['variables'].get(var_name) != exec_globals[var_name]:
                    session['variables'][var_name] = exec_globals[var_name]
                    result['variables_changed'].append(var_name)
            
            result['success'] = True
            result['output'] = stdout_capture.getvalue()
            
        except Exception as e:
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()
            stderr_output = stderr_capture.getvalue()
            if stderr_output:
                result['error'] += f"\nStderr: {stderr_output}"
        
        result['execution_time'] = time.time() - start_time
        
        # Store in execution history
        self.execution_history[session_id].append(result)
        
        return result
    
    def generate_code_with_ai(self, task_description: str, context: str = "", session_id: str = None) -> str:
        """
        Use AI to generate Python code for a given task
        """
        if session_id and session_id in self.sessions:
            session_context = f"Session variables: {list(self.sessions[session_id]['variables'].keys())}\n"
            session_context += f"Imported modules: {list(self.sessions[session_id]['imports'])}\n"
        else:
            session_context = ""
        
        prompt = f"""You are a CodeAct AI agent. Generate Python code to accomplish the following task:

Task: {task_description}

Context: {context}
{session_context}

Requirements:
1. Write clean, executable Python code
2. Include error handling where appropriate
3. Use print() statements to show progress and results
4. Import any necessary modules
5. Make the code self-contained and robust

Generate only the Python code, no explanations:"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a CodeAct AI agent that generates Python code for autonomous execution. Always respond with only executable Python code."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            code = response.choices[0].message.content.strip()
            
            # Clean up code (remove markdown formatting if present)
            if code.startswith('```python'):
                code = code[9:]
            if code.startswith('```'):
                code = code[3:]
            if code.endswith('```'):
                code = code[:-3]
            
            return code.strip()
            
        except Exception as e:
            return f"# Error generating code: {str(e)}\nprint('Failed to generate code for task: {task_description}')"
    
    def execute_task_autonomously(self, task_description: str, session_id: str = None, max_iterations: int = 3) -> Dict[str, Any]:
        """
        Autonomously execute a task by generating and running code
        """
        if not session_id:
            session_id = self.create_session()
        
        results = []
        
        for iteration in range(max_iterations):
            # Generate code for the task
            code = self.generate_code_with_ai(
                task_description, 
                context=f"Iteration {iteration + 1}/{max_iterations}",
                session_id=session_id
            )
            
            # Execute the generated code
            execution_result = self.execute_code(session_id, code, context=f"Autonomous execution - {task_description}")
            results.append(execution_result)
            
            # If successful, break
            if execution_result['success'] and not execution_result['error']:
                break
            
            # If failed, try to fix the error
            if execution_result['error'] and iteration < max_iterations - 1:
                task_description += f"\n\nPrevious attempt failed with error: {execution_result['error']}\nPlease fix the error and try again."
        
        return {
            'session_id': session_id,
            'task_description': task_description,
            'iterations': len(results),
            'results': results,
            'final_success': results[-1]['success'] if results else False,
            'final_output': results[-1]['output'] if results else '',
            'final_error': results[-1]['error'] if results else ''
        }
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a session"""
        if session_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[session_id]
        history = self.execution_history.get(session_id, [])
        
        return {
            'session_id': session_id,
            'created_at': session['created_at'],
            'last_activity': session['last_activity'],
            'execution_count': session['execution_count'],
            'variables': list(session['variables'].keys()),
            'imports': list(session['imports']),
            'execution_history_count': len(history),
            'recent_executions': history[-5:] if history else []
        }
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        return [
            {
                'session_id': session_id,
                'created_at': session['created_at'],
                'last_activity': session['last_activity'],
                'execution_count': session['execution_count'],
                'variables_count': len(session['variables']),
                'imports_count': len(session['imports'])
            }
            for session_id, session in self.sessions.items()
        ]
    
    def cleanup_session(self, session_id: str) -> bool:
        """Clean up a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.execution_history:
            del self.execution_history[session_id]
        return True
    
    def debug_code(self, code: str, error_message: str, session_id: str = None) -> str:
        """
        Use AI to debug and fix code based on error message
        """
        prompt = f"""Debug and fix the following Python code that produced an error:

Code:
{code}

Error:
{error_message}

Please provide the corrected Python code that fixes the error. Return only the corrected code:"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a debugging expert. Fix Python code errors and return only the corrected code."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            fixed_code = response.choices[0].message.content.strip()
            
            # Clean up code
            if fixed_code.startswith('```python'):
                fixed_code = fixed_code[9:]
            if fixed_code.startswith('```'):
                fixed_code = fixed_code[3:]
            if fixed_code.endswith('```'):
                fixed_code = fixed_code[:-3]
            
            return fixed_code.strip()
            
        except Exception as e:
            return f"# Error debugging code: {str(e)}\n{code}"
    
    def install_package(self, package_name: str) -> Dict[str, Any]:
        """
        Install a Python package using pip
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'package': package_name,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'package': package_name,
                'error': 'Installation timeout (60s)',
                'return_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'package': package_name,
                'error': str(e),
                'return_code': -1
            }

# Global CodeAct engine instance
codeact_engine = None

def get_codeact_engine(openai_api_key: str) -> CodeActEngine:
    """Get or create the global CodeAct engine instance"""
    global codeact_engine
    if codeact_engine is None:
        codeact_engine = CodeActEngine(openai_api_key)
    return codeact_engine

