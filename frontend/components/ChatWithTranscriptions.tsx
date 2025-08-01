'use client';

import React from 'react';
import { Chat } from '@/vendor/components-js/packages/react/src';
import TranscriptionView from './TranscriptionView';

export default function ChatWithTranscriptions() {
  const [showTranscriptions, setShowTranscriptions] = React.useState(false);

  return (
    <div className="lk-chat-container">
      {/* Toggle Button */}
      <div className="flex justify-between items-center p-2 border-b border-gray-200">
        <h3 className="text-sm font-medium">
          {showTranscriptions ? 'Transcriptions' : 'Chat'}
        </h3>
        <button
          onClick={() => setShowTranscriptions(!showTranscriptions)}
          className="px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          {showTranscriptions ? 'Show Chat' : 'Show Transcriptions'}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {showTranscriptions ? (
          <TranscriptionView />
        ) : (
          <Chat />
        )}
      </div>
    </div>
  );
}
