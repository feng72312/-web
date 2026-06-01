import { useState } from "react";
import { copyTextToClipboard } from "../utils/copyText";

interface CopyTextButtonProps {
  text: string;
  label?: string;
  className?: string;
  disabled?: boolean;
}

export function CopyTextButton({
  text,
  label = "复制",
  className = "secondary copy-text-btn",
  disabled = false,
}: CopyTextButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const ok = await copyTextToClipboard(text);
    if (!ok) {
      return;
    }
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      type="button"
      className={className}
      disabled={disabled || !text.trim()}
      onClick={handleCopy}
    >
      {copied ? "已复制" : label}
    </button>
  );
}
