import { Fragment, type ReactNode } from "react";
import { sanitizeInterpretText } from "../utils/sanitizeInterpret";

function renderInline(text: string): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    return <Fragment key={index}>{part}</Fragment>;
  });
}

function renderParagraph(text: string, key: string): ReactNode {
  const trimmed = text.trim();
  if (!trimmed) {
    return null;
  }
  return <p key={key}>{renderInline(trimmed)}</p>;
}

interface InterpretMarkdownProps {
  text: string;
  className?: string;
}

export function InterpretMarkdown({ text, className = "" }: InterpretMarkdownProps) {
  const cleaned = sanitizeInterpretText(text);
  if (!cleaned) {
    return null;
  }

  const blocks: ReactNode[] = [];
  const paragraphs = cleaned.split(/\n{2,}/);
  paragraphs.forEach((block, blockIndex) => {
    const lines = block.split(/\n/).map((line) => line.trim()).filter(Boolean);
    if (lines.length === 0) {
      return;
    }

    const allQuotes = lines.every((line) => line.startsWith(">"));
    if (allQuotes) {
      blocks.push(
        <blockquote key={`q-${blockIndex}`}>
          {lines.map((line, lineIndex) => (
            <p key={lineIndex}>{renderInline(line.replace(/^>\s?/, ""))}</p>
          ))}
        </blockquote>,
      );
      return;
    }

    lines.forEach((line, lineIndex) => {
      const heading = line.match(/^###\s+(.+)$/);
      if (heading) {
        blocks.push(
          <h3 key={`h3-${blockIndex}-${lineIndex}`} className="interpret-md-h3">
            {renderInline(heading[1])}
          </h3>,
        );
        return;
      }
      const heading2 = line.match(/^##\s+(.+)$/);
      if (heading2) {
        blocks.push(
          <h2 key={`h2-${blockIndex}-${lineIndex}`} className="interpret-md-h2">
            {renderInline(heading2[1])}
          </h2>,
        );
        return;
      }
      if (line.startsWith(">")) {
        blocks.push(
          <blockquote key={`bq-${blockIndex}-${lineIndex}`}>
            <p>{renderInline(line.replace(/^>\s?/, ""))}</p>
          </blockquote>,
        );
        return;
      }
      if (/^-{3,}$/.test(line)) {
        return;
      }
      blocks.push(renderParagraph(line, `p-${blockIndex}-${lineIndex}`));
    });
  });

  return <div className={`interpret-markdown ${className}`.trim()}>{blocks}</div>;
}
