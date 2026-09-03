import { useEffect, useState } from "react";
import { BaziVisualDemo } from "../components/bazi/BaziVisualDemo";
import { appendTimelineEntry } from "../services/reportTimeline";
import {
  fetchInterpret,
  fetchInterpretStream,
  fetchLuckTimeline,
  fetchPaipan,
} from "../services/api";
import { fetchRagStatus, type RagStatus } from "../services/ragApi";
import { fetchChatStatus, initChatSession } from "../services/chatApi";
import { buildBaziFusionSource } from "../components/ai/fusionSourceBuilder";
import { upsertFusionSource } from "../components/ai/fusionSourceStorage";
import { openModuleAiChatSession } from "../components/ai/moduleChatBridge";
import { createModuleChatSessionRecord } from "../components/ai/moduleSession";
import type { AiChatSession } from "../components/ai/types";
import { saveBaziChartRef } from "../utils/baziChartCache";
import { deferIdle } from "../utils/deferIdle";
import { mergeInterpretSummary, type InterpretStyle } from "../utils/interpretStyle";
import type {
  ChatModelOption,
  Interpretation,
  LuckTimeline,
  PaipanRequest,
  PaipanResponse,
} from "../types/bazi";

interface BaziTabProps {
  onOpenAiChatSession: (session: AiChatSession) => void;
}

export function BaziTab({ onOpenAiChatSession }: BaziTabProps) {
  const [paipanLoading, setPaipanLoading] = useState(false);
  const [luckLoading, setLuckLoading] = useState(false);
  const [luckTimeline, setLuckTimeline] = useState<LuckTimeline | null>(null);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
  const [, setChatInitLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<PaipanResponse | null>(null);
  const [lastRequest, setLastRequest] = useState<PaipanRequest | null>(null);
  const [interpretation, setInterpretation] = useState<Interpretation | null>(null);
  const [chatAgentId, setChatAgentId] = useState<string | null>(null);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [ragStatus, setRagStatus] = useState<RagStatus | null>(null);
  const [interpretQuestion, setInterpretQuestion] = useState(
    "请论此命主格局、用神喜忌与一生大势",
  );
  const [streamingSummary, setStreamingSummary] = useState("");
  const [interpretStage, setInterpretStage] = useState("");

  useEffect(() => {
    fetchChatStatus()
      .then((status) => {
        setChatEnabled(status.enabled);
        setChatModels(status.models ?? []);
        if (status.model) {
          setSelectedModel(status.model);
        } else if (status.models?.length) {
          setSelectedModel(status.models[0].id);
        }
      })
      .catch(() => {
        setChatEnabled(false);
      });
  }, []);

  useEffect(() => {
    if (!result) {
      setRagStatus(null);
      return;
    }
    fetchRagStatus()
      .then(setRagStatus)
      .catch(() => setRagStatus(null));
  }, [result]);

  const startChatSession = async (paipan: PaipanResponse): Promise<string | null> => {
    if (!chatEnabled) {
      return null;
    }
    setChatInitLoading(true);
    try {
      const id = await initChatSession(
        paipan.chart as unknown as Record<string, unknown>,
        paipan.sections as unknown as Array<Record<string, unknown>>,
      );
      setChatAgentId(id);
      return id;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "AI 对话连接失败";
      setError(msg);
      return null;
    } finally {
      setChatInitLoading(false);
    }
  };

  const handleOpenAiChat = async () => {
    if (!result) {
      return;
    }
    const agentId = chatAgentId ?? interpretation?.agentId ?? (await startChatSession(result));
    if (!agentId) {
      return;
    }
    const chart = result.chart;
    const fusionSource = buildBaziFusionSource({
      chart: result.chart as unknown as Record<string, unknown>,
      question: interpretQuestion.trim(),
      chartName: chart.input?.name || chart.dayMaster || "命盘",
      subtitle: chart.dayMaster,
      summaryPlain: interpretation?.summaryPlain,
      summaryProfessional: interpretation?.summaryProfessional,
      agentId,
    });
    await openModuleAiChatSession(
      createModuleChatSessionRecord({
        agentId,
        moduleId: "01",
        moduleLabel: "八字",
        question: interpretQuestion.trim(),
        chartName: chart.input?.name || chart.dayMaster || "命盘",
        subtitle: chart.dayMaster,
      }),
      interpretation,
      onOpenAiChatSession,
      fusionSource,
    );
  };

  useEffect(() => {
    const onAuthCancelled = () => setInterpretStyleLoading(null);
    window.addEventListener("zy-auth-cancelled", onAuthCancelled);
    return () => window.removeEventListener("zy-auth-cancelled", onAuthCancelled);
  }, []);

  const handleSubmit = async (data: PaipanRequest) => {
    setPaipanLoading(true);
    setError("");
    setInterpretation(null);
    setChatAgentId(null);
    setLastInterpretStyle(null);
    setLuckTimeline(null);
    try {
      const paipan = await fetchPaipan(data);
      setResult(paipan);
      setLastRequest(data);
      saveBaziChartRef(paipan, data);
      deferIdle(() => {
        upsertFusionSource(
          buildBaziFusionSource({
            chart: paipan.chart as unknown as Record<string, unknown>,
            question: interpretQuestion.trim(),
            chartName: paipan.chart.input?.name || paipan.chart.dayMaster || "命盘",
            subtitle: paipan.chart.dayMaster,
          }),
        );
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "请求失败");
      setResult(null);
      setLastRequest(null);
      setInterpretation(null);
      setChatAgentId(null);
      setLuckTimeline(null);
    } finally {
      setPaipanLoading(false);
    }
  };

  const applyInterpretResult = (full: Awaited<ReturnType<typeof fetchInterpret>>, style: InterpretStyle) => {
    setInterpretation((prev) => {
      const mergedInterp = {
        ...full.interpretation,
        ...mergeInterpretSummary(prev, full.interpretation.summary, style),
      };
      appendTimelineEntry({
        moduleId: "01",
        moduleLabel: "八字命理",
        question: interpretQuestion.trim(),
        interpretation: mergedInterp,
      });
      if (result) {
        upsertFusionSource(
          buildBaziFusionSource({
            chart: result.chart as unknown as Record<string, unknown>,
            question: interpretQuestion.trim(),
            chartName: result.chart.input?.name || result.chart.dayMaster || "命盘",
            subtitle: result.chart.dayMaster,
            summaryPlain: mergedInterp.summaryPlain,
            summaryProfessional: mergedInterp.summaryProfessional,
            agentId: full.interpretation.agentId ?? chatAgentId,
          }),
        );
      }
      return mergedInterp;
    });
    if (full.interpretation.agentId) {
      setChatAgentId(full.interpretation.agentId);
    }
    setStreamingSummary("");
    setInterpretStage("");
  };

  const handleInterpret = async (style: InterpretStyle) => {
    if (!lastRequest) {
      return;
    }
    setInterpretStyleLoading(style);
    setLastInterpretStyle(style);
    setError("");
    setStreamingSummary("");
    setInterpretStage("");
    const options = {
      excerpts: interpretation?.excerpts,
      question: interpretQuestion.trim(),
      model: selectedModel,
      style,
    };
    try {
      let gotDelta = false;
      const full = await new Promise<Awaited<ReturnType<typeof fetchInterpret>>>((resolve, reject) => {
        fetchInterpretStream(lastRequest, options, {
          onStage: setInterpretStage,
          onDelta: (text) => {
            gotDelta = true;
            setStreamingSummary((prev) => prev + text);
          },
          onDone: resolve,
          onError: (msg, status) => {
            reject(Object.assign(new Error(msg), { status, gotDelta }));
          },
        });
      });
      applyInterpretResult(full, style);
    } catch (err) {
      const streamFailedEarly =
        err instanceof Error &&
        !(err as Error & { gotDelta?: boolean }).gotDelta;
      if (streamFailedEarly) {
        try {
          const full = await fetchInterpret(lastRequest, options);
          applyInterpretResult(full, style);
          return;
        } catch (fallbackErr) {
          setError(
            fallbackErr instanceof Error
              ? `AI 解读失败: ${fallbackErr.message}`
              : "AI 解读失败",
          );
          return;
        }
      }
      setError(
        err instanceof Error ? `AI 解读失败: ${err.message}` : "AI 解读失败",
      );
    } finally {
      setInterpretStyleLoading(null);
    }
  };

  const handleOpenLuck = async () => {
    if (luckTimeline) {
      return;
    }
    if (!lastRequest) {
      return;
    }
    setLuckLoading(true);
    setError("");
    try {
      const payload = await fetchLuckTimeline(lastRequest);
      setLuckTimeline(payload.luckTimeline);
    } catch (err) {
      setError(err instanceof Error ? err.message : "大运流年加载失败");
    } finally {
      setLuckLoading(false);
    }
  };

  const buildProfessionalCopyText = (): string => {
    if (!interpretation?.summaryProfessional) {
      return "";
    }
    if (
      interpretation.tripleFusion &&
      interpretation.summaryProfessional === interpretation.tripleFusion.merged.summary
    ) {
      const t = interpretation.tripleFusion;
      return [
        `综合结论\n${t.merged.summary}`,
        `八字 (${t.bazi.stance})\n${t.bazi.summary}`,
        `紫微 (${t.ziwei.stance})\n${t.ziwei.summary}`,
        `星命 (${t.xingming.stance})\n${t.xingming.summary}`,
      ].join("\n\n");
    }
    if (
      interpretation.fusion &&
      interpretation.summaryProfessional === interpretation.fusion.merged.summary
    ) {
      const fusion = interpretation.fusion;
      const liuyaoMeta = [
        fusion.liuyao.benGuaName ? `本卦 ${fusion.liuyao.benGuaName}` : "",
        fusion.liuyao.yongShen ? `用神 ${fusion.liuyao.yongShen.yongShen}` : "",
        `倾向: ${fusion.liuyao.stance}`,
      ]
        .filter(Boolean)
        .join(" ");
      return [
        `综合结论\n${fusion.merged.summary}`,
        `八字判断 (倾向: ${fusion.bazi.stance})\n${fusion.bazi.summary}`,
        `六爻判断 (${liuyaoMeta})\n${fusion.liuyao.summary}`,
      ].join("\n\n");
    }
    return interpretation.summaryProfessional;
  };

  return (
    <BaziVisualDemo
      error={error}
      paipanLoading={paipanLoading}
      luckLoading={luckLoading}
      result={result}
      lastRequest={lastRequest}
      luckTimeline={luckTimeline}
      interpretation={interpretation}
      chatEnabled={chatEnabled}
      chatModels={chatModels}
      selectedModel={selectedModel}
      onModelChange={setSelectedModel}
      interpretStyleLoading={interpretStyleLoading}
      interpretStage={interpretStage}
      streamingSummary={streamingSummary}
      interpretQuestion={interpretQuestion}
      onInterpretQuestionChange={setInterpretQuestion}
      ragStatus={ragStatus}
      onOpenAiChat={handleOpenAiChat}
      onSubmit={handleSubmit}
      onOpenLuck={handleOpenLuck}
      onInterpret={handleInterpret}
      onInterpretStyleLoading={setInterpretStyleLoading}
      buildProfessionalCopyText={buildProfessionalCopyText}
    />
  );
}
