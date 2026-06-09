import { motion } from "framer-motion";
import type { InterpretRunnerState } from "../hooks/useInterpretRunner";
import { InterpretMarkdown } from "./InterpretMarkdown";
import { InterpretSkeleton } from "./ui/Skeleton";
import { ErrorState } from "./ui/ErrorState";

interface InterpretStreamViewProps {
  state: InterpretRunnerState;
  streamText: string;
  finalText?: string;
  error?: string | null;
  onRetry?: () => void;
}

export function InterpretStreamView({
  state,
  streamText,
  finalText,
  error,
  onRetry,
}: InterpretStreamViewProps) {
  if (state === "error" && error) {
    return <ErrorState message={error} onRetry={onRetry} />;
  }
  if (state === "loading") {
    return <InterpretSkeleton />;
  }
  const text = state === "streaming" ? streamText : finalText ?? streamText;
  if (!text) {
    return null;
  }
  return (
    <motion.div
      className="interpret-stream-view"
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <InterpretMarkdown text={text} />
      {state === "streaming" && <span className="stream-caret" aria-hidden="true" />}
    </motion.div>
  );
}
