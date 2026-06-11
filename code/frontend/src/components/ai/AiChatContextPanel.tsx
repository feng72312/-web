import { InterpretModelPicker } from "../InterpretModelPicker";
import { AiQuickPrompts } from "./AiQuickPrompts";
import { FusionSourcePicker } from "./FusionSourcePicker";
import { getScenarioConfig } from "./scenarioConfig";
import type { ChatModelOption } from "../../types/bazi";
import type { GeneralChatScenario } from "../../services/chatApi";
import type { FusionChartSource } from "./fusionTypes";
import type { AiChatSessionSource } from "./types";

const FUSION_QUICK_PROMPTS = [
  "请先总览这几个盘有哪些同向判断?",
  "哪些地方结论冲突, 各自来自什么体系视角?",
  "结合大运流年与紫微大限, 近几年重点看哪里?",
  "若只问事业财运, 哪个盘的信息更直接可用?",
];

interface AiChatContextPanelProps {
  chatEnabled: boolean;
  chatModels: ChatModelOption[];
  selectedModel: string;
  onModelChange: (modelId: string) => void;
  activeScenario: GeneralChatScenario;
  sessionTitle: string;
  sessionSource: AiChatSessionSource;
  sessionBusy?: boolean;
  fusionSources: FusionChartSource[];
  selectedFusionIds: string[];
  fusionImportBusy?: boolean;
  onToggleFusionSource: (sourceId: string) => void;
  onRemoveFusionSource: (sourceId: string) => void;
  onCreateFusionSession: () => void;
  onQuickPrompt: (prompt: string) => void;
  onGoModules: () => void;
}

export function AiChatContextPanel({
  chatEnabled,
  chatModels,
  selectedModel,
  onModelChange,
  activeScenario,
  sessionTitle,
  sessionSource,
  sessionBusy = false,
  fusionSources,
  selectedFusionIds,
  fusionImportBusy = false,
  onToggleFusionSource,
  onRemoveFusionSource,
  onCreateFusionSession,
  onQuickPrompt,
  onGoModules,
}: AiChatContextPanelProps) {
  const scenario = getScenarioConfig(activeScenario);
  const isModuleSession = sessionSource === "module";
  const isFusionSession = sessionSource === "fusion";
  const quickPrompts = isFusionSession ? FUSION_QUICK_PROMPTS : (scenario?.quickPrompts ?? []);

  return (
    <aside className="ai-chat-context-panel">
      <section className="ai-chat-context-block">
        <h3>当前会话</h3>
        <p className="ai-chat-context-title">{sessionTitle}</p>
        <p className="ai-chat-context-desc">
          {isFusionSession
            ? "已加载多个盘面进行融合分析, 可继续追问同向点, 冲突点与综合建议."
            : isModuleSession
              ? "已绑定当前排盘或牌阵, 可继续追问判断依据, 细节和后续建议."
              : (scenario?.description ?? "通用术数问答会话.")}
        </p>
      </section>

      <FusionSourcePicker
        sources={fusionSources}
        selectedIds={selectedFusionIds}
        disabled={!chatEnabled || sessionBusy || fusionImportBusy}
        onToggle={onToggleFusionSource}
        onRemove={onRemoveFusionSource}
        onCreateFusion={onCreateFusionSession}
      />

      <section className="ai-chat-context-block">
        <h3>AI 模型</h3>
        <InterpretModelPicker
          models={chatModels}
          value={selectedModel}
          onChange={onModelChange}
          chatEnabled={chatEnabled}
          disabled={sessionBusy}
        />
        {chatEnabled ? (
          <p className="ai-chat-context-hint">
            切换模型后, 下一条消息将按所选模型发送.
          </p>
        ) : null}
      </section>

      <section className="ai-chat-context-block">
        <h3>快捷问题</h3>
        <AiQuickPrompts
          prompts={quickPrompts}
          disabled={!chatEnabled || sessionBusy}
          onSelect={onQuickPrompt}
        />
      </section>

      <section className="ai-chat-context-block">
        <h3>使用建议</h3>
        <ul className="ai-chat-context-tips">
          <li>模块内打开 AI 对话后, 会进入当前页面继续追问对应排盘或牌阵.</li>
          <li>左侧历史记录可加载排盘档案; 右侧勾选素材后可创建融合分析会话.</li>
          <li>涉及医疗, 法律, 投资等重大决策请寻求专业人士意见.</li>
        </ul>
        <button type="button" className="product-gold-button" onClick={onGoModules}>
          前往预测模块
        </button>
      </section>
    </aside>
  );
}
