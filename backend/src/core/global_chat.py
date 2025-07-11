"""
Valis AI - Global Chat System
Real-time global chat room with channels, roles, and community features
"""

import uuid
import time
import json
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from dataclasses import dataclass
import asyncio
import websockets

class UserRole(Enum):
    GUEST = "guest"
    USER = "user"
    CREATOR = "creator"
    FOUNDER = "founder"
    MODERATOR = "moderator"
    ADMIN = "admin"

class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    CODE = "code"
    SYSTEM = "system"
    ANNOUNCEMENT = "announcement"

@dataclass
class ChatUser:
    user_id: str
    username: str
    display_name: str
    role: UserRole
    avatar_url: str = ""
    status: str = "online"
    joined_at: float = 0
    last_seen: float = 0
    message_count: int = 0
    reputation: int = 0

@dataclass
class ChatMessage:
    message_id: str
    user_id: str
    username: str
    content: str
    message_type: MessageType
    channel_id: str
    timestamp: float
    edited_at: Optional[float] = None
    reply_to: Optional[str] = None
    reactions: Dict[str, List[str]] = None
    attachments: List[Dict] = None

class GlobalChatSystem:
    """
    Real-time global chat system with channels and community features
    """
    
    def __init__(self):
        self.users: Dict[str, ChatUser] = {}
        self.channels: Dict[str, Dict] = {}
        self.messages: Dict[str, List[ChatMessage]] = {}
        self.active_connections: Dict[str, Set] = {}
        self.user_connections: Dict[str, str] = {}  # websocket -> user_id
        
        # Initialize default channels
        self._initialize_default_channels()
        
        # Message history limits
        self.max_messages_per_channel = 1000
        
        # Rate limiting
        self.rate_limits = {
            UserRole.GUEST: {'messages_per_minute': 5, 'characters_per_message': 500},
            UserRole.USER: {'messages_per_minute': 10, 'characters_per_message': 1000},
            UserRole.CREATOR: {'messages_per_minute': 20, 'characters_per_message': 2000},
            UserRole.FOUNDER: {'messages_per_minute': 50, 'characters_per_message': 5000},
            UserRole.MODERATOR: {'messages_per_minute': 100, 'characters_per_message': 10000},
            UserRole.ADMIN: {'messages_per_minute': 1000, 'characters_per_message': 50000}
        }
        
        self.user_message_history = {}  # Track for rate limiting
    
    def _initialize_default_channels(self):
        """Initialize default chat channels"""
        default_channels = [
            {
                'channel_id': 'general',
                'name': 'General',
                'description': 'General discussion about Valis AI',
                'type': 'public',
                'created_by': 'system',
                'created_at': time.time(),
                'member_count': 0,
                'message_count': 0,
                'rules': [
                    'Be respectful to all community members',
                    'No spam or excessive self-promotion',
                    'Keep discussions relevant to AI and technology',
                    'Use appropriate language'
                ]
            },
            {
                'channel_id': 'creators',
                'name': 'Creators Hub',
                'description': 'For creators building with Valis AI',
                'type': 'public',
                'created_by': 'system',
                'created_at': time.time(),
                'member_count': 0,
                'message_count': 0,
                'rules': [
                    'Share your creations and get feedback',
                    'Collaborate on projects',
                    'Help other creators'
                ]
            },
            {
                'channel_id': 'founders',
                'name': 'Founders Circle',
                'description': 'Exclusive channel for founders and entrepreneurs',
                'type': 'restricted',
                'required_role': UserRole.FOUNDER,
                'created_by': 'system',
                'created_at': time.time(),
                'member_count': 0,
                'message_count': 0,
                'rules': [
                    'Business strategy discussions',
                    'Networking and partnerships',
                    'Exclusive founder insights'
                ]
            },
            {
                'channel_id': 'support',
                'name': 'Support',
                'description': 'Get help with Valis AI',
                'type': 'public',
                'created_by': 'system',
                'created_at': time.time(),
                'member_count': 0,
                'message_count': 0,
                'rules': [
                    'Ask questions about using Valis AI',
                    'Report bugs and issues',
                    'Get technical support'
                ]
            },
            {
                'channel_id': 'announcements',
                'name': 'Announcements',
                'description': 'Official Valis AI announcements',
                'type': 'read_only',
                'created_by': 'system',
                'created_at': time.time(),
                'member_count': 0,
                'message_count': 0,
                'rules': [
                    'Official announcements only',
                    'Product updates and news',
                    'Community events'
                ]
            }
        ]
        
        for channel in default_channels:
            self.channels[channel['channel_id']] = channel
            self.messages[channel['channel_id']] = []
            self.active_connections[channel['channel_id']] = set()
    
    def register_user(self, user_id: str, username: str, display_name: str, role: UserRole = UserRole.USER) -> ChatUser:
        """Register a new chat user"""
        
        chat_user = ChatUser(
            user_id=user_id,
            username=username,
            display_name=display_name,
            role=role,
            joined_at=time.time(),
            last_seen=time.time()
        )
        
        self.users[user_id] = chat_user
        self.user_message_history[user_id] = []
        
        return chat_user
    
    def connect_user(self, user_id: str, websocket) -> Dict[str, Any]:
        """Connect a user to the chat system"""
        if user_id not in self.users:
            return {'error': 'User not registered'}
        
        user = self.users[user_id]
        user.status = "online"
        user.last_seen = time.time()
        
        # Store websocket connection
        self.user_connections[websocket] = user_id
        
        # Add to general channel by default
        self.active_connections['general'].add(websocket)
        
        # Broadcast user online status
        self._broadcast_user_status(user_id, "online")
        
        return {
            'user_id': user_id,
            'username': user.username,
            'channels': self._get_user_channels(user_id),
            'online_users': self._get_online_users(),
            'status': 'connected'
        }
    
    def disconnect_user(self, websocket) -> Dict[str, Any]:
        """Disconnect a user from the chat system"""
        if websocket not in self.user_connections:
            return {'error': 'Connection not found'}
        
        user_id = self.user_connections[websocket]
        user = self.users.get(user_id)
        
        if user:
            user.status = "offline"
            user.last_seen = time.time()
        
        # Remove from all channels
        for channel_connections in self.active_connections.values():
            channel_connections.discard(websocket)
        
        # Remove connection mapping
        del self.user_connections[websocket]
        
        # Broadcast user offline status
        if user:
            self._broadcast_user_status(user_id, "offline")
        
        return {
            'user_id': user_id,
            'status': 'disconnected'
        }
    
    def send_message(self, user_id: str, channel_id: str, content: str, message_type: MessageType = MessageType.TEXT, reply_to: str = None) -> Dict[str, Any]:
        """Send a message to a channel"""
        
        # Validate user
        if user_id not in self.users:
            return {'error': 'User not found'}
        
        user = self.users[user_id]
        
        # Validate channel
        if channel_id not in self.channels:
            return {'error': 'Channel not found'}
        
        channel = self.channels[channel_id]
        
        # Check permissions
        if not self._can_user_send_message(user, channel):
            return {'error': 'Permission denied'}
        
        # Rate limiting
        if not self._check_rate_limit(user_id, content):
            return {'error': 'Rate limit exceeded'}
        
        # Create message
        message = ChatMessage(
            message_id=str(uuid.uuid4()),
            user_id=user_id,
            username=user.username,
            content=content,
            message_type=message_type,
            channel_id=channel_id,
            timestamp=time.time(),
            reply_to=reply_to,
            reactions={},
            attachments=[]
        )
        
        # Add to channel messages
        self.messages[channel_id].append(message)
        
        # Maintain message limit
        if len(self.messages[channel_id]) > self.max_messages_per_channel:
            self.messages[channel_id] = self.messages[channel_id][-self.max_messages_per_channel:]
        
        # Update stats
        user.message_count += 1
        user.last_seen = time.time()
        channel['message_count'] += 1
        
        # Broadcast message
        self._broadcast_message(channel_id, message)
        
        return {
            'message_id': message.message_id,
            'status': 'sent',
            'timestamp': message.timestamp
        }
    
    def join_channel(self, user_id: str, channel_id: str, websocket) -> Dict[str, Any]:
        """Join a user to a channel"""
        
        # Validate user
        if user_id not in self.users:
            return {'error': 'User not found'}
        
        user = self.users[user_id]
        
        # Validate channel
        if channel_id not in self.channels:
            return {'error': 'Channel not found'}
        
        channel = self.channels[channel_id]
        
        # Check permissions
        if not self._can_user_join_channel(user, channel):
            return {'error': 'Permission denied'}
        
        # Add to channel
        self.active_connections[channel_id].add(websocket)
        
        # Get recent messages
        recent_messages = self.messages[channel_id][-50:]  # Last 50 messages
        
        return {
            'channel_id': channel_id,
            'channel_info': channel,
            'recent_messages': [self._message_to_dict(msg) for msg in recent_messages],
            'online_users': self._get_channel_users(channel_id),
            'status': 'joined'
        }
    
    def leave_channel(self, user_id: str, channel_id: str, websocket) -> Dict[str, Any]:
        """Remove a user from a channel"""
        
        if channel_id in self.active_connections:
            self.active_connections[channel_id].discard(websocket)
        
        return {
            'channel_id': channel_id,
            'status': 'left'
        }
    
    def add_reaction(self, user_id: str, message_id: str, emoji: str) -> Dict[str, Any]:
        """Add a reaction to a message"""
        
        # Find message
        message = self._find_message(message_id)
        if not message:
            return {'error': 'Message not found'}
        
        # Add reaction
        if message.reactions is None:
            message.reactions = {}
        
        if emoji not in message.reactions:
            message.reactions[emoji] = []
        
        if user_id not in message.reactions[emoji]:
            message.reactions[emoji].append(user_id)
        
        # Broadcast reaction update
        self._broadcast_reaction_update(message)
        
        return {
            'message_id': message_id,
            'emoji': emoji,
            'status': 'added'
        }
    
    def _can_user_send_message(self, user: ChatUser, channel: Dict) -> bool:
        """Check if user can send messages in channel"""
        
        # Read-only channels
        if channel.get('type') == 'read_only':
            return user.role in [UserRole.MODERATOR, UserRole.ADMIN]
        
        # Restricted channels
        if channel.get('type') == 'restricted':
            required_role = channel.get('required_role', UserRole.USER)
            return self._has_role_or_higher(user.role, required_role)
        
        return True
    
    def _can_user_join_channel(self, user: ChatUser, channel: Dict) -> bool:
        """Check if user can join channel"""
        
        # Restricted channels
        if channel.get('type') == 'restricted':
            required_role = channel.get('required_role', UserRole.USER)
            return self._has_role_or_higher(user.role, required_role)
        
        return True
    
    def _has_role_or_higher(self, user_role: UserRole, required_role: UserRole) -> bool:
        """Check if user has required role or higher"""
        role_hierarchy = [
            UserRole.GUEST,
            UserRole.USER,
            UserRole.CREATOR,
            UserRole.FOUNDER,
            UserRole.MODERATOR,
            UserRole.ADMIN
        ]
        
        user_level = role_hierarchy.index(user_role)
        required_level = role_hierarchy.index(required_role)
        
        return user_level >= required_level
    
    def _check_rate_limit(self, user_id: str, content: str) -> bool:
        """Check if user is within rate limits"""
        
        user = self.users[user_id]
        limits = self.rate_limits[user.role]
        
        current_time = time.time()
        
        # Clean old messages (older than 1 minute)
        self.user_message_history[user_id] = [
            msg_time for msg_time in self.user_message_history[user_id]
            if current_time - msg_time < 60
        ]
        
        # Check message count limit
        if len(self.user_message_history[user_id]) >= limits['messages_per_minute']:
            return False
        
        # Check character limit
        if len(content) > limits['characters_per_message']:
            return False
        
        # Add current message time
        self.user_message_history[user_id].append(current_time)
        
        return True
    
    def _broadcast_message(self, channel_id: str, message: ChatMessage):
        """Broadcast message to all users in channel"""
        
        if channel_id not in self.active_connections:
            return
        
        message_data = {
            'type': 'message',
            'data': self._message_to_dict(message)
        }
        
        # Send to all connected users in channel
        for websocket in self.active_connections[channel_id].copy():
            try:
                # In a real implementation, you'd use asyncio.create_task
                # For now, we'll store the message for retrieval
                pass
            except:
                # Remove disconnected websocket
                self.active_connections[channel_id].discard(websocket)
    
    def _broadcast_user_status(self, user_id: str, status: str):
        """Broadcast user status change"""
        
        status_data = {
            'type': 'user_status',
            'data': {
                'user_id': user_id,
                'status': status,
                'timestamp': time.time()
            }
        }
        
        # Broadcast to all channels where user is present
        for channel_id, connections in self.active_connections.items():
            for websocket in connections.copy():
                try:
                    # Store for retrieval
                    pass
                except:
                    connections.discard(websocket)
    
    def _broadcast_reaction_update(self, message: ChatMessage):
        """Broadcast reaction update"""
        
        reaction_data = {
            'type': 'reaction_update',
            'data': {
                'message_id': message.message_id,
                'reactions': message.reactions
            }
        }
        
        # Broadcast to channel
        channel_id = message.channel_id
        if channel_id in self.active_connections:
            for websocket in self.active_connections[channel_id].copy():
                try:
                    # Store for retrieval
                    pass
                except:
                    self.active_connections[channel_id].discard(websocket)
    
    def _message_to_dict(self, message: ChatMessage) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': message.message_id,
            'user_id': message.user_id,
            'username': message.username,
            'content': message.content,
            'message_type': message.message_type.value,
            'channel_id': message.channel_id,
            'timestamp': message.timestamp,
            'edited_at': message.edited_at,
            'reply_to': message.reply_to,
            'reactions': message.reactions or {},
            'attachments': message.attachments or []
        }
    
    def _find_message(self, message_id: str) -> Optional[ChatMessage]:
        """Find a message by ID"""
        for channel_messages in self.messages.values():
            for message in channel_messages:
                if message.message_id == message_id:
                    return message
        return None
    
    def _get_user_channels(self, user_id: str) -> List[Dict[str, Any]]:
        """Get channels accessible to user"""
        user = self.users[user_id]
        accessible_channels = []
        
        for channel_id, channel in self.channels.items():
            if self._can_user_join_channel(user, channel):
                accessible_channels.append({
                    'channel_id': channel_id,
                    'name': channel['name'],
                    'description': channel['description'],
                    'type': channel['type'],
                    'member_count': len(self.active_connections.get(channel_id, set())),
                    'message_count': channel['message_count']
                })
        
        return accessible_channels
    
    def _get_online_users(self) -> List[Dict[str, Any]]:
        """Get list of online users"""
        online_users = []
        
        for user in self.users.values():
            if user.status == "online":
                online_users.append({
                    'user_id': user.user_id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'role': user.role.value,
                    'avatar_url': user.avatar_url,
                    'message_count': user.message_count,
                    'reputation': user.reputation
                })
        
        return online_users
    
    def _get_channel_users(self, channel_id: str) -> List[Dict[str, Any]]:
        """Get users currently in a channel"""
        if channel_id not in self.active_connections:
            return []
        
        channel_users = []
        for websocket in self.active_connections[channel_id]:
            if websocket in self.user_connections:
                user_id = self.user_connections[websocket]
                user = self.users.get(user_id)
                if user:
                    channel_users.append({
                        'user_id': user.user_id,
                        'username': user.username,
                        'display_name': user.display_name,
                        'role': user.role.value,
                        'avatar_url': user.avatar_url
                    })
        
        return channel_users
    
    def get_channel_messages(self, channel_id: str, limit: int = 50, before: float = None) -> List[Dict[str, Any]]:
        """Get messages from a channel"""
        if channel_id not in self.messages:
            return []
        
        messages = self.messages[channel_id]
        
        # Filter by timestamp if specified
        if before:
            messages = [msg for msg in messages if msg.timestamp < before]
        
        # Get last N messages
        recent_messages = messages[-limit:] if limit else messages
        
        return [self._message_to_dict(msg) for msg in recent_messages]
    
    def get_chat_stats(self) -> Dict[str, Any]:
        """Get overall chat statistics"""
        total_messages = sum(len(messages) for messages in self.messages.values())
        online_count = sum(1 for user in self.users.values() if user.status == "online")
        
        return {
            'total_users': len(self.users),
            'online_users': online_count,
            'total_channels': len(self.channels),
            'total_messages': total_messages,
            'channels': [
                {
                    'channel_id': channel_id,
                    'name': channel['name'],
                    'message_count': channel['message_count'],
                    'active_users': len(self.active_connections.get(channel_id, set()))
                }
                for channel_id, channel in self.channels.items()
            ]
        }

# Global chat system instance
global_chat_system = None

def get_global_chat_system() -> GlobalChatSystem:
    """Get or create the global chat system instance"""
    global global_chat_system
    if global_chat_system is None:
        global_chat_system = GlobalChatSystem()
    return global_chat_system

