import { TarotVisualDemo } from "../components/tarot/TarotVisualDemo";
import type { AiChatSession } from "../components/ai/types";

interface TarotTabProps {
  onOpenAiChatSession: (session: AiChatSession) => void;
}

export function TarotTab({ onOpenAiChatSession }: TarotTabProps) {
  return <TarotVisualDemo onOpenAiChatSession={onOpenAiChatSession} />;
}
