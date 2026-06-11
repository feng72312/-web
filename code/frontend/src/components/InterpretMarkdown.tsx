import { Fragment, type ReactNode } from "react";
import { sanitizeInterpretText } from "../utils/sanitizeInterpret";

const PLAIN_SECTION_TITLES =
  "总断|一句话结论|依据|为什么这么说|趋势|接下来可能怎样|建议|你可以怎么做";

const PLAIN_SECTION_HEADING_RE = new RegExp(
  `^(?:###\\s+)?(?:${PLAIN_SECTION_TITLES})[：:]?\\s*$`,
);

const PLAIN_SECTION_INLINE_RE = new RegExp(
  `^(?:###\\s+)?(${PLAIN_SECTION_TITLES})[：:]\\s+(.+)$`,
);

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

    for (let lineIndex = 0; lineIndex < lines.length; lineIndex += 1) {
      const line = lines[lineIndex];
      const inlineSection = line.match(PLAIN_SECTION_INLINE_RE);
      if (inlineSection) {
        blocks.push(
          <h3 key={`sec-${blockIndex}-${lineIndex}`} className="interpret-md-h3 interpret-md-section">
            {inlineSection[1]}
          </h3>,
        );
        blocks.push(renderParagraph(inlineSection[2], `sec-p-${blockIndex}-${lineIndex}`));
        continue;
      }
      if (PLAIN_SECTION_HEADING_RE.test(line)) {
        const title = line.replace(/^###\s+/, "").replace(/[：:]\s*$/, "");
        blocks.push(
          <h3 key={`sec-${blockIndex}-${lineIndex}`} className="interpret-md-h3 interpret-md-section">
            {title}
          </h3>,
        );
        continue;
      }
      const heading = line.match(/^###\s+(.+)$/);
      if (heading) {
        blocks.push(
          <h3 key={`h3-${blockIndex}-${lineIndex}`} className="interpret-md-h3">
            {renderInline(heading[1])}
          </h3>,
        );
        continue;
      }
      const heading2 = line.match(/^##\s+(.+)$/);
      if (heading2) {
        blocks.push(
          <h2 key={`h2-${blockIndex}-${lineIndex}`} className="interpret-md-h2">
            {renderInline(heading2[1])}
          </h2>,
        );
        continue;
      }
      if (line.startsWith(">")) {
        blocks.push(
          <blockquote key={`bq-${blockIndex}-${lineIndex}`}>
            <p>{renderInline(line.replace(/^>\s?/, ""))}</p>
          </blockquote>,
        );
        continue;
      }
      if (/^-{3,}$/.test(line)) {
        continue;
      }
      if (line.startsWith("- ")) {
        const items: string[] = [line.slice(2).trim()];
        while (
          lineIndex + 1 < lines.length &&
          lines[lineIndex + 1].startsWith("- ")
        ) {
          lineIndex += 1;
          items.push(lines[lineIndex].slice(2).trim());
        }
        blocks.push(
          <ul key={`ul-${blockIndex}-${lineIndex}`} className="interpret-md-list">
            {items.map((item, itemIndex) => (
              <li key={itemIndex}>{renderInline(item)}</li>
            ))}
          </ul>,
        );
        continue;
      }
      blocks.push(renderParagraph(line, `p-${blockIndex}-${lineIndex}`));
    }
  });

  return <div className={`interpret-markdown ${className}`.trim()}>{blocks}</div>;
}
