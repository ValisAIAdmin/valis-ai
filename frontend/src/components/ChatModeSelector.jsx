import React, { useState } from 'react';

const ChatModeSelector = ({ currentMode, onModeChange, disabled = false }) => {
  const [isOpen, setIsOpen] = useState(false);

  const modes = [
    {
      id: 'adaptive',
      name: 'Adaptive',
      description: 'AI automatically selects the best approach',
      icon: '🧠',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      id: 'agent',
      name: 'Agent',
      description: 'Full autonomous execution with workspace',
      icon: '🤖',
      color: 'from-purple-500 to-pink-500'
    },
    {
      id: 'chat',
      name: 'Chat',
      description: 'Conversational assistance and guidance',
      icon: '💬',
      color: 'from-green-500 to-emerald-500'
    },
    {
      id: 'custom',
      name: 'Custom',
      description: 'User-defined AI behavior patterns',
      icon: '⚙️',
      color: 'from-orange-500 to-red-500'
    }
  ];

  const currentModeData = modes.find(mode => mode.id === currentMode) || modes[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          flex items-center space-x-3 px-4 py-3 rounded-xl border-2 border-gray-700 
          bg-gradient-to-r ${currentModeData.color} bg-opacity-10 hover:bg-opacity-20 
          transition-all duration-200 min-w-[200px] ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <span className="text-2xl">{currentModeData.icon}</span>
        <div className="flex-1 text-left">
          <div className="font-semibold text-white">{currentModeData.name}</div>
          <div className="text-xs text-gray-400 truncate">{currentModeData.description}</div>
        </div>
        <svg 
          className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && !disabled && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-gray-800 border border-gray-700 rounded-xl shadow-2xl z-50 overflow-hidden">
          {modes.map((mode) => (
            <button
              key={mode.id}
              onClick={() => {
                onModeChange(mode.id);
                setIsOpen(false);
              }}
              className={`
                w-full flex items-center space-x-3 px-4 py-3 hover:bg-gray-700 transition-colors
                ${mode.id === currentMode ? 'bg-gray-700' : ''}
              `}
            >
              <span className="text-2xl">{mode.icon}</span>
              <div className="flex-1 text-left">
                <div className="font-semibold text-white">{mode.name}</div>
                <div className="text-xs text-gray-400">{mode.description}</div>
              </div>
              {mode.id === currentMode && (
                <svg className="w-5 h-5 text-cyan-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatModeSelector;

