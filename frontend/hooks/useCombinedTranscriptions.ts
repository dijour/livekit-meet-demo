import { useTrackTranscription, useVoiceAssistant, useLocalParticipant } from "@/vendor/components-js/packages/react/src";
import { useMemo } from "react";
import { Track } from "livekit-client";

export default function useCombinedTranscriptions() {
  const { agentTranscriptions } = useVoiceAssistant();
  const { localParticipant } = useLocalParticipant();

  const micTrackRef = useMemo(() => {
    if (!localParticipant) return undefined;
    const trackPub = localParticipant.getTrackPublication(Track.Source.Microphone);
    if (!trackPub) return undefined;
    return {
      participant: localParticipant,
      publication: trackPub,
      source: Track.Source.Microphone
    };
  }, [localParticipant]);

  const { segments: userTranscriptions } = useTrackTranscription(micTrackRef);

  const combinedTranscriptions = useMemo(() => {
    return [
      ...agentTranscriptions.map((val) => {
        return { ...val, role: "assistant" };
      }),
      ...userTranscriptions.map((val) => {
        return { ...val, role: "user" };
      }),
    ].sort((a, b) => a.firstReceivedTime - b.firstReceivedTime);
  }, [agentTranscriptions, userTranscriptions]);

  return combinedTranscriptions;
}
