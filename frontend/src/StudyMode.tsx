import { useEffect, useState } from "react";
import { api, describeApiError } from "./api/client";
import type { LearningResourceRead, LearningResourceVersionRead, StudySessionRead, VersionProgressRead } from "./api/types";

type Mode = "learn" | "practice" | "review";
type Source = "summary" | "reviewer" | "flashcards" | "practice_quiz" | "mock_exam" | "qa_reviewer";
type Activity = {
  kind: "reading" | "card" | "question";
  title: string;
  body?: string;
  answer?: string;
  options?: string[];
  explanation?: string;
  concept: string;
  id: string;
};

const sourceLabels: Record<Source, string> = {
  summary: "Summary and key notes",
  reviewer: "Reviewer",
  flashcards: "Flashcards",
  practice_quiz: "Practice quiz",
  mock_exam: "Mock exam",
  qa_reviewer: "Q&A reviewer",
};

function activitiesFor(version: LearningResourceVersionRead, source: Source): Activity[] {
  const content = version.content as Record<string, any>;
  const topic = version.topics[0] || version.title;
  if (source === "summary") {
    const summary = content.summary?.content || version.summary;
    const notes = Array.isArray(content.key_notes) ? content.key_notes : [];
    return [
      ...(summary ? [{ kind: "reading" as const, title: version.title, body: summary, concept: topic, id: "summary" }] : []),
      ...notes.map((note: any, index: number) => ({ kind: "reading" as const, title: String(note.topic || `Key notes ${index + 1}`), body: Array.isArray(note.notes) ? note.notes.join("\n") : "", concept: String(note.topic || topic), id: `note-${index}` })),
    ].filter(item => item.body);
  }
  if (source === "reviewer") {
    const sections = content.reviewer?.sections;
    return Array.isArray(sections) ? sections.map((section: any, index: number) => ({ kind: "reading" as const, title: String(section.title || `Section ${index + 1}`), body: [section.content, ...(section.key_points || [])].filter(Boolean).join("\n"), concept: String(section.title || topic), id: `reviewer-${index}` })).filter(item => item.body) : [];
  }
  if (source === "flashcards") {
    return Array.isArray(content.flashcards) ? content.flashcards.map((card: any, index: number) => ({ kind: "card" as const, title: String(card.question || ""), answer: String(card.answer || ""), concept: String(card.topic || topic), id: `card-${index}` })).filter(item => item.title && item.answer) : [];
  }
  const questions = source === "mock_exam" ? content.exam?.questions : source === "qa_reviewer" ? content.qa_reviewer : content.quizzes || content.practice_quiz;
  return Array.isArray(questions) ? questions.map((question: any, index: number) => ({
    kind: "question" as const,
    title: String(question.question || ""),
    answer: String(question.correct_answer || question.answer || ""),
    options: Array.isArray(question.options) ? question.options.map(String) : undefined,
    explanation: String(question.explanation || ""),
    concept: String(question.topic || topic),
    id: String(question.id || question.question_id || `${source}-${index}`),
  })).filter(item => item.title && item.answer) : [];
}

function availableSources(version: LearningResourceVersionRead): Source[] {
  return (Object.keys(sourceLabels) as Source[]).filter(source => activitiesFor(version, source).length > 0);
}

export default function StudyMode({ onboardingId, onComplete, onExit }: {
  onboardingId: number | null;
  onComplete: (score: number, total: number, concepts: { name: string; correct: boolean }[]) => void;
  onExit: () => void;
}) {
  const [mode, setMode] = useState<Mode>("learn");
  const [resources, setResources] = useState<LearningResourceRead[]>([]);
  const [resourceId, setResourceId] = useState<number | null>(null);
  const [versions, setVersions] = useState<LearningResourceVersionRead[]>([]);
  const [versionId, setVersionId] = useState<number | null>(null);
  const [progress, setProgress] = useState<VersionProgressRead | null>(null);
  const [source, setSource] = useState<Source | null>(null);
  const [session, setSession] = useState<StudySessionRead | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [index, setIndex] = useState(0);
  const [response, setResponse] = useState("");
  const [revealed, setRevealed] = useState(false);
  const [correct, setCorrect] = useState(0);
  const [total, setTotal] = useState(0);
  const [concepts, setConcepts] = useState<{ name: string; correct: boolean }[]>([]);
  const [startedAt, setStartedAt] = useState(0);
  const [itemStartedAt, setItemStartedAt] = useState(0);
  const [savedAnswerIndex, setSavedAnswerIndex] = useState(-1);

  useEffect(() => {
    if (onboardingId == null) return;
    let active = true;
    setLoading(true);
    setError("");
    api.listLearningResources(onboardingId).then(items => {
      if (active) { setResources(items); setResourceId(items[0]?.id ?? null); }
    }).catch(err => { if (active) setError(describeApiError(err)); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [onboardingId]);

  useEffect(() => {
    if (resourceId == null) { setVersions([]); setVersionId(null); return; }
    let active = true;
    setLoading(true);
    setError("");
    setVersions([]);
    setVersionId(null);
    api.listVersions(resourceId).then(items => {
      if (active) { setVersions(items); setVersionId((items.find(item => item.is_current) || items[0])?.id ?? null); }
    }).catch(err => { if (active) setError(describeApiError(err)); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [resourceId]);

  useEffect(() => {
    if (onboardingId == null || resourceId == null || versionId == null) { setProgress(null); return; }
    let active = true;
    setProgress(null);
    api.getVersionProgress(resourceId, versionId, onboardingId)
      .then(value => { if (active) setProgress(value); })
      .catch(err => { if (active) setError(describeApiError(err)); });
    return () => { active = false; };
  }, [onboardingId, resourceId, versionId]);

  const version = versions.find(item => item.id === versionId && item.learning_resource_id === resourceId);
  const sources = version ? availableSources(version) : [];
  const preferred = mode === "practice" ? ["practice_quiz", "mock_exam", "flashcards"] : mode === "review" ? ["flashcards", "reviewer", "summary"] : ["summary", "reviewer", "flashcards"];
  const chosenSource = source && sources.includes(source) ? source : preferred.find(item => sources.includes(item as Source)) as Source | undefined || sources[0];
  const activities = version && chosenSource ? activitiesFor(version, chosenSource) : [];
  const activity = activities[index];

  const start = async () => {
    if (onboardingId == null || !version || !chosenSource) return;
    setBusy(true);
    setError("");
    try {
      const started = await api.startStudySession({ onboarding_id: onboardingId, resource_version_id: version.id, mode, source: chosenSource });
      setSession(started);
      setStartedAt(Date.now());
      setItemStartedAt(Date.now());
      setSavedAnswerIndex(-1);
      setIndex(0);
      setCorrect(0);
      setTotal(0);
      setConcepts([]);
    } catch (err) { setError(describeApiError(err)); }
    finally { setBusy(false); }
  };

  const advance = async (selfReported?: boolean) => {
    if (!session || !activity || busy) return;
    const assessed = activity.kind !== "reading";
    const isCorrect = activity.kind === "card" ? !!selfReported : response.trim().toLocaleLowerCase() === activity.answer?.trim().toLocaleLowerCase();
    setBusy(true);
    setError("");
    try {
      if (assessed && savedAnswerIndex !== index) {
        await api.submitStudyAnswer(session.id, {
          question_id: activity.id.slice(0, 120),
          concept_id: activity.concept.slice(0, 120),
          concept_name: activity.concept.slice(0, 160),
          student_answer: activity.kind === "card" ? (isCorrect ? "Recalled" : "Not recalled") : response,
          correct_answer: activity.answer || "",
          is_correct: isCorrect,
          time_taken_seconds: Math.max(0, Math.floor((Date.now() - itemStartedAt) / 1000)),
        });
        setSavedAnswerIndex(index);
      }
      const nextCorrect = correct + (assessed && isCorrect ? 1 : 0);
      const nextTotal = total + (assessed ? 1 : 0);
      const nextConcepts = assessed ? [...concepts, { name: activity.concept, correct: isCorrect }] : concepts;
      if (index + 1 === activities.length) {
        await api.completeStudySession(session.id, { score: nextCorrect, total_items: nextTotal, correct_items: nextCorrect, time_spent_seconds: Math.max(0, Math.floor((Date.now() - startedAt) / 1000)) });
        onComplete(nextCorrect, nextTotal, nextConcepts);
      } else {
        setCorrect(nextCorrect);
        setTotal(nextTotal);
        setConcepts(nextConcepts);
        setIndex(index + 1);
        setItemStartedAt(Date.now());
        setSavedAnswerIndex(-1);
        setResponse("");
        setRevealed(false);
      }
    } catch (err) { setError(describeApiError(err)); }
    finally { setBusy(false); }
  };

  if (onboardingId == null) return <section className="panel topic-panel"><h2>Finish account setup first</h2><p>Study Mode needs a saved learner profile to load resources and record progress.</p></section>;
  if (session && activity) return <div className="focus-shell">
    <header className="focus-header"><button className="brand" onClick={onExit}>Calibrat8</button><div className="focus-progress"><span><strong>{version?.title}</strong><small>Activity {index + 1} of {activities.length}</small></span><div><i style={{ width: `${(index + 1) / activities.length * 100}%` }}/></div></div><button className="btn btn-secondary" onClick={onExit}>Exit</button></header>
    <main className="focus-main"><div className="focus-kicker"><span>{sourceLabels[chosenSource!]}</span></div>
      {activity.kind === "reading" && <article className="learning-card"><h2>{activity.title}</h2><p className="study-reading">{activity.body}</p></article>}
      {activity.kind === "card" && <button className="flashcard" onClick={() => setRevealed(true)}><span className="eyebrow">{revealed ? "ANSWER" : "TAP TO REVEAL"}</span><strong>{revealed ? activity.answer : activity.title}</strong></button>}
      {activity.kind === "question" && <article className="learning-card quiz-card"><h2>{activity.title}</h2>{activity.options?.length ? activity.options.map(option => <button key={option} className={`answer-option ${response === option ? "selected" : ""}`} onClick={() => setResponse(option)} aria-pressed={response === option}>{option}</button>) : <label className="setup-field"><span>Your answer</span><input value={response} onChange={event => setResponse(event.target.value)} /></label>}</article>}
      {error && <p className="api-error" role="alert">{error}</p>}
      <div className="focus-footer"><p>{activity.kind === "card" ? "Reveal the answer, then rate your recall." : activity.kind === "reading" ? "Read at your own pace." : "Choose or write your answer."}</p><div className="study-actions">{activity.kind === "card" ? <><button className="btn btn-secondary" disabled={!revealed || busy} onClick={() => advance(false)}>Need practice</button><button className="btn btn-primary" disabled={!revealed || busy} onClick={() => advance(true)}>I recalled it</button></> : <button className="btn btn-primary" disabled={busy || (activity.kind === "question" && !response.trim())} onClick={() => advance()}>{busy ? "Saving…" : index + 1 === activities.length ? "Finish session" : "Next"}</button>}</div></div>
    </main>
  </div>;

  return <div className="page planner-page"><section className="planner-head"><div><span className="badge badge-peach">STUDY MODE</span><h2>Choose what to study</h2><p>Study one saved resource version at a time.</p></div></section>
    <section className="panel topic-panel section-block"><div className="section-heading"><div><p className="eyebrow">MODE</p><h3>How do you want to study?</h3></div></div><div className="learning-styles">{(["learn", "practice", "review"] as Mode[]).map(item => <button key={item} className={mode === item ? "selected" : ""} onClick={() => setMode(item)} aria-pressed={mode === item}><strong>{item[0].toUpperCase() + item.slice(1)}</strong></button>)}</div></section>
    <section className="panel topic-panel section-block"><div className="section-heading"><div><p className="eyebrow">LEARNING RESOURCES</p><h3>Load your material</h3></div></div>{loading && <p>Loading resources…</p>}{!loading && resources.length === 0 && <p>No saved learning resources yet. Import material and generate a resource to begin.</p>}
      {resources.length > 0 && <><label className="setup-field"><span>Resource</span><select value={resourceId ?? ""} onChange={event => { setResourceId(Number(event.target.value)); setSource(null); }}>{resources.map(item => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label><label className="setup-field"><span>Version (latest three)</span><select value={versionId ?? ""} onChange={event => { setVersionId(Number(event.target.value)); setSource(null); }}>{versions.map(item => <option key={item.id} value={item.id}>Version {item.version_number}{item.is_current ? " · Current" : ""}</option>)}</select></label></>}
      {version && <><p className="muted">{version.summary || version.title}</p>{progress && <p className="muted">{progress.attempts_count ? `Studied ${progress.attempts_count} time${progress.attempts_count === 1 ? "" : "s"} · ${progress.mastery_state.replace(/_/g, " ")} · latest accuracy ${Math.round(progress.latest_accuracy)}%` : "Not studied yet"}</p>}<div className="learning-styles">{sources.map(item => <button key={item} className={chosenSource === item ? "selected" : ""} onClick={() => setSource(item)} aria-pressed={chosenSource === item}><strong>{sourceLabels[item]}</strong><small>{activitiesFor(version, item).length} activities</small></button>)}</div>{sources.length === 0 && <p>This version has no study material to load.</p>}</>}
      {error && <p className="api-error" role="alert">{error}</p>}
      <div className="setup-actions"><button className="btn btn-primary" disabled={!chosenSource || !version || busy || loading} onClick={start}>{busy ? "Starting…" : "Start session"}</button></div>
    </section>
  </div>;
}
