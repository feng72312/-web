interface AiQuickPromptsProps {
  prompts: string[];
  disabled?: boolean;
  onSelect: (prompt: string) => void;
}

export function AiQuickPrompts({
  prompts,
  disabled = false,
  onSelect,
}: AiQuickPromptsProps) {
  if (prompts.length === 0) {
    return null;
  }

  return (
    <div className="ai-chat-quick-prompts">
      {prompts.map((prompt) => (
        <button
          key={prompt}
          type="button"
          className="ai-chat-prompt-chip"
          disabled={disabled}
          onClick={() => onSelect(prompt)}
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}
