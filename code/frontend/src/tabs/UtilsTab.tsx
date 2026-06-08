import { useState } from "react";
import { CewenTool } from "../utilities/cewen/CewenTool";
import { HepanTool } from "../utilities/hepan/HepanTool";
import { JiemengTool } from "../utilities/jiemeng/JiemengTool";
import { NamingTool } from "../utilities/naming/NamingTool";
import { ZhugeTool } from "../utilities/zhuge/ZhugeTool";
import {
  DEFAULT_UTILITY,
  getUtilityItem,
  type UtilityId,
} from "../utilities/registry";
import { UtilityNav } from "../utilities/UtilityNav";
import { UtilityPlaceholder } from "../utilities/UtilityPlaceholder";
import "../styles/utilities.css";

interface Props {
  activeUtility: UtilityId;
  onUtilityChange: (id: UtilityId) => void;
}

export function UtilsTab({ activeUtility, onUtilityChange }: Props) {
  const [visitedUtilities, setVisitedUtilities] = useState<UtilityId[]>([DEFAULT_UTILITY]);

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
      return <HepanTool />;
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
    <div className="utils-tab">
      <section className="panel utils-intro-panel">
        <h2>实用专区</h2>
        <p className="hint">
          轻量工具: 合盘, 诸葛神数, 周公解梦, 测字, 起名. 号码分析敬请期待.
        </p>
        <UtilityNav activeId={activeUtility} onSelect={handleSelect} />
      </section>

      {visitedUtilities.map((id) => (
        <div key={id} hidden={activeUtility !== id}>
          {renderUtility(id)}
        </div>
      ))}
    </div>
  );
}
