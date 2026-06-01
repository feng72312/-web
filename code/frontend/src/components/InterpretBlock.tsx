import { CopyTextButton } from "./CopyTextButton";

interface InterpretBlockProps {
  title: string;
  copyText: string;
  children: React.ReactNode;
}

export function InterpretBlock({ title, copyText, children }: InterpretBlockProps) {
  return (
    <div className="interpret-block">
      <div className="interpret-block-head">
        <h3 className="interpret-block-title">{title}</h3>
        <CopyTextButton text={copyText} />
      </div>
      {children}
    </div>
  );
}
