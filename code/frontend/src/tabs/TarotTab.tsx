import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DualInterpretSummary } from "../components/DualInterpretSummary";
import { RagExcerptList } from "../components/RagExcerptList";
import { InterpretModelPicker } from "../components/InterpretModelPicker";
import { InterpretStyleButtons } from "../components/InterpretStyleButtons";
import { ChatPanel } from "../components/ChatPanel";
import { CardDrawBoard } from "../components/tarot/CardDrawBoard";
import { DeckPicker } from "../components/tarot/DeckPicker";
import { DrawModePicker } from "../components/tarot/DrawModePicker";
import { ManualPickBoard } from "../components/tarot/ManualPickBoard";
import { PickFanBoard } from "../components/tarot/PickFanBoard";
import { ReadingBoard } from "../components/tarot/ReadingBoard";
import { SpreadPicker } from "../components/tarot/SpreadPicker";
import { fetchChatStatus } from "../services/chatApi";
import {
  buildTarot,
  drawTarot,
  fetchTarotInterpret,
  fetchTarotDeckCards,
  fetchTarotSpreads,
  initTarotChatSession,
  revealTarot,
  shuffleTarot,
  suggestTarotSpread,
} from "../services/tarotApi";
import { mergeInterpretSummary, type InterpretStyle } from "../utils/interpretStyle";
import type { ChatModelOption } from "../types/bazi";
import type {
  ManualCardSelection,
  SpreadDef,
  TarotCardInfo,
  TarotDeckId,
  TarotDrawMode,
  TarotInterpretation,
  TarotReading,
  TarotShuffleResponse,
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
  const [drawMode, setDrawMode] = useState<TarotDrawMode>("pick");
  const [shuffle, setShuffle] = useState<TarotShuffleResponse | null>(null);
  const [manualCards, setManualCards] = useState<ManualCardSelection[]>([]);
  const [deckCards, setDeckCards] = useState<TarotCardInfo[]>([]);
  const [pickFlow, setPickFlow] = useState(false);

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

  useEffect(() => {
    if (drawMode !== "pick" || reading || !pickFlow) return;
    setLoading(true);
    setError("");
    shuffleTarot(deck, true)
      .then(setShuffle)
      .catch((err) => setError(err instanceof Error ? err.message : "洗牌失败"))
      .finally(() => setLoading(false));
  }, [deck, drawMode, pickFlow, reading]);

  useEffect(() => {
    if (drawMode !== "manual") return;
    setLoading(true);
    setError("");
    fetchTarotDeckCards(deck)
      .then((payload) => setDeckCards(payload.cards))
      .catch((err) => setError(err instanceof Error ? err.message : "牌库加载失败"))
      .finally(() => setLoading(false));
  }, [deck, drawMode]);

  useEffect(() => {
    document.body.classList.toggle("tarot-pick-immersive", pickFlow);
    return () => document.body.classList.remove("tarot-pick-immersive");
  }, [pickFlow]);

  const handleSuggestSpread = async () => {
    if (!question.trim()) {
      setError("请先输入问事内容");
      return;
    }
    setSuggestLoading(true);
    setError("");
    try {
      const result = await suggestTarotSpread(question.trim());
      handleSpreadChange(result.spreadId);
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

  const handleModeChange = (mode: TarotDrawMode) => {
    setDrawMode(mode);
    setPickFlow(false);
    setManualCards([]);
    setShuffle(null);
    handleResetReading();
  };

  const handleDeckChange = (nextDeck: TarotDeckId) => {
    setDeck(nextDeck);
    setPickFlow(false);
    setManualCards([]);
    setShuffle(null);
    handleResetReading();
  };

  const handleSpreadChange = (nextSpread: string) => {
    setSpreadId(nextSpread);
    setPickFlow(false);
    setManualCards([]);
    handleResetReading();
  };

  const handleStartPickFlow = () => {
    if (!question.trim()) {
      setError("请先输入问事内容");
      return;
    }
    if (!selectedSpread) {
      setError("请先选择牌阵");
      return;
    }
    setError("");
    setShuffle(null);
    setPickFlow(true);
  };

  const handleReshuffle = async () => {
    setLoading(true);
    setError("");
    setShuffle(null);
    try {
      const payload = await shuffleTarot(deck, true);
      setShuffle(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "洗牌失败");
    } finally {
      setLoading(false);
    }
  };

  const handlePickRedraw = async () => {
    handleResetReading();
    await handleReshuffle();
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

  const handleRevealPicks = async (picks: number[]) => {
    if (!question.trim()) {
      setError("请先输入问事内容");
      return;
    }
    if (!shuffle) {
      setError("请先完成洗牌");
      return;
    }
    setLoading(true);
    setError("");
    setInterpretation(null);
    setChatAgentId(null);
    setDrawComplete(false);
    try {
      const payload = await revealTarot({
        question: question.trim(),
        deck,
        spread: spreadId,
        allowReversed: true,
        sessionToken: shuffle.sessionToken,
        picks,
      });
      setReading(payload.reading);
      setPickFlow(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "揭牌失败");
      setReading(null);
    } finally {
      setLoading(false);
    }
  };

  const handleBuildManual = async () => {
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
      const payload = await buildTarot({
        question: question.trim(),
        deck,
        spread: spreadId,
        cards: manualCards,
      });
      setReading(payload.reading);
      setDrawComplete(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成牌阵失败");
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

  const selectedSpread = spreads.find((spread) => spread.id === spreadId);

  if (pickFlow && selectedSpread) {
    return (
      <div className="tarot-tab discipline-page tarot-pick-flow">
        <PickFanBoard
          deckSize={shuffle?.deckSize ?? 0}
          cardCount={selectedSpread.cardCount}
          deck={deck}
          spreadName={selectedSpread.nameZh}
          question={question.trim()}
          loading={loading || !shuffle}
          onBack={() => setPickFlow(false)}
          onReveal={handleRevealPicks}
          onReshuffle={handleReshuffle}
        />
        {error && <div className="error-box">{error}</div>}
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
            <h3 className="cast-form-section-title">抽牌方式</h3>
            <DrawModePicker value={drawMode} onChange={handleModeChange} disabled={loading} />
          </section>
          <section className="cast-form-section">
            <h3 className="cast-form-section-title">牌系</h3>
            <DeckPicker value={deck} onChange={handleDeckChange} disabled={loading} />
          </section>
          <section className="cast-form-section">
            <SpreadPicker
              spreads={spreads}
              value={spreadId}
              onChange={handleSpreadChange}
              onSuggest={handleSuggestSpread}
              suggestLoading={suggestLoading}
              suggestReason={suggestReason}
              disabled={loading}
            />
          </section>
        </div>
        {drawMode === "auto" && (
          <CardDrawBoard
            reading={reading}
            deck={deck}
            loading={loading}
            onDraw={handleDraw}
            onReset={handleResetReading}
            onRevealComplete={setDrawComplete}
          />
        )}
        {drawMode === "pick" && (
          reading ? (
            <CardDrawBoard
              reading={reading}
              deck={deck}
              loading={loading}
              onDraw={handlePickRedraw}
              onReset={handleResetReading}
              onRevealComplete={setDrawComplete}
            />
          ) : (
            <div className="form-actions form-actions-end tarot-pick-entry-actions">
              <button
                type="button"
                className="primary-btn"
                disabled={loading || !selectedSpread}
                onClick={handleStartPickFlow}
              >
                开始亲手抽牌
              </button>
            </div>
          )
        )}
        {drawMode === "manual" && !reading && selectedSpread && (
          <ManualPickBoard
            positions={selectedSpread.positions}
            deck={deck}
            deckCards={deckCards}
            value={manualCards}
            onChange={setManualCards}
            onSubmit={handleBuildManual}
            loading={loading}
          />
        )}
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
              onLoadingStart={setInterpretStyleLoading}
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
