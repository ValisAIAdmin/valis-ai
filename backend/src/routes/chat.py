"""
Valis AI - Chat Routes
API endpoints for chat modes and messaging
"""

from flask import Blueprint, request, jsonify
from core.chat_modes import get_chat_mode_manager, ChatMode
from core.global_chat import get_global_chat_system, UserRole, MessageType
from config import OPENAI_API_KEY

chat_bp = Blueprint('chat', __name__)

# Chat Modes Routes
@chat_bp.route('/modes/session', methods=['POST'])
def create_chat_session():
    """Create a new chat session"""
    try:
        data = request.get_json()
        mode = data.get('mode', 'adaptive')
        user_id = data.get('user_id', 'anonymous')
        
        chat_mode_manager = get_chat_mode_manager(OPENAI_API_KEY)
        session_id = chat_mode_manager.create_chat_session(ChatMode(mode), user_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'mode': mode
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/modes/message', methods=['POST'])
def send_chat_message():
    """Send a message in chat mode"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message', '')
        mode = data.get('mode')
        
        if not session_id or not message:
            return jsonify({'error': 'Session ID and message required'}), 400
        
        chat_mode_manager = get_chat_mode_manager(OPENAI_API_KEY)
        
        # Convert mode string to enum if provided
        chat_mode = ChatMode(mode) if mode else None
        
        result = chat_mode_manager.process_message(session_id, message, chat_mode)
        
        return jsonify({
            'success': True,
            'response': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/modes/switch', methods=['POST'])
def switch_chat_mode():
    """Switch chat mode for a session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        new_mode = data.get('mode')
        
        if not session_id or not new_mode:
            return jsonify({'error': 'Session ID and mode required'}), 400
        
        chat_mode_manager = get_chat_mode_manager(OPENAI_API_KEY)
        result = chat_mode_manager.switch_mode(session_id, ChatMode(new_mode))
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/modes/session/<session_id>', methods=['GET'])
def get_chat_session_info(session_id):
    """Get information about a chat session"""
    try:
        chat_mode_manager = get_chat_mode_manager(OPENAI_API_KEY)
        session_info = chat_mode_manager.get_session_info(session_id)
        
        return jsonify({
            'success': True,
            'session_info': session_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Global Chat Routes
@chat_bp.route('/global/register', methods=['POST'])
def register_chat_user():
    """Register a user for global chat"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        username = data.get('username')
        display_name = data.get('display_name', username)
        role = data.get('role', 'user')
        
        if not user_id or not username:
            return jsonify({'error': 'User ID and username required'}), 400
        
        global_chat = get_global_chat_system()
        chat_user = global_chat.register_user(user_id, username, display_name, UserRole(role))
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': chat_user.user_id,
                'username': chat_user.username,
                'display_name': chat_user.display_name,
                'role': chat_user.role.value,
                'joined_at': chat_user.joined_at
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/global/channels', methods=['GET'])
def get_chat_channels():
    """Get available chat channels"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        global_chat = get_global_chat_system()
        
        # Get user channels (this checks permissions)
        if user_id in global_chat.users:
            channels = global_chat._get_user_channels(user_id)
        else:
            # Return public channels for unregistered users
            channels = [
                {
                    'channel_id': 'general',
                    'name': 'General',
                    'description': 'General discussion about Valis AI',
                    'type': 'public'
                }
            ]
        
        return jsonify({
            'success': True,
            'channels': channels
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/global/messages/<channel_id>', methods=['GET'])
def get_channel_messages(channel_id):
    """Get messages from a channel"""
    try:
        limit = int(request.args.get('limit', 50))
        before = request.args.get('before')
        
        if before:
            before = float(before)
        
        global_chat = get_global_chat_system()
        messages = global_chat.get_channel_messages(channel_id, limit, before)
        
        return jsonify({
            'success': True,
            'messages': messages,
            'channel_id': channel_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/global/send', methods=['POST'])
def send_global_message():
    """Send a message to global chat"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        channel_id = data.get('channel_id')
        content = data.get('content', '')
        message_type = data.get('message_type', 'text')
        reply_to = data.get('reply_to')
        
        if not user_id or not channel_id or not content:
            return jsonify({'error': 'User ID, channel ID, and content required'}), 400
        
        global_chat = get_global_chat_system()
        result = global_chat.send_message(
            user_id, 
            channel_id, 
            content, 
            MessageType(message_type),
            reply_to
        )
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/global/reaction', methods=['POST'])
def add_message_reaction():
    """Add a reaction to a message"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        message_id = data.get('message_id')
        emoji = data.get('emoji')
        
        if not user_id or not message_id or not emoji:
            return jsonify({'error': 'User ID, message ID, and emoji required'}), 400
        
        global_chat = get_global_chat_system()
        result = global_chat.add_reaction(user_id, message_id, emoji)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/global/online', methods=['GET'])
def get_online_users():
    """Get list of online users"""
    try:
        global_chat = get_global_chat_system()
        online_users = global_chat._get_online_users()
        
        return jsonify({
            'success': True,
            'online_users': online_users,
            'count': len(online_users)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/global/stats', methods=['GET'])
def get_chat_stats():
    """Get chat statistics"""
    try:
        global_chat = get_global_chat_system()
        stats = global_chat.get_chat_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

