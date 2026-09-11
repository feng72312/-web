import { useEffect, useState } from "react";
import { CewenTool } from "../utilities/cewen/CewenTool";
import { HepanTool } from "../utilities/hepan/HepanTool";
import { JiemengTool } from "../utilities/jiemeng/JiemengTool";
import { NamingTool } from "../utilities/naming/NamingTool";
import { ZhugeTool } from "../utilities/zhuge/ZhugeTool";
import {
  getUtilityItem,
  type UtilityId,
} from "../utilities/registry";
import { UtilityNav } from "../utilities/UtilityNav";
import { UtilityPlaceholder } from "../utilities/UtilityPlaceholder";
import type { AiChatSession } from "../components/ai/types";
import "../styles/utilities.css";

interface Props {
  activeUtility: UtilityId;
  onUtilityChange: (id: UtilityId) => void;
  onOpenAiChatSession: (session: AiChatSession) => void;
}

export function UtilsTab({
  activeUtility,
  onUtilityChange,
  onOpenAiChatSession,
}: Props) {
  const [visitedUtilities, setVisitedUtilities] = useState<UtilityId[]>([activeUtility]);

  useEffect(() => {
    setVisitedUtilities((prev) =>
      prev.includes(activeUtility) ? prev : [...prev, activeUtility],
    );
  }, [activeUtility]);

  const handleSelect = (id: UtilityId) => {
    onUtilityChange(id);
    setVisitedUtilities((prev) => (prev.includes(id) ? prev : [...prev, id]));
  };

  const renderUtility = (id: UtilityId) => {
    const item = getUtilityItem(id);
    if (!item) return null;
    if (!item.enabled) {
      return <UtilityPlaceholder item={item} />;
    }
    if (id === "hepan") {
      return <HepanTool onOpenAiChatSession={onOpenAiChatSession} />;
    }
    if (id === "zhuge") {
      return <ZhugeTool />;
    }
    if (id === "jiemeng") {
      return <JiemengTool />;
    }
    if (id === "cewen") {
      return <CewenTool />;
    }
    if (id === "naming") {
      return <NamingTool />;
    }
    return <UtilityPlaceholder item={item} />;
  };

  return (
    <div className="visual-utils-shell">
      <section className="visual-utils-hero">
        <h2>实用专区</h2>
        <p className="hint">
          轻量工具: 合盘, 诸葛神数, 周公解梦, 测字, 起名. 号码分析敬请期待.
        </p>
        <UtilityNav activeId={activeUtility} onSelect={handleSelect} />
      </section>

      <div className="visual-utils-content">
        {visitedUtilities.map((id) => (
          <div key={id} hidden={activeUtility !== id}>
            {renderUtility(id)}
          </div>
        ))}
      </div>
    </div>
  );
}
