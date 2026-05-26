import { useState } from "react";
import { AnalysisPanels } from "./components/AnalysisPanels";
import { BirthForm } from "./components/BirthForm";
import { FourPillars } from "./components/FourPillars";
import { LuckTimelineView } from "./components/LuckTimelineView";
import { PillarDetailView } from "./components/PillarDetailView";
import { fetchInterpret, fetchPaipan } from "./services/api";
import type { InterpretResponse, PaipanRequest, PaipanResponse } from "./types/bazi";
import "./styles/app.css";
import "./styles/chart-detail.css";

type ChartView = "summary" | "pillars" | "luck";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<PaipanResponse | null>(null);
  const [interpretation, setInterpretation] = useState<
    InterpretResponse["interpretation"] | null
  >(null);
  const [chartView, setChartView] = useState<ChartView>("summary");

  const handleSubmit = async (data: PaipanRequest) => {
    setLoading(true);
    setError("");
    setChartView("summary");
    try {
      const paipan = await fetchPaipan(data);
      setResult(paipan);
      const full = await fetchInterpret(data);
      setInterpretation(full.interpretation);
    } catch (err) {
      setError(err instanceof Error ? err.message : "请求失败");
      setResult(null);
      setInterpretation(null);
    } finally {
      setLoading(false);
    }
  };

  const chart = result?.chart;
  const pillarDetail = chart?.pillarDetail;
  const luckTimeline = chart?.luckTimeline;

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Bazi Platform MVP</p>
          <h1>八字排盘</h1>
          <p className="subtitle">模块化架构, 便于后续扩展典籍解读与更多分析模块</p>
        </div>
      </header>

      <main className="app-main">
        <BirthForm loading={loading} onSubmit={handleSubmit} />

        {error && <div className="error-box">{error}</div>}

        {result && chartView === "pillars" && pillarDetail && (
          <PillarDetailView detail={pillarDetail} onBack={() => setChartView("summary")} />
        )}

        {result && chartView === "luck" && luckTimeline && (
          <LuckTimelineView timeline={luckTimeline} onBack={() => setChartView("summary")} />
        )}

        {result && chartView === "summary" && (
          <div className="result-area">
            {chart?.input.name && (
              <p className="result-name">命主: {chart.input.name}</p>
            )}
            <section className="panel chart-panel">
              <h2>四柱排盘</h2>
              <FourPillars
                chart={chart}
                onOpenDetail={() => pillarDetail && setChartView("pillars")}
                onOpenLuck={() => luckTimeline && setChartView("luck")}
              />
            </section>

            <AnalysisPanels chart={chart} sections={result.sections} />

            {interpretation && (
              <section className="panel interpret-panel">
                <h2>命理解读</h2>
                <p className="interpret-summary">{interpretation.summary}</p>
                <details>
                  <summary>RAG 检索词</summary>
                  <p className="mono">{interpretation.query}</p>
                </details>
                {interpretation.excerpts.map((item, idx) => (
                  <blockquote key={idx} className="excerpt">
                    <cite>{item.source}</cite>
                    <p>{item.excerpt}</p>
                  </blockquote>
                ))}
              </section>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
