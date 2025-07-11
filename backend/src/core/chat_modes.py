"""
Valis AI - Chat Modes System
Implementation of Adaptive/Agent/Chat modes like Manus AI with Valis enhancements
"""

import openai
import time
import uuid
import json
from enum import Enum
from typing import Dict, List, Any, Optional
from .codeact_engine import get_codeact_engine
from .autonomous_intelligence import AutonomousIntelligence

class ChatMode(Enum):
    ADAPTIVE = "adaptive"  # AI automatically selects best approach
    AGENT = "agent"        # Full autonomous execution with workspace
    CHAT = "chat"          # Conversational assistance and guidance
    CUSTOM = "custom"      # User-defined AI behavior patterns

class ChatModeManager:
    """
    Manages different chat modes and their behaviors
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        self.codeact_engine = get_codeact_engine(openai_api_key)
        self.autonomous_ai = AutonomousIntelligence(openai_api_key)
        self.active_sessions = {}
        
    def create_chat_session(self, mode: ChatMode = ChatMode.ADAPTIVE, user_id: str = None) -> str:
        """Create a new chat session with specified mode"""
        session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            'session_id': session_id,
            'user_id': user_id,
            'mode': mode,
            'created_at': time.time(),
            'last_activity': time.time(),
            'message_count': 0,
            'context': [],
            'workspace_id': None,
            'task_history': [],
            'preferences': {
                'auto_execute': True,
                'show_code': True,
                'verbose_output': False,
                'safety_checks': True
            }
        }
        
        return session_id
    
    def process_message(self, session_id: str, message: str, mode: ChatMode = None) -> Dict[str, Any]:
        """
        Process a user message based on the current chat mode
        """
        if session_id not in self.active_sessions:
            session_id = self.create_chat_session(mode or ChatMode.ADAPTIVE)
        
        session = self.active_sessions[session_id]
        session['last_activity'] = time.time()
        session['message_count'] += 1
        
        # Override mode if specified
        if mode:
            session['mode'] = mode
        
        current_mode = session['mode']
        
        # Add message to context
        session['context'].append({
            'role': 'user',
            'content': message,
            'timestamp': time.time(),
            'mode': current_mode.value
        })
        
        # Process based on mode
        if current_mode == ChatMode.ADAPTIVE:
            return self._process_adaptive_mode(session, message)
        elif current_mode == ChatMode.AGENT:
            return self._process_agent_mode(session, message)
        elif current_mode == ChatMode.CHAT:
            return self._process_chat_mode(session, message)
        elif current_mode == ChatMode.CUSTOM:
            return self._process_custom_mode(session, message)
        else:
            return self._process_chat_mode(session, message)  # Default fallback
    
    def _process_adaptive_mode(self, session: Dict, message: str) -> Dict[str, Any]:
        """
        Adaptive mode: AI automatically selects the best approach
        """
        # Analyze the message to determine the best mode
        analysis = self._analyze_message_intent(message, session['context'])
        
        recommended_mode = analysis['recommended_mode']
        confidence = analysis['confidence']
        reasoning = analysis['reasoning']
        
        # If confidence is high, switch to recommended mode
        if confidence > 0.7:
            session['mode'] = ChatMode(recommended_mode)
            
            # Process with the recommended mode
            if recommended_mode == 'agent':
                result = self._process_agent_mode(session, message)
            elif recommended_mode == 'chat':
                result = self._process_chat_mode(session, message)
            else:
                result = self._process_chat_mode(session, message)
            
            # Add adaptive mode information
            result['adaptive_analysis'] = {
                'detected_intent': analysis['intent'],
                'recommended_mode': recommended_mode,
                'confidence': confidence,
                'reasoning': reasoning,
                'mode_switched': True
            }
            
            return result
        else:
            # Low confidence, stay in chat mode for clarification
            result = self._process_chat_mode(session, message)
            result['adaptive_analysis'] = {
                'detected_intent': analysis['intent'],
                'recommended_mode': recommended_mode,
                'confidence': confidence,
                'reasoning': reasoning,
                'mode_switched': False,
                'clarification_needed': True
            }
            
            return result
    
    def _process_agent_mode(self, session: Dict, message: str) -> Dict[str, Any]:
        """
        Agent mode: Full autonomous execution with workspace
        """
        # Create workspace if not exists
        if not session['workspace_id']:
            session['workspace_id'] = self.codeact_engine.create_session()
        
        # Use autonomous AI to handle the task
        task_result = self.autonomous_ai.create_task(message)
        task_id = task_result
        
        # Execute the task autonomously
        execution_result = self.codeact_engine.execute_task_autonomously(
            message, 
            session['workspace_id']
        )
        
        # Generate AI response
        ai_response = self._generate_agent_response(message, execution_result)
        
        # Add to context
        session['context'].append({
            'role': 'assistant',
            'content': ai_response['message'],
            'timestamp': time.time(),
            'mode': 'agent',
            'execution_result': execution_result,
            'task_id': task_id
        })
        
        session['task_history'].append({
            'task_id': task_id,
            'message': message,
            'execution_result': execution_result,
            'timestamp': time.time()
        })
        
        return {
            'session_id': session['session_id'],
            'mode': 'agent',
            'message': ai_response['message'],
            'execution_result': execution_result,
            'task_id': task_id,
            'workspace_id': session['workspace_id'],
            'show_code': session['preferences']['show_code'],
            'auto_executed': True,
            'timestamp': time.time()
        }
    
    def _process_chat_mode(self, session: Dict, message: str) -> Dict[str, Any]:
        """
        Chat mode: Conversational assistance and guidance
        """
        # Generate conversational response
        ai_response = self._generate_chat_response(message, session['context'])
        
        # Add to context
        session['context'].append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': time.time(),
            'mode': 'chat'
        })
        
        return {
            'session_id': session['session_id'],
            'mode': 'chat',
            'message': ai_response,
            'conversational': True,
            'suggestions': self._generate_suggestions(message),
            'timestamp': time.time()
        }
    
    def _process_custom_mode(self, session: Dict, message: str) -> Dict[str, Any]:
        """
        Custom mode: User-defined AI behavior patterns
        """
        # For now, implement as enhanced chat mode
        # In future, this could load user-defined behavior patterns
        return self._process_chat_mode(session, message)
    
    def _analyze_message_intent(self, message: str, context: List[Dict]) -> Dict[str, Any]:
        """
        Analyze message intent to recommend the best chat mode
        """
        prompt = f"""Analyze the following user message and determine the best chat mode:

Message: "{message}"

Context: {json.dumps(context[-3:], indent=2) if context else "No previous context"}

Chat Modes:
- "agent": For tasks requiring autonomous execution (coding, building, deploying, automation)
- "chat": For questions, discussions, explanations, and general conversation

Respond with JSON:
{{
    "intent": "description of user intent",
    "recommended_mode": "agent" or "chat",
    "confidence": 0.0-1.0,
    "reasoning": "explanation of recommendation"
}}"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an intent analysis expert. Analyze user messages and recommend the best chat mode. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            # Fallback analysis
            message_lower = message.lower()
            
            # Keywords that suggest agent mode
            agent_keywords = [
                'create', 'build', 'make', 'develop', 'code', 'program', 'deploy', 
                'website', 'app', 'application', 'api', 'database', 'script',
                'automate', 'generate', 'implement', 'execute', 'run'
            ]
            
            # Keywords that suggest chat mode
            chat_keywords = [
                'what', 'how', 'why', 'explain', 'tell me', 'describe', 'help',
                'question', 'understand', 'learn', 'know', 'think', 'opinion'
            ]
            
            agent_score = sum(1 for keyword in agent_keywords if keyword in message_lower)
            chat_score = sum(1 for keyword in chat_keywords if keyword in message_lower)
            
            if agent_score > chat_score:
                return {
                    'intent': 'Task execution request',
                    'recommended_mode': 'agent',
                    'confidence': min(0.8, 0.5 + agent_score * 0.1),
                    'reasoning': f'Message contains {agent_score} execution-related keywords'
                }
            else:
                return {
                    'intent': 'Conversational inquiry',
                    'recommended_mode': 'chat',
                    'confidence': min(0.8, 0.5 + chat_score * 0.1),
                    'reasoning': f'Message contains {chat_score} conversational keywords'
                }
    
    def _generate_agent_response(self, message: str, execution_result: Dict) -> Dict[str, Any]:
        """
        Generate AI response for agent mode
        """
        if execution_result['final_success']:
            response = f"✅ I've successfully completed your request! {execution_result['final_output']}"
        else:
            response = f"I encountered some challenges while working on your request. {execution_result['final_error']}"
        
        return {
            'message': response,
            'execution_summary': execution_result
        }
    
    def _generate_chat_response(self, message: str, context: List[Dict]) -> str:
        """
        Generate conversational AI response for chat mode
        """
        # Build context for the conversation
        conversation_history = []
        for ctx in context[-10:]:  # Last 10 messages
            conversation_history.append({
                'role': ctx['role'],
                'content': ctx['content']
            })
        
        conversation_history.append({
            'role': 'user',
            'content': message
        })
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Valis AI, a helpful and knowledgeable assistant. Provide clear, informative, and engaging responses. You can help with questions, explanations, and guidance on various topics."},
                    *conversation_history
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your message. Please try again."
    
    def _generate_suggestions(self, message: str) -> List[str]:
        """
        Generate helpful suggestions based on the message
        """
        message_lower = message.lower()
        
        suggestions = []
        
        if any(word in message_lower for word in ['website', 'web', 'site']):
            suggestions.extend([
                "Would you like me to create a website for you?",
                "I can help you build a landing page",
                "Need help with web development?"
            ])
        
        if any(word in message_lower for word in ['app', 'application', 'mobile']):
            suggestions.extend([
                "I can help you build an application",
                "Would you like to create a mobile app?",
                "Need assistance with app development?"
            ])
        
        if any(word in message_lower for word in ['code', 'program', 'script']):
            suggestions.extend([
                "I can write and execute code for you",
                "Would you like me to create a script?",
                "Need help with programming?"
            ])
        
        return suggestions[:3]  # Return max 3 suggestions
    
    def switch_mode(self, session_id: str, new_mode: ChatMode) -> Dict[str, Any]:
        """
        Switch chat mode for a session
        """
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        old_mode = self.active_sessions[session_id]['mode']
        self.active_sessions[session_id]['mode'] = new_mode
        self.active_sessions[session_id]['last_activity'] = time.time()
        
        return {
            'session_id': session_id,
            'old_mode': old_mode.value,
            'new_mode': new_mode.value,
            'switched_at': time.time(),
            'message': f"Switched from {old_mode.value} mode to {new_mode.value} mode"
        }
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a chat session
        """
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        session = self.active_sessions[session_id]
        
        return {
            'session_id': session_id,
            'mode': session['mode'].value,
            'created_at': session['created_at'],
            'last_activity': session['last_activity'],
            'message_count': session['message_count'],
            'workspace_id': session['workspace_id'],
            'task_count': len(session['task_history']),
            'preferences': session['preferences']
        }
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active chat sessions
        """
        return [
            {
                'session_id': session_id,
                'mode': session['mode'].value,
                'created_at': session['created_at'],
                'last_activity': session['last_activity'],
                'message_count': session['message_count'],
                'user_id': session['user_id']
            }
            for session_id, session in self.active_sessions.items()
        ]
    
    def cleanup_session(self, session_id: str) -> bool:
        """
        Clean up a chat session
        """
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Cleanup workspace if exists
            if session['workspace_id']:
                self.codeact_engine.cleanup_session(session['workspace_id'])
            
            del self.active_sessions[session_id]
            return True
        
        return False

# Global chat mode manager instance
chat_mode_manager = None

def get_chat_mode_manager(openai_api_key: str) -> ChatModeManager:
    """Get or create the global chat mode manager instance"""
    global chat_mode_manager
    if chat_mode_manager is None:
        chat_mode_manager = ChatModeManager(openai_api_key)
    return chat_mode_manager

