'use client';

import React from 'react';
import TranscriptionView from './TranscriptionView';

export default function TranscriptionToggle() {
  const [showTranscriptions, setShowTranscriptions] = React.useState(false);

  return (
    <>
      {/* Toggle Button - Fixed position */}
      <button
        onClick={() => setShowTranscriptions(!showTranscriptions)}
        className="fixed top-4 right-4 z-50 px-4 py-2 bg-blue-600 text-white rounded-lg shadow-lg hover:bg-blue-700 transition-colors"
        title={showTranscriptions ? 'Hide Transcriptions' : 'Show Transcriptions'}
      >
        {showTranscriptions ? '💬 Hide Transcriptions' : '📝 Show Transcriptions'}
      </button>

      {/* Transcription Overlay */}
      {showTranscriptions && (
        <div className="fixed top-16 right-4 z-40 bg-white rounded-lg shadow-xl border border-gray-200 max-w-md w-full">
          <div className="p-3 border-b border-gray-200 flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-800">Live Transcriptions</h3>
            <button
              onClick={() => setShowTranscriptions(false)}
              className="text-gray-500 hover:text-gray-700 text-xl"
              title="Close"
            >
              ×
            </button>
          </div>
          <div className="p-2">
            <TranscriptionView />
          </div>
        </div>
      )}
    </>
  );
}
