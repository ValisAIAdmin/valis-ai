import React, { useState, useEffect, useRef } from 'react';

const GlobalChat = ({ userId, username, userRole = 'user' }) => {
  const [channels, setChannels] = useState([]);
  const [activeChannel, setActiveChannel] = useState('general');
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);

  const channelIcons = {
    general: '💬',
    creators: '🎨',
    founders: '👑',
    support: '🛠️',
    announcements: '📢'
  };

  const roleColors = {
    guest: 'text-gray-400',
    user: 'text-blue-400',
    creator: 'text-purple-400',
    founder: 'text-yellow-400',
    moderator: 'text-green-400',
    admin: 'text-red-400'
  };

  useEffect(() => {
    // Initialize chat
    initializeChat();
    loadChannels();
    loadMessages(activeChannel);
    loadOnlineUsers();
  }, []);

  useEffect(() => {
    // Load messages when channel changes
    if (activeChannel) {
      loadMessages(activeChannel);
    }
  }, [activeChannel]);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    scrollToBottom();
  }, [messages]);

  const initializeChat = async () => {
    try {
      // Register user for global chat
      const response = await fetch('/api/chat/global/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          username: username,
          display_name: username,
          role: userRole
        })
      });

      if (response.ok) {
        setIsConnected(true);
      }
    } catch (error) {
      console.error('Failed to initialize chat:', error);
    }
  };

  const loadChannels = async () => {
    try {
      const response = await fetch(`/api/chat/global/channels?user_id=${userId}`);
      if (response.ok) {
        const data = await response.json();
        setChannels(data.channels || []);
      }
    } catch (error) {
      console.error('Failed to load channels:', error);
    }
  };

  const loadMessages = async (channelId) => {
    try {
      const response = await fetch(`/api/chat/global/messages/${channelId}?limit=50`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const loadOnlineUsers = async () => {
    try {
      const response = await fetch('/api/chat/global/online');
      if (response.ok) {
        const data = await response.json();
        setOnlineUsers(data.online_users || []);
      }
    } catch (error) {
      console.error('Failed to load online users:', error);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !isConnected) return;

    try {
      const response = await fetch('/api/chat/global/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          channel_id: activeChannel,
          content: newMessage.trim(),
          message_type: 'text'
        })
      });

      if (response.ok) {
        setNewMessage('');
        // Reload messages to show the new one
        setTimeout(() => loadMessages(activeChannel), 100);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const addReaction = async (messageId, emoji) => {
    try {
      await fetch('/api/chat/global/reaction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          message_id: messageId,
          emoji: emoji
        })
      });
      
      // Reload messages to show updated reactions
      loadMessages(activeChannel);
    } catch (error) {
      console.error('Failed to add reaction:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'now';
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    if (diffDays < 7) return `${diffDays}d`;
    return date.toLocaleDateString();
  };

  const getChannelName = (channelId) => {
    const channel = channels.find(c => c.channel_id === channelId);
    return channel ? channel.name : channelId;
  };

  return (
    <div className="flex h-full bg-gray-900 rounded-xl overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white">Global Chat</h3>
          <div className="text-sm text-gray-400">
            {onlineUsers.length} online
          </div>
        </div>

        {/* Channels */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-2">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
              Channels
            </div>
            {channels.map((channel) => (
              <button
                key={channel.channel_id}
                onClick={() => setActiveChannel(channel.channel_id)}
                className={`
                  w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors
                  ${activeChannel === channel.channel_id 
                    ? 'bg-cyan-600 text-white' 
                    : 'text-gray-300 hover:bg-gray-700'
                  }
                `}
              >
                <span className="text-lg">
                  {channelIcons[channel.channel_id] || '💬'}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{channel.name}</div>
                  {channel.member_count > 0 && (
                    <div className="text-xs opacity-75">{channel.member_count} members</div>
                  )}
                </div>
              </button>
            ))}
          </div>

          {/* Online Users */}
          <div className="p-2 border-t border-gray-700">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
              Online ({onlineUsers.length})
            </div>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {onlineUsers.slice(0, 10).map((user) => (
                <div key={user.user_id} className="flex items-center space-x-2 px-2 py-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className={`text-sm truncate ${roleColors[user.role] || 'text-gray-300'}`}>
                    {user.display_name}
                  </span>
                </div>
              ))}
              {onlineUsers.length > 10 && (
                <div className="text-xs text-gray-500 px-2">
                  +{onlineUsers.length - 10} more
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="p-4 border-b border-gray-700 bg-gray-800">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">
              {channelIcons[activeChannel] || '💬'}
            </span>
            <div>
              <h4 className="font-semibold text-white">
                {getChannelName(activeChannel)}
              </h4>
              <div className="text-sm text-gray-400">
                {messages.length} messages
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div key={message.message_id} className="group">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                  {message.username.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="font-semibold text-white">
                      {message.username}
                    </span>
                    <span className="text-xs text-gray-500">
                      {formatTimestamp(message.timestamp)}
                    </span>
                  </div>
                  <div className="text-gray-300 break-words">
                    {message.content}
                  </div>
                  
                  {/* Reactions */}
                  {message.reactions && Object.keys(message.reactions).length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {Object.entries(message.reactions).map(([emoji, users]) => (
                        <button
                          key={emoji}
                          onClick={() => addReaction(message.message_id, emoji)}
                          className="flex items-center space-x-1 px-2 py-1 bg-gray-700 rounded-full text-xs hover:bg-gray-600 transition-colors"
                        >
                          <span>{emoji}</span>
                          <span className="text-gray-400">{users.length}</span>
                        </button>
                      ))}
                    </div>
                  )}
                  
                  {/* Quick Reactions */}
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity mt-1">
                    <div className="flex space-x-1">
                      {['👍', '❤️', '😂', '😮', '😢', '😡'].map((emoji) => (
                        <button
                          key={emoji}
                          onClick={() => addReaction(message.message_id, emoji)}
                          className="text-lg hover:scale-125 transition-transform"
                        >
                          {emoji}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="p-4 border-t border-gray-700 bg-gray-800">
          <div className="flex space-x-3">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder={`Message #${getChannelName(activeChannel).toLowerCase()}`}
              className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500"
              disabled={!isConnected}
            />
            <button
              onClick={sendMessage}
              disabled={!newMessage.trim() || !isConnected}
              className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg font-semibold hover:from-cyan-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Send
            </button>
          </div>
          
          {!isConnected && (
            <div className="text-xs text-red-400 mt-2">
              Connecting to chat...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GlobalChat;

