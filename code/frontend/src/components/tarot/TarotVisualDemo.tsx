import { useEffect, useMemo, useState } from "react";
import { DualInterpretSummary } from "../DualInterpretSummary";
import { InterpretModelPicker } from "../InterpretModelPicker";
import { InterpretStyleButtons } from "../InterpretStyleButtons";
import { RagExcerptList } from "../RagExcerptList";
import { useAuth } from "../../context/AuthContext";
import { fetchChatStatus } from "../../services/chatApi";
import { openModuleAiChatSession } from "../ai/moduleChatBridge";
import { createModuleChatSessionRecord } from "../ai/moduleSession";
import type { AiChatSession } from "../ai/types";
import {
  fetchTarotInterpret,
  fetchTarotSpreads,
  initTarotChatSession,
  revealTarot,
  shuffleTarot,
} from "../../services/tarotApi";
import type { ChatModelOption } from "../../types/bazi";
import type {
  SpreadDef,
  TarotDeckId,
  TarotInterpretation,
  TarotReading,
  TarotShuffleResponse,
} from "../../types/tarot";
import { mergeInterpretSummary, type InterpretStyle } from "../../utils/interpretStyle";
import { MysticDeckGrid } from "./MysticDeckGrid";
import { MysticSelectedSlots } from "./MysticSelectedSlots";
import "../../styles/tarot-visual-demo.css";

interface TarotVisualDemoProps {
  onOpenAiChatSession: (session: AiChatSession) => void;
}

const DECK_OPTIONS: { id: TarotDeckId; label: string; hint: string }[] = [
  { id: "rws", label: "韦特塔罗", hint: "经典象征" },
  { id: "marseille", label: "马赛塔罗", hint: "古典体系" },
  { id: "thoth", label: "托特塔罗", hint: "神秘学派" },
];

const COMPLEXITY_LABEL: Record<string, string> = {
  beginner: "入门",
  intermediate: "进阶",
  advanced: "深度",
};

export function TarotVisualDemo({ onOpenAiChatSession }: TarotVisualDemoProps) {
  const { runWithAuth } = useAuth();
  const [question, setQuestion] = useState("");
  const [deck, setDeck] = useState<TarotDeckId>("rws");
  const [spreadId, setSpreadId] = useState("three-card");
  const [spreads, setSpreads] = useState<SpreadDef[]>([]);
  const [shuffle, setShuffle] = useState<TarotShuffleResponse | null>(null);
  const [picks, setPicks] = useState<number[]>([]);
  const [reading, setReading] = useState<TarotReading | null>(null);
  const [interpretation, setInterpretation] = useState<TarotInterpretation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [chatEnabled, setChatEnabled] = useState(false);
  const [models, setModels] = useState<ChatModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState("deepseek-chat");
  const [interpretStyleLoading, setInterpretStyleLoading] = useState<InterpretStyle | null>(null);

  useEffect(() => {
    document.body.classList.add("tarot-visual-immersive");
    return () => document.body.classList.remove("tarot-visual-immersive");
  }, []);

  useEffect(() => {
    fetchTarotSpreads()
      .then((payload) => setSpreads(payload.spreads))
      .catch(() => setError("牌阵列表加载失败"));
    fetchChatStatus()
      .then((status) => {
        setChatEnabled(status.enabled);
        setModels(status.models ?? []);
        if (status.model) {
          setSelectedModel(status.model);
        }
      })
      .catch(() => setChatEnabled(false));
  }, []);

  const selectedSpread = useMemo(
    () => spreads.find((spread) => spread.id === spreadId),
    [spreadId, spreads],
  );
  const selectedDeck = DECK_OPTIONS.find((item) => item.id === deck) ?? DECK_OPTIONS[0];

  const resetReading = () => {
    setPicks([]);
    setReading(null);
    setInterpretation(null);
    setShuffle(null);
    setError("");
  };

  const handleDeckChange = (nextDeck: TarotDeckId) => {
    setDeck(nextDeck);
    resetReading();
  };

  const handleSpreadChange = (nextSpread: string) => {
    setSpreadId(nextSpread);
    resetReading();
  };

  const handleShuffle = async () => {
    if (!question.trim()) {
      setError("请先输入问事内容");
      return;
    }
    setLoading(true);
    setError("");
    setPicks([]);
    setReading(null);
    setInterpretation(null);
    try {
      const result = await shuffleTarot(deck, true);
      setShuffle(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "洗牌失败");
    } finally {
      setLoading(false);
    }
  };

  const handlePick = (index: number) => {
    if (!selectedSpread || loading) return;
    setPicks((prev) => {
      if (prev.includes(index)) {
        return prev.filter((item) => item !== index);
      }
      if (prev.length >= selectedSpread.cardCount) {
        return prev;
      }
      return [...prev, index];
    });
  };

  const handleReveal = async () => {
    if (!selectedSpread || !shuffle) {
      setError("请先洗牌");
      return;
    }
    if (picks.length !== selectedSpread.cardCount) {
      setError(`请先选满 ${selectedSpread.cardCount} 张牌`);
      return;
    }
    setLoading(true);
    setError("");
    try {
      const result = await revealTarot({
        question: question.trim(),
        deck,
        spread: selectedSpread.id,
        allowReversed: true,
        sessionToken: shuffle.sessionToken,
        picks,
      });
      setReading(result.reading);
    } catch (err) {
      setError(err instanceof Error ? err.message : "揭牌失败");
    } finally {
      setLoading(false);
    }
  };

  const handleInterpret = async (style: InterpretStyle) => {
    if (!reading) return;
    setInterpretStyleLoading(style);
    setError("");
    try {
      const result = await fetchTarotInterpret(
        reading,
        interpretation?.excerpts,
        selectedModel,
        style,
      );
      setInterpretation((prev) => ({
        ...result.interpretation,
        ...mergeInterpretSummary(prev, result.interpretation.summary, style),
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "解读失败");
    } finally {
      setInterpretStyleLoading(null);
    }
  };

  const handleOpenChat = async () => {
    if (!reading) {
      setError("请先完成揭牌");
      return;
    }
    try {
      let agentId = interpretation?.agentId ?? null;
      if (!agentId) {
        const session = await initTarotChatSession(reading, interpretation?.excerpts);
        agentId = session.agentId;
      }
      await openModuleAiChatSession(
        createModuleChatSessionRecord({
          agentId,
          moduleId: "13",
          moduleLabel: "塔罗",
          question: reading.question || question.trim(),
          chartName: selectedSpread?.nameZh ?? reading.spread,
          subtitle: selectedDeck.label,
        }),
        interpretation,
        onOpenAiChatSession,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "对话连接失败");
    }
  };

  return (
    <div className="tarot-visual-demo">
      <header className="tarot-visual-topbar">
        <div>
          <p className="tarot-visual-kicker">Ziyun Tarot Lab</p>
          <h2>塔罗占卜</h2>
        </div>
        <div className="tarot-visual-topmeta">
          <span>{selectedSpread?.nameZh ?? "加载牌阵中"}</span>
          <span>{selectedDeck.label}</span>
        </div>
      </header>

      {error && <div className="tarot-visual-error">{error}</div>}

      <div className="tarot-visual-grid">
        <aside className="tarot-ritual-panel">
          <section className="tarot-vellum-card">
            <span className="tarot-card-eyebrow">Question</span>
            <label className="tarot-visual-field">
              <span>问事</span>
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="例如: 这次换工作是否合适?"
                rows={5}
              />
            </label>
          </section>

          <section className="tarot-vellum-card">
            <span className="tarot-card-eyebrow">Deck</span>
            <div className="tarot-visual-options">
              {DECK_OPTIONS.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={deck === item.id ? "tarot-choice active" : "tarot-choice"}
                  onClick={() => handleDeckChange(item.id)}
                >
                  <strong>{item.label}</strong>
                  <small>{item.hint}</small>
                </button>
              ))}
            </div>
          </section>

          <section className="tarot-vellum-card">
            <span className="tarot-card-eyebrow">Spread</span>
            <div className="tarot-spread-scroll">
              {spreads.map((spread) => (
                <button
                  key={spread.id}
                  type="button"
                  className={spreadId === spread.id ? "tarot-spread-token active" : "tarot-spread-token"}
                  onClick={() => handleSpreadChange(spread.id)}
                >
                  <strong>{spread.nameZh}</strong>
                  <span>
                    {spread.cardCount} 张 · {COMPLEXITY_LABEL[spread.complexity] ?? spread.complexity}
                  </span>
                </button>
              ))}
            </div>
          </section>
        </aside>

        <main className="tarot-altar">
          <div className="tarot-altar-head">
            <div>
              <p className="tarot-visual-kicker">Draw Table</p>
              <h3>{reading ? "牌阵已揭开" : "凝神, 从牌背中选择"}</h3>
            </div>
            <strong>
              已选 {picks.length} / {selectedSpread?.cardCount ?? 0}
            </strong>
          </div>

          <MysticDeckGrid
            deckSize={shuffle?.deckSize ?? 0}
            cardCount={selectedSpread?.cardCount ?? 0}
            picks={picks}
            loading={loading || Boolean(reading)}
            onPick={handlePick}
          />

          {selectedSpread && (
            <MysticSelectedSlots positions={selectedSpread.positions} picks={picks} />
          )}

          <div className="tarot-visual-actions">
            <button type="button" className="tarot-ghost-button" disabled={loading} onClick={handleShuffle}>
              {shuffle ? "重新洗牌" : "洗牌入局"}
            </button>
            <button
              type="button"
              className="tarot-gold-button"
              disabled={loading || !shuffle || !selectedSpread || picks.length !== selectedSpread.cardCount}
              onClick={handleReveal}
            >
              {loading ? "观牌中..." : "确认揭牌"}
            </button>
          </div>
        </main>

        <aside className="tarot-oracle-panel">
          <section className="tarot-oracle-card">
            <span className="tarot-card-eyebrow">Oracle Notes</span>
            <h3>本局线索</h3>
            <p>
              {selectedSpread
                ? `${selectedSpread.nameZh} 需要 ${selectedSpread.cardCount} 张牌。先洗牌, 再按直觉选择牌背。`
                : "正在加载牌阵。"}
            </p>
          </section>

          {reading ? (
            <section className="tarot-oracle-card">
              <span className="tarot-card-eyebrow">Revealed</span>
              <h3>揭牌摘要</h3>
              <div className="tarot-revealed-list">
                {reading.cards.map((card) => (
                  <div key={`${card.position}-${card.cardId}`} className="tarot-revealed-item">
                    <strong>{card.positionLabel}</strong>
                    <span>
                      {card.nameZh} · {card.orientation === "reversed" ? "逆位" : "正位"}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          ) : (
            <section className="tarot-oracle-card">
              <span className="tarot-card-eyebrow">Ritual</span>
              <h3>如何选择</h3>
              <p>不要预设答案。让问题停在心里, 从桌面牌背中选择第一眼有牵引感的位置。</p>
            </section>
          )}

          <section className="tarot-oracle-card tarot-ai-card">
            <span className="tarot-card-eyebrow">AI Reading</span>
            <InterpretModelPicker
              models={models}
              value={selectedModel}
              onChange={setSelectedModel}
              chatEnabled={chatEnabled}
              disabled={interpretStyleLoading !== null}
            />
            <InterpretStyleButtons
              professionalLoading={interpretStyleLoading === "professional"}
              plainLoading={interpretStyleLoading === "plain"}
              disabled={!reading || !chatEnabled}
              onLoadingStart={setInterpretStyleLoading}
              onProfessional={() => runWithAuth(() => handleInterpret("professional"))}
              onPlain={() => runWithAuth(() => handleInterpret("plain"))}
            />
            <button
              type="button"
              className="tarot-ghost-button"
              disabled={!reading || !chatEnabled}
              onClick={() => runWithAuth(() => handleOpenChat())}
            >
              打开 AI 对话
            </button>
          </section>
        </aside>
      </div>

      {reading && interpretation && (
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
    </div>
  );
}
