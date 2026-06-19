import { useInterpretQueueNotice } from "../hooks/useInterpretQueueNotice";

export function InterpretQueueBanner() {
  const message = useInterpretQueueNotice();
  if (!message) {
    return null;
  }
  return (
    <div className="interpret-queue-banner" role="status" aria-live="polite">
      {message}
    </div>
  );
}
