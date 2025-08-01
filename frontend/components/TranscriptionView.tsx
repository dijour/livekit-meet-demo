import useCombinedTranscriptions from "@/hooks/useCombinedTranscriptions";
import { RoomContext } from "@/vendor/components-js/packages/react/src";
import * as React from "react";
import { RoomContextType } from "../types/room";

export default function TranscriptionView() {
  const { isSimulation } = React.useContext(RoomContext) as RoomContextType;
  const combinedTranscriptions = useCombinedTranscriptions();
  const dummyTranscriptions = React.useMemo(() => [
    { id: '1', role: 'user', text: 'Hello, can you help me with my project?' },
    { id: '2', role: 'assistant', text: 'Of course! I\'d be happy to help. What kind of project are you working on?' },
    { id: '3', role: 'user', text: 'I\'m building a React application and having trouble with state management.' },
    { id: '4', role: 'assistant', text: 'I see. There are several approaches to state management in React. Could you tell me more about your specific requirements?' }
  ], []);
  const containerRef = React.useRef<HTMLDivElement>(null);

  // scroll to bottom when new transcription is added
  React.useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [combinedTranscriptions]);

  return (
    <div className="relative h-[200px] w-[512px] max-w-[90vw] mx-auto">
      {/* Fade-out gradient mask */}

      {/* Scrollable content */}
      <div ref={containerRef} className="h-full flex flex-col gap-2 overflow-y-auto px-4 py-8">
        {(isSimulation ? dummyTranscriptions : combinedTranscriptions).map((segment) => (
          <div
            id={segment.id}
            key={segment.id}
            className={
              segment.role === "assistant"
                ? "p-2 self-start fit-content"
                : "bg-[#0078BE]/[0.16] rounded-l-xl rounded-br-xl px-4 py-3 self-end fit-content"
            }
          >
            {segment.text}
          </div>
        ))}
      </div>
    </div>
  );
}
