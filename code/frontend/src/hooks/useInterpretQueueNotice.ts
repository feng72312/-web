import { useEffect, useState } from "react";
import { subscribeInterpretQueue } from "../utils/interpretQueue";

export function useInterpretQueueNotice(): string | null {
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => subscribeInterpretQueue((detail) => {
    if (detail.waiting && detail.message) {
      setMessage(detail.message);
      return;
    }
    setMessage(null);
  }), []);

  return message;
}
