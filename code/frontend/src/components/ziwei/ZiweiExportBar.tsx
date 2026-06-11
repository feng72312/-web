import { useState, type RefObject } from "react";

interface ZiweiExportBarProps {
  boardRef: RefObject<HTMLDivElement | null>;
}

export function ZiweiExportBar({ boardRef }: ZiweiExportBarProps) {
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState("");

  const handlePrint = () => {
    window.print();
  };

  const handleExportImage = async () => {
    const node = boardRef.current;
    if (!node) {
      return;
    }
    setExporting(true);
    setError("");
    try {
      const { toPng } = await import("html-to-image");
      const dataUrl = await toPng(node, {
        cacheBust: true,
        pixelRatio: 2,
        backgroundColor: getComputedStyle(document.body).backgroundColor || "#fffdf8",
      });
      const link = document.createElement("a");
      link.download = `ziwei-chart-${Date.now()}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      setError(err instanceof Error ? err.message : "导出失败");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="ziwei-export-bar">
      <button type="button" className="ziwei-export-btn" onClick={handlePrint}>
        打印盘面
      </button>
      <button
        type="button"
        className="ziwei-export-btn"
        disabled={exporting}
        onClick={() => void handleExportImage()}
      >
        {exporting ? "导出中..." : "导出图片"}
      </button>
      {error ? <span className="ziwei-export-error">{error}</span> : null}
    </div>
  );
}
