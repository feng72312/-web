import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight, BookOpenText, ChevronLeft, ChevronRight, Clock3,
  ExternalLink, RotateCcw, Search, ShieldCheck, Sparkles,
} from "lucide-react";
import type {
  PersonaAvailability, PersonaCategory, PersonaChatSession, PersonaDetail, PersonaSummary,
} from "../../types/persona";

interface PersonaHallProps {
  personas: PersonaSummary[];
  categories: PersonaCategory[];
  total: number;
  sourceCommit: string;
  selected: PersonaDetail | null;
  loadingDetail: boolean;
  busy: boolean;
  error: string;
  sessions: PersonaChatSession[];
  onSelect: (personaId: string) => void;
  onStart: (persona: PersonaDetail, prompt?: string) => void;
  onResume: (session: PersonaChatSession) => void;
}

const PAGE_SIZE = 24;

function modeLabel(persona: PersonaSummary): string {
  return persona.interactionMode === "historical_simulation" ? "历史思想模拟" : "公开思想框架";
}

export function PersonaHall({
  personas, categories, total, sourceCommit, selected, loadingDetail, busy, error,
  sessions, onSelect, onStart, onResume,
}: PersonaHallProps) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [availability, setAvailability] = useState<PersonaAvailability | "all">("all");
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase("zh-CN");
    return personas.filter((persona) => {
      if (category !== "all" && persona.categoryId !== category) return false;
      if (availability !== "all" && persona.availability !== availability) return false;
      const haystack = [persona.name, persona.formalName, persona.id, persona.categoryLabel,
        persona.upstream.name, ...persona.themes].join(" ").toLocaleLowerCase("zh-CN");
      return !needle || haystack.includes(needle);
    });
  }, [availability, category, personas, query]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const visible = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  useEffect(() => setPage(1), [availability, category, query]);
  useEffect(() => {
    if (page > pageCount) setPage(pageCount);
  }, [page, pageCount]);

  const resetFilters = () => {
    setQuery("");
    setCategory("all");
    setAvailability("all");
  };

  return (
    <div className="persona-hall">
      <section className="persona-hall-hero" aria-labelledby="persona-hall-title">
        <div className="persona-hall-heading">
          <p className="persona-kicker">Hall of Minds · 思想人物馆</p>
          <h2 id="persona-hall-title">百家思想，一席深谈</h2>
          <p>沿 18 个领域查找 165 位人物。历史人物采用明示的思想模拟；当代与生平状态不确定人物，只解析公开思想框架，不冒充本人。</p>
          <div className="persona-trust-row">
            <span><ShieldCheck size={16} /> 身份边界明示</span>
            <span><BookOpenText size={16} /> 上游与提交可查</span>
            <span><Sparkles size={16} /> 回到现实行动</span>
          </div>
        </div>
        <div className="persona-hall-seal" aria-hidden="true"><span>问</span><small>百家 · 今谈</small></div>
      </section>

      {error ? <p className="persona-error" role="alert">{error}</p> : null}

      <section className="persona-catalog" aria-labelledby="persona-catalog-title">
        <header className="persona-section-heading">
          <div><p className="persona-kicker">Curated Personas</p><h3 id="persona-catalog-title">人物索引</h3></div>
          <span>{total} 位人物 · {categories.length} 类 · 快照 {sourceCommit.slice(0, 7)}</span>
        </header>

        <div className="persona-catalog-tools">
          <label className="persona-search"><Search size={17} aria-hidden="true" /><span className="sr-only">搜索人物</span>
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索姓名、拼音仓库名或思想主题" />
          </label>
          <label className="persona-status-filter"><span>状态</span>
            <select value={availability} onChange={(event) => setAvailability(event.target.value as PersonaAvailability | "all")}>
              <option value="all">全部</option><option value="ready">可对话</option><option value="review_required">待审核</option><option value="unavailable">不可用</option>
            </select>
          </label>
        </div>

        <nav className="persona-category-nav" aria-label="人物分类">
          <button type="button" className={category === "all" ? "is-active" : ""} onClick={() => setCategory("all")}><span>全部</span><small>{personas.length}</small></button>
          {categories.map((item) => (
            <button type="button" key={item.id} className={category === item.id ? "is-active" : ""} onClick={() => setCategory(item.id)}>
              <span>{item.label}</span><small>{item.count}</small>
            </button>
          ))}
        </nav>

        <div className="persona-results-meta"><strong>{filtered.length}</strong> 位符合条件<span>第 {page} / {pageCount} 页</span></div>
        {visible.length ? (
          <div className="persona-catalog-grid">
            {visible.map((persona) => (
              <button key={persona.id} type="button" className={`persona-card${selected?.id === persona.id ? " is-selected" : ""}`} onClick={() => onSelect(persona.id)}>
                <span className="persona-card-seal" aria-hidden="true">{persona.sealCharacter}</span>
                <span className="persona-card-era">{persona.categoryLabel}</span>
                <strong>{persona.name}</strong>
                <span className={`persona-mode-tag ${persona.interactionMode}`}>{modeLabel(persona)}</span>
                <span className="persona-card-summary">{persona.summary}</span>
                <span className="persona-card-themes">{persona.themes.slice(0, 3).map((theme) => <i key={theme}>{theme}</i>)}</span>
                <span className="persona-card-link">查看人物志 <ArrowRight size={15} /></span>
              </button>
            ))}
          </div>
        ) : (
          <div className="persona-empty"><strong>没有找到对应人物</strong><span>试试姓名、仓库拼音或“长期主义”这类主题。</span><button type="button" onClick={resetFilters}><RotateCcw size={15} /> 重置筛选</button></div>
        )}

        {pageCount > 1 ? (
          <nav className="persona-pagination" aria-label="人物分页">
            <button type="button" disabled={page === 1} onClick={() => setPage((value) => value - 1)}><ChevronLeft size={16} /> 上一页</button>
            <span>{(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, filtered.length)} / {filtered.length}</span>
            <button type="button" disabled={page === pageCount} onClick={() => setPage((value) => value + 1)}>下一页 <ChevronRight size={16} /></button>
          </nav>
        ) : null}
      </section>

      {sessions.length > 0 ? (
        <section className="persona-hall-history" aria-labelledby="persona-hall-history-title">
          <header><Clock3 size={17} aria-hidden="true" /><div><p className="persona-kicker">Recent Dialogues</p><h3 id="persona-hall-history-title">续上前一席话</h3></div></header>
          <div>{sessions.slice(0, 4).map((session) => (
            <button type="button" key={session.agentId} onClick={() => onResume(session)}><span>{session.personaName}</span><strong>{session.title}</strong><small>{new Date(session.createdAt).toLocaleString("zh-CN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</small><ArrowRight size={15} aria-hidden="true" /></button>
          ))}</div>
        </section>
      ) : null}

      {loadingDetail ? <section className="persona-detail-skeleton" role="status">正在展卷，读取人物志…</section> : selected ? (
        <section className="persona-preview" aria-labelledby="persona-preview-title">
          <div className="persona-preview-profile">
            <p className="persona-kicker">Persona Dossier · {selected.categoryLabel}</p><h3 id="persona-preview-title">{selected.name}</h3>
            <div className={`persona-mode-tag ${selected.interactionMode}`}>{modeLabel(selected)}</div><p>{selected.summary}</p>
            <div className="persona-disclosure"><ShieldCheck size={18} aria-hidden="true" /><span>{selected.disclosure}</span></div>
            {selected.availability === "ready" ? (
              <button type="button" className="persona-primary-button" disabled={busy} onClick={() => onStart(selected)}>{busy ? "正在备席…" : `开始${selected.interactionMode === "historical_simulation" ? "思想对话" : "框架讨论"}`}<ArrowRight size={16} /></button>
            ) : <p className="persona-unavailable">暂不能创建对话：{selected.availabilityReason}</p>}
          </div>
          <div className="persona-preview-notes">
            <div><h4>适合讨论</h4><ul>{selected.suitableFor.map((item) => <li key={item}>{item}</li>)}</ul></div>
            <div><h4>思想主题</h4><div className="persona-theme-cloud">{selected.themes.map((theme) => <span key={theme}>{theme}</span>)}</div></div>
            <div><h4>从一个问题开始</h4><div className="persona-starter-list">{selected.starters.map((starter) => <button type="button" key={starter.label} disabled={busy || selected.availability !== "ready"} onClick={() => onStart(selected, starter.prompt)}><span>{starter.theme}</span>{starter.label}</button>)}</div></div>
            <div className="persona-audit-card"><strong>{selected.license.name} · {selected.availability === "ready" ? "已通过自动审计" : "待审核"}</strong><span>固定提交 {selected.upstream.commit.slice(0, 12) || "未取得"}</span><a href={selected.upstream.url} target="_blank" rel="noreferrer">{selected.upstream.name}<ExternalLink size={13} /></a></div>
          </div>
        </section>
      ) : null}
    </div>
  );
}
