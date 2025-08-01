import { Room } from 'livekit-client';

export interface RoomContextType extends Room {
  isSimulation?: boolean;
  setIsSimulation?: (value: boolean) => void;
}
