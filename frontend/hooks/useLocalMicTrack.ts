import { useLocalParticipant } from "@/vendor/components-js/packages/react/src";
import { Track } from "livekit-client";
import { useMemo } from "react";

export default function useLocalMicTrack() {
  const { localParticipant } = useLocalParticipant();
  
  const micTrackRef = useMemo(() => {
    if (!localParticipant) return undefined;
    
    const audioTrack = localParticipant.getTrackPublication(Track.Source.Microphone);
    return audioTrack?.track || undefined;
  }, [localParticipant]);

  return micTrackRef;
}
