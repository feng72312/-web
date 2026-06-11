export type VisualTheme =
  | "astro"
  | "star"
  | "hexagram"
  | "meihua"
  | "qimen"
  | "liuren"
  | "fengshui"
  | "utility"
  | "hepan"
  | "zhuge"
  | "dream"
  | "character"
  | "naming";

interface VisualSigilProps {
  theme: VisualTheme;
  size?: "sm" | "md" | "lg";
}

export function VisualSigil({ theme, size = "md" }: VisualSigilProps) {
  return (
    <div className={`visual-sigil theme-${theme} size-${size}`} aria-hidden="true">
      <span className="visual-sigil-mark">*</span>
    </div>
  );
}
