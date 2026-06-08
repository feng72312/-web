import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { RagExcerptList } from "../components/RagExcerptList";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { ChatPanel } from "../components/ChatPanel";
import { CardDrawBoard } from "../components/tarot/CardDrawBoard";
import { DeckPicker } from "../components/tarot/DeckPicker";
import { ReadingBoard } from "../components/tarot/ReadingBoard";
import { SpreadPicker } from "../components/tarot/SpreadPicker";
import { fetchChatStatus } from "../services/chatApi";
import {
  drawTarot,
  fetchTarotInterpret,
  fetchTarotSpreads,
  initTarotChatSession,
  suggestTarotSpread,
} from "../services/tarotApi";
import { mergeInterpretSummary, type InterpretStyle } from "../utils/interpretStyle";
import type { ChatModelOption } from "../types/bazi";
import type {
  SpreadDef,
  TarotDeckId,
  TarotInterpretation,
  TarotReading,
} from "../types/tarot";
import "../styles/tarot.css";

export function TarotTab() {
  const { runWithAuth } = useAuth();
  const [question, setQuestion] = useState("");
  const [deck, setDeck] = useState<TarotDeckId>("rws");
  const [spreadId, setSpreadId] = useState("three-card");
  const [spreads, setSpreads] = useState<SpreadDef[]>([]);
  const [suggestReason, setSuggestReason] = useState("");
  const [suggestLoading, setSuggestLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);
  const [, setLastInterpretStyle] = useState<InterpretStyle | null>(null);
  const [error, setError] = useState("");
  const [reading, setReading] = useState<TarotReading | null>(null);
  const [interpretation, setInterpretation] = useState<TarotInterpretation | null>(null);
  const [chatAgentId, setChatAgentId] = useState<string | null>(null);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [chatModels, setChatModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [showChat, setShowChat] = useState(false);
  const [drawComplete, setDrawComplete] = useState(false);

  useEffect(() => {
    fetchTarotSpreads()
      .then((payload) => setSpreads(payload.spreads))
      .catch(() => setError("牌阵列表加载失败"));
    fetchChatStatus()
      .then((status) => {
        setChatEnabled(status.enabled);
        setChatModels(status.models ?? []);
        if (status.model) {
          setSelectedModel(status.model);
        }
      })
      .catch(() => setChatEnabled(false));
  }, []);

  const handleSuggestSpread = async () => {
    if (!question.trim()) {
      setError("请先输入问事内容");
      return;
    }
    setSuggestLoading(true);
    setError("");
    try {
      const result = await suggestTarotSpread(question.trim());
      setSpreadId(result.spreadId);
      setSuggestReason(result.reason);
    } catch (err) {
      setError(err instanceof Error ? err.message : "牌阵推荐失败");
    } finally {
      setSuggestLoading(false);
    }
  };

  const handleResetReading = () => {
    setReading(null);
    setInterpretation(null);
    setChatAgentId(null);
    setDrawComplete(false);
    setError("");
  };

  const handleDraw = async () => {
    if (!question.trim()) {
      setError("请先输入问事内容");
      return;
    }
    setLoading(true);
    setError("");
    setInterpretation(null);
    setChatAgentId(null);
    setDrawComplete(false);
    try {
      const payload = await drawTarot({
        question: question.trim(),
        deck,
        spread: spreadId,
        allowReversed: true,
      });
      setReading(payload.reading);
    } catch (err) {
      setError(err instanceof Error ? err.message : "抽牌失败");
      setReading(null);
    } finally {
      setLoading(false);
    }
  };

  const handleInterpret = async (style: InterpretStyle) => {
    if (!reading) return;
    setInterpretStyleLoading(style);
    setLastInterpretStyle(style);
    setError("");
    try {
      const full = await fetchTarotInterpret(
        reading,
        interpretation?.excerpts,
        selectedModel,
        style,
      );
      setInterpretation((prev) => ({
        ...full.interpretation,
        ...mergeInterpretSummary(prev, full.interpretation.summary, style),
      }));
      if (full.interpretation.agentId) {
        setChatAgentId(full.interpretation.agentId);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "解读失败");
    } finally {
      setInterpretStyleLoading(null);
    }
  };

  const handleOpenChat = () => {
    runWithAuth(async () => {
      if (!reading) {
        setError("请先完成抽牌");
        return;
      }
      try {
        const session = await initTarotChatSession(reading, interpretation?.excerpts);
        setChatAgentId(session.agentId);
        setShowChat(true);
      } catch (err) {
        setError(err instanceof Error ? err.message : "对话连接失败");
      }
    });
  };

  if (showChat && reading) {
    return (
      <div className="tarot-tab chat-mode">
        <ChatPanel
          layout="page"
          agentId={chatAgentId}
          chartName={reading.spreadName}
          dayMaster={reading.deckName}
          chatEnabled={chatEnabled}
          chatModels={chatModels}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
          sessionLoading={false}
          connectError=""
          onConnect={() => {}}
          onBack={() => setShowChat(false)}
        />
      </div>
    );
  }

  return (
    <div className="tarot-tab discipline-page">
      <section className="panel panel-cast">
        <div className="panel-head">
          <div>
            <h2>塔罗占卜</h2>
            <p className="hint">支持韦特 / 马赛 / 托特三套牌, 多种牌阵, AI 中文解读与追问.</p>
          </div>
        </div>
        <div className="cast-form">
          <section className="cast-form-section">
            <h3 className="cast-form-section-title">问事</h3>
            <label className="field field-grow">
              <span>问事内容</span>
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="例如: 这次换工作是否合适?"
                rows={3}
              />
            </label>
          </section>
          <section className="cast-form-section">
            <h3 className="cast-form-section-title">牌系</h3>
            <DeckPicker value={deck} onChange={setDeck} disabled={loading} />
          </section>
          <section className="cast-form-section">
            <SpreadPicker
              spreads={spreads}
              value={spreadId}
              onChange={setSpreadId}
              onSuggest={handleSuggestSpread}
              suggestLoading={suggestLoading}
              suggestReason={suggestReason}
              disabled={loading}
            />
          </section>
        </div>
        <CardDrawBoard
          reading={reading}
          deck={deck}
          loading={loading}
          onDraw={handleDraw}
          onReset={handleResetReading}
          onRevealComplete={setDrawComplete}
        />
      </section>

      {error && <div className="error-box">{error}</div>}

      {reading && drawComplete && (
        <>
          <section className="panel panel-chart">
            <div className="panel-head">
              <h2>牌阵结果</h2>
              {reading.meta?.drawNote && <p className="hint">{reading.meta.drawNote}</p>}
            </div>
            <ReadingBoard reading={reading} />
          </section>

          <section className="panel action-panel">
            <h2>典籍与 AI</h2>
            <InterpretModelPicker
              models={chatModels}
              value={selectedModel}
              onChange={setSelectedModel}
              chatEnabled={chatEnabled}
              disabled={interpretStyleLoading !== null}
            />
            <div className="action-row">
              <button type="button" className="secondary" disabled={!chatEnabled} onClick={handleOpenChat}>
                打开 AI 对话
              </button>
            </div>
            <InterpretStyleButtons
              professionalLoading={interpretStyleLoading === "professional"}
              plainLoading={interpretStyleLoading === "plain"}
              onProfessional={() => runWithAuth(() => handleInterpret("professional"))}
              onPlain={() => runWithAuth(() => handleInterpret("plain"))}
            />
          </section>

          {(interpretation?.summaryProfessional ||
            interpretation?.summaryPlain ||
            interpretation?.summary) && (
            <DualInterpretSummary title="塔罗解读" interpretation={interpretation}>
              {interpretation.query && (
                <details>
                  <summary>古籍索引</summary>
                  <p className="mono">{interpretation.query}</p>
                </details>
              )}
              <RagExcerptList excerpts={interpretation.excerpts ?? []} />
            </DualInterpretSummary>
          )}
        </>
      )}
    </div>
  );
}
