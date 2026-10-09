import { FormEvent, ReactNode, useEffect, useRef, useState } from "react";

type Page =
  | "home" | "tutor" | "planner" | "focus" | "lessons" | "ingest" | "generation"
  | "library" | "notes" | "flashcards" | "quiz" | "completion" | "knowledge"
  | "recommendations" | "report" | "settings" | "coach" | "progress";
type ProfileData = {
  name: string;
  level: string;
  subjects: string[];
  examDate: string;
  dailyMinutes: string;
  studyTime: string;
  learningStyle: string;
  personalization: boolean;
  deviceType: string;
  deviceMemory: string;
  modelPreference: string;
  learningTopic: string;
  learningSources: string[];
};
type IconName =
  | "home" | "spark" | "calendar" | "book" | "chart" | "settings" | "wifi"
  | "download" | "arrow" | "play" | "clock" | "check" | "mic" | "send"
  | "plus" | "pause" | "stop" | "search" | "file" | "cards" | "quiz"
  | "chevron" | "more" | "edit" | "offline" | "close" | "headphones"
  | "upload" | "layers" | "image" | "sun" | "moon";

const paths: Record<IconName, ReactNode> = {
  home: <><path d="m3 11 9-8 9 8"/><path d="M5 10v10h14V10M9 20v-6h6v6"/></>,
  spark: <><path d="m12 3-1.4 4.1A5.3 5.3 0 0 1 7.1 10L3 11.5l4.1 1.4a5.3 5.3 0 0 1 3.5 3.5L12 21l1.4-4.6a5.3 5.3 0 0 1 3.5-3.5l4.1-1.4-4.1-1.5a5.3 5.3 0 0 1-3.5-2.9Z"/></>,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M8 3v4m8-4v4M3 10h18m-13 4h3m2 0h3m-8 3h3"/></>,
  book: <><path d="M4 5.5A3.5 3.5 0 0 1 7.5 2H11v17H7.5A3.5 3.5 0 0 0 4 22Z"/><path d="M20 5.5A3.5 3.5 0 0 0 16.5 2H13v17h3.5A3.5 3.5 0 0 1 20 22Z"/></>,
  chart: <><path d="M4 20V10m6 10V4m6 16v-7m5 7H2"/></>,
  settings: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3V2.8h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z"/></>,
  wifi: <><path d="M5 12.6a10 10 0 0 1 14 0M2 9.2a15 15 0 0 1 20 0M8.5 16a5 5 0 0 1 7 0"/><circle cx="12" cy="19" r="1"/></>,
  offline: <><path d="M5 12.6a10 10 0 0 1 10.7-2M8.5 16a5 5 0 0 1 7 0M2 9.2a15 15 0 0 1 9.5-3.1M3 3l18 18"/><circle cx="12" cy="19" r="1"/></>,
  download: <><path d="M12 3v12m-5-5 5 5 5-5M4 20h16"/></>,
  arrow: <><path d="M5 12h14m-5-5 5 5-5 5"/></>,
  play: <path d="m9 6 9 6-9 6Z"/>,
  pause: <><path d="M9 5v14m6-14v14"/></>,
  stop: <rect x="6" y="6" width="12" height="12" rx="2"/>,
  clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
  check: <path d="m5 12 4 4L19 6"/>,
  mic: <><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0m-7 7v3m-4 0h8"/></>,
  send: <><path d="m3 4 18 8-18 8 3-8Z"/><path d="M6 12h15"/></>,
  plus: <path d="M12 5v14m-7-7h14"/>,
  search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
  file: <><path d="M6 2h8l4 4v16H6Z"/><path d="M14 2v5h5M9 12h6m-6 4h6"/></>,
  cards: <><rect x="4" y="6" width="14" height="14" rx="2"/><path d="m7 6 1-3h12v14l-2 .7"/></>,
  quiz: <><circle cx="12" cy="12" r="9"/><path d="M9.8 9a2.3 2.3 0 1 1 3.4 2c-.8.4-1.2.9-1.2 2m0 3h.01"/></>,
  chevron: <path d="m9 6 6 6-6 6"/>,
  more: <><circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/></>,
  edit: <><path d="m4 20 4.5-1 10-10-3.5-3.5-10 10Z"/><path d="m13.5 7 3.5 3.5"/></>,
  close: <path d="M6 6l12 12M18 6 6 18"/>,
  headphones: <><path d="M4 14v-2a8 8 0 0 1 16 0v2"/><path d="M4 14h3v6H5a1 1 0 0 1-1-1Zm16 0h-3v6h2a1 1 0 0 0 1-1Z"/></>,
  upload: <><path d="M12 16V4m-5 5 5-5 5 5"/><path d="M4 15v5h16v-5"/></>,
  layers: <><path d="m12 2 9 5-9 5-9-5Z"/><path d="m3 12 9 5 9-5M3 17l9 5 9-5"/></>,
  image: <><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-5-5L5 20"/></>,
  sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41"/></>,
  moon: <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>,
};

function Icon({ name, size = 20 }: { name: IconName; size?: number }) {
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

export type ExpressionState =
  | "happy" | "curious" | "thinking" | "supportive"
  | "focused" | "excited" | "listening" | "concerned";

export type ExpressionState =
  | "happy" | "curious" | "thinking" | "supportive"
  | "focused" | "excited" | "listening" | "concerned";

export function Calibrat8Mascot({
  expression = "happy",
  size = "medium",
  className = ""
}: {
  expression?: ExpressionState;
  size?: "small" | "medium" | "large" | "hero";
  className?: string;
}) {
  const sizePx = { small: 42, medium: 84, large: 140, hero: 220 }[size];
  return (
    <div className={`calibrat8-mascot calibrat8-${size} ${className}`} style={{ width: sizePx, height: sizePx, display: "inline-grid", placeItems: "center" }}>
      <img
        src="/calibrat8-character.png"
        alt={`Calibrat8 companion character (${expression})`}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
          filter: "drop-shadow(0 10px 20px rgba(56, 189, 248, 0.25))"
        }}
      />
    </div>
  );
}

function Lumi({ size = "medium", expression = "happy" }: { size?: "small" | "medium" | "large" | "hero"; expression?: ExpressionState }) {
  return <Calibrat8Mascot size={size} expression={expression} />;
}

function Button({ children, onClick, variant = "primary", icon, type = "button", disabled = false, className = "" }: {
  children: ReactNode; onClick?: () => void; variant?: "primary" | "secondary" | "ghost" | "soft";
  icon?: IconName; type?: "button" | "submit"; disabled?: boolean; className?: string;
}) {
  return <button type={type} disabled={disabled} onClick={onClick} className={`btn btn-${variant} ${className}`}>{icon && <Icon name={icon} size={18}/>}<span>{children}</span></button>;
}

function Badge({ children, tone = "sage" }: { children: ReactNode; tone?: "sage" | "peach" | "blue" | "neutral" }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

const nav = [
  { id: "home" as Page, label: "Home", icon: "home" as IconName },
  { id: "library" as Page, label: "Resources", icon: "book" as IconName },
  { id: "planner" as Page, label: "Study", icon: "calendar" as IconName },
  { id: "knowledge" as Page, label: "Knowledge Map", icon: "layers" as IconName },
  { id: "report" as Page, label: "Reports", icon: "chart" as IconName },
];

function isNavActive(item: Page, page: Page) {
  if (item === page) return true;
  if (item === "library") return ["ingest", "generation", "notes", "flashcards", "quiz", "completion", "recommendations", "lessons"].includes(page);
  if (item === "planner") return page === "focus";
  return item === "knowledge" && page === "coach";
}

function Sidebar({ page, setPage, online, setOnline, profile, editProfile, theme, toggleTheme }: { page: Page; setPage: (p: Page) => void; online: boolean; setOnline: (v: boolean) => void; profile: ProfileData; editProfile: () => void }) {
  return <aside className="sidebar">
    <button className="brand" onClick={() => setPage("home")} aria-label="Calibrat8 home">
      <span className="brand-mark"><Icon name="spark" size={18}/></span>
      <span>Calibrat8</span>
    </button>
    <nav className="nav-list" aria-label="Primary navigation">
      {nav.map(item => <button key={item.id} className={`nav-item ${isNavActive(item.id, page) ? "active" : ""}`} onClick={() => setPage(item.id)}>
        <Icon name={item.icon}/><span>{item.id === "knowledge" ? "Knowledge Analysis" : item.label}</span>
      </button>)}
    </nav>
    <div className="sidebar-bottom">
      <button className="nav-item" onClick={toggleTheme}><Icon name={theme === "dark" ? "sun" : "moon"}/><span>{theme === "dark" ? "Light theme" : "Dark theme"}</span></button>
      <button className={`connection ${online ? "" : "is-offline"}`} onClick={() => setOnline(!online)}>
        <span className="status-dot"/><span><strong>{online ? "Online" : "Offline"}</strong><small>{online ? "AI tutor available" : "Saved materials ready"}</small></span>
      </button>
      <button className="nav-item" onClick={() => setPage("settings")}><Icon name="settings"/><span>Settings & offline</span></button>
      <button className="nav-item compact-preferences" onClick={editProfile}><Icon name="edit"/><span>Edit learning profile</span></button>
      <div className="profile"><div className="avatar">{profile.name.split(" ").map(part => part[0]).join("").slice(0, 2).toUpperCase()}</div><span><strong>{profile.name}</strong><small>{profile.level}</small></span><Icon name="more"/></div>
    </div>
  </aside>;
}

function MobileNav({ page, setPage }: { page: Page; setPage: (p: Page) => void }) {
  return <nav className="mobile-nav" aria-label="Mobile navigation">{nav.map(item =>
    <button key={item.id} className={isNavActive(item.id, page) ? "active" : ""} onClick={() => setPage(item.id)}><Icon name={item.icon}/><span>{item.id === "planner" ? "Study Mode" : item.label.replace("Study ", "")}</span></button>
  )}</nav>;
}

function Topbar({ title, online, setOnline, theme, toggleTheme }: { title: string; online: boolean; setOnline: (v: boolean) => void; theme: "dark" | "light"; toggleTheme: () => void }) {
  return <header className="topbar">
    <div><p className="eyebrow">COSMIC LEARNING COMPANION · LEARN, SCORE, CALIBRATE</p><h1>{title}</h1></div>
    <div className="topbar-actions">
      <button className="theme-toggle-btn" onClick={toggleTheme} aria-label={`Switch to ${theme === "dark" ? "light (neumorphic)" : "dark (cosmic glass)"} theme`}>
        <Icon name={theme === "dark" ? "sun" : "moon"} size={18}/>
      </button>
      <button className={`top-status ${online ? "" : "is-offline"}`} onClick={() => setOnline(!online)}><Icon name={online ? "wifi" : "offline"} size={17}/>{online ? "Online" : "Offline"}</button>
    </div>
  </header>;
}

function ProgressRing({ value, label }: { value: number; label: string }) {
  return <div className="progress-ring" style={{ "--progress": `${value * 3.6}deg` } as React.CSSProperties}><div><strong>{value}%</strong><small>{label}</small></div></div>;
}

function Home({ go, online, openOffline, profile }: { go: (p: Page) => void; online: boolean; openOffline: () => void; profile: ProfileData }) {
  const firstName = profile.name.trim().split(" ")[0] || "Learner";
  const focusSubject = profile.subjects[0] || "Mathematics";
  return <div className="page home-page">
    <section className="hero">
      <div className="hero-copy">
        <Badge tone="peach">WELCOME BACK</Badge>
        <h2>Ready to learn, {firstName}?</h2>
        <p>Start with {focusSubject.toLowerCase()}, create new resources, or review your learning report.</p>
        <div className="hero-actions"><Button onClick={() => go("planner")} icon="play">Begin learning</Button><span>Choose your study mode</span></div>
      </div>
      <div className="hero-visual" aria-hidden="true">
        <div className="orbit orbit-one"/><div className="orbit orbit-two"/>
        <Lumi size="large"/>
        <div className="float-card"><Icon name="spark" size={16}/><span><strong>Calibrat8 is ready.</strong> One step at a time.</span></div>
      </div>
    </section>

    <section className="section-block">
      <div className="section-heading"><div><p className="eyebrow">START HERE</p><h3>Choose your next step</h3></div></div>
      <div className="quick-grid">
        <button className="quick-card coral" onClick={() => go("ingest")}><span className="quick-icon"><Icon name="plus"/></span><span><strong>Create Learning Resources</strong><small>Turn text, voice, photos, or files into a learning set.</small></span><Icon name="arrow"/></button>
        <button className="quick-card sage" onClick={() => go("planner")}><span className="quick-icon"><Icon name="play"/></span><span><strong>Study Mode</strong><small>Choose Learn, Practice, or Review and begin a focused session.</small></span><Icon name="arrow"/></button>
        <button className="quick-card blue" onClick={() => go("report")}><span className="quick-icon"><Icon name="chart"/></span><span><strong>Report Learning</strong><small>See weekly progress, strengths, and topics that need more practice.</small></span><Icon name="arrow"/></button>
      </div>
    </section>

    <div className="section-block">
      <section className="panel today-panel">
        <div className="section-heading"><div><p className="eyebrow">SUGGESTED NEXT</p><h3>Your study plan</h3></div><button className="text-button" onClick={() => go("planner")}>Open Study Mode <Icon name="chevron" size={15}/></button></div>
        <div className="timeline">
          <div className="timeline-item"><span className="timeline-dot">1</span><div><strong>Review cell structure</strong><small>12 flashcards · suggested</small></div><span>20 min</span></div>
          <div className="timeline-item current"><span className="timeline-dot">2</span><div><strong>Quadratic equations</strong><small>Worked examples · up next</small><div className="mini-progress"><span/></div></div><span>25 min</span></div>
          <div className="timeline-item"><span className="timeline-dot">3</span><div><strong>French Revolution</strong><small>Summary + quick quiz</small></div><span>30 min</span></div>
        </div>
      </section>
    </div>

    <section className="section-block">
      <div className="section-heading"><div><p className="eyebrow">SAVED FOR YOU</p><h3>Pick up where you left off</h3></div><button className="text-button" onClick={() => go("lessons")}>View all <Icon name="arrow" size={15}/></button></div>
      <div className="resource-row">
        <button className="resource-card" onClick={() => go("notes")}><span className="subject-art biology"><Icon name="book" size={30}/></span><span><Badge>Biology</Badge><strong>Cell division & mitosis</strong><small><Icon name="clock" size={14}/> Key notes · demo source</small></span></button>
        <button className="resource-card" onClick={() => go("flashcards")}><span className="subject-art maths"><Icon name="cards" size={30}/></span><span><Badge tone="peach">Biology</Badge><strong>Mitosis recall cards</strong><small><Icon name="cards" size={14}/> 3 flashcards · offline</small></span></button>
        <button className="resource-card" onClick={() => go("quiz")}><span className="subject-art history"><Icon name="quiz" size={30}/></span><span><Badge tone="blue">Biology</Badge><strong>Cell division reviewer</strong><small><Icon name="quiz" size={14}/> Practice quiz · 3 questions</small></span></button>
      </div>
    </section>
  </div>;
}

function Tutor({ online }: { online: boolean }) {
  const [messages, setMessages] = useState([
    { role: "user", text: "Why does the sign change when I move a number to the other side of an equation?" },
    { role: "tutor", text: "Think of an equation like a balanced scale. You’re not really “moving” the number—you’re doing the opposite operation to both sides so the scale stays balanced.", detail: "For example: x + 3 = 8. Subtract 3 from both sides: x + 3 − 3 = 8 − 3, so x = 5." },
  ]);
  const [input, setInput] = useState("");
  const [detail, setDetail] = useState(false);
  const send = (text = input) => {
    if (!text.trim()) return;
    setMessages(m => [...m, { role: "user", text }, { role: "tutor", text: online ? "Let’s take it one small step at a time. I’ll use the balance idea and show you what changes on each side." : "Live AI help needs an internet connection. Your saved explanation and practice cards are still available offline.", detail: online ? "Start by identifying the operation attached to the number. Then apply its inverse to both sides." : undefined }]);
    setInput("");
  };
  return <div className="tutor-layout">
    <section className="chat-area">
      <div className="chat-intro"><Lumi size="medium"/><div><Badge tone={online ? "sage" : "neutral"}>{online ? "CALIBRAT8 · AI TUTOR ONLINE" : "CALIBRAT8 · LIVE HELP UNAVAILABLE"}</Badge><h2>Let’s figure this out together.</h2><p>Ask Calibrat8 a question, or choose a quick way to continue.</p></div></div>
      <div className="messages">
        {messages.map((m, i) => <div key={i} className={`message-row ${m.role}`}>
          {m.role === "tutor" && <Lumi size="small"/>}
          <div className="message-bubble"><p>{m.text}</p>{m.detail && <div className="worked-example"><strong>Worked example</strong><p>{m.detail}</p></div>}
            {m.role === "tutor" && i === 1 && <><button className="disclosure" onClick={() => setDetail(!detail)}>{detail ? "Hide" : "Show"} why this works <Icon name="chevron" size={14}/></button>{detail && <p className="detail-copy">Adding and subtracting the same amount preserves equality. Both sides change equally, so the relationship stays true.</p>}</>}
          </div>
        </div>)}
      </div>
      <div className="suggestion-row">{["Explain it simply", "Show me another example", "Test my understanding"].map(x => <button key={x} onClick={() => send(x)}>{x}</button>)}</div>
      <form className="composer" onSubmit={(e: FormEvent) => { e.preventDefault(); send(); }}>
        <button type="button" className="composer-icon" aria-label="Add learning material"><Icon name="plus"/></button>
        <input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask a follow-up question…" aria-label="Tutor question"/>
        <button type="button" className="composer-icon" aria-label="Use voice input" title={online ? "Voice input prototype" : "Voice unavailable offline"}><Icon name="mic"/></button>
        <button type="submit" className="send-button" aria-label="Send question"><Icon name="send"/></button>
      </form>
      <p className="prototype-note">Demo tutor responses are pre-written for this prototype; no live AI model is connected.</p>
    </section>
    <aside className="context-panel">
      <p className="eyebrow">CURRENT CONTEXT</p><h3>Quadratic equations</h3>
      <div className="context-meta"><span><Icon name="book" size={16}/> Mathematics</span><span><Icon name="clock" size={16}/> Studying 14 min</span></div>
      <hr/>
      <p className="eyebrow">SAVE THIS EXPLANATION AS</p>
      <button className="context-action"><Icon name="cards"/><span><strong>Flashcards</strong><small>3 suggested cards</small></span><Icon name="plus"/></button>
      <button className="context-action"><Icon name="quiz"/><span><strong>Quick practice</strong><small>4 understanding checks</small></span><Icon name="plus"/></button>
      <div className="support-note"><Icon name="download"/><p><strong>Available offline</strong><br/>Saved cards and quizzes work without a connection.</p></div>
    </aside>
  </div>;
}

const initialTopics = ["Quadratic equations", "Cell division", "French Revolution", "Organic chemistry", "Essay structure"];
const schedule = [
  { topic: "Quadratic equations", activity: "Examples + practice", time: 30, tone: "coral" },
  { topic: "Cell division", activity: "Summary + flashcards", time: 25, tone: "sage" },
  { topic: "Break", activity: "Step away and reset", time: 10, tone: "neutral" },
  { topic: "Organic chemistry", activity: "Key concepts + quiz", time: 25, tone: "blue" },
  { topic: "French Revolution", activity: "Timeline review", time: 20, tone: "peach" },
  { topic: "Essay structure", activity: "Recall + outline", time: 10, tone: "sage" },
];

function Planner({ start }: { start: () => void }) {
  const [studyMode, setStudyMode] = useState<"Learn" | "Practice" | "Review">("Learn");
  const [plannerStep, setPlannerStep] = useState(0);
  const [selectedMaterials, setSelectedMaterials] = useState(["Notes Summary / Key Notes"]);
  const modeDetails = [
    { name: "Learn" as const, icon: "book" as IconName, copy: "Build understanding with key notes, explanations, and guided examples." },
    { name: "Practice" as const, icon: "quiz" as IconName, copy: "Answer targeted questions and get immediate feedback on each concept." },
    { name: "Review" as const, icon: "cards" as IconName, copy: "Refresh earlier material with summaries, recall cards, and quick checks." },
  ];
  const materialOptions = [
    { name: "Notes Summary / Key Notes", icon: "book" as IconName, copy: "Load concise summaries, definitions, and important takeaways.", time: 10, tone: "sage" },
    { name: "Flashcards", icon: "cards" as IconName, copy: "Load question-and-answer cards for active recall.", time: 10, tone: "coral" },
    { name: "Quizzes / Exam / Reviewer", icon: "quiz" as IconName, copy: "Load practice questions, reviewer items, and answer checks.", time: 15, tone: "blue" },
  ];
  const loadedMaterials = materialOptions.filter(material => selectedMaterials.includes(material.name));
  const totalMinutes = loadedMaterials.reduce((total, material) => total + material.time, 0);
  const toggleMaterial = (material: string) => setSelectedMaterials(current => current.includes(material) ? current.filter(item => item !== material) : [...current, material]);
  const stepTitles = ["Choose your study mode", "Choose learning materials", "Review your session"];
  return <div className="page planner-page">
    <section className="planner-head"><div><Badge tone="peach">STUDY MODE</Badge><h2>{stepTitles[plannerStep]}</h2><p>Complete one simple step at a time.</p></div>{plannerStep === 2 && <div className="duration-card"><Icon name="clock"/><span><small>ESTIMATED TIME</small><strong>{totalMinutes} min</strong></span></div>}</section>
    <section className="panel topic-panel">
      <div className="section-heading"><div><p className="eyebrow">STEP {plannerStep + 1} OF 3</p><h3>{stepTitles[plannerStep]}</h3></div><Badge tone="neutral">{Math.round((plannerStep + 1) / 3 * 100)}%</Badge></div>
      <div className="onboarding-progress" aria-label={`Study setup step ${plannerStep + 1} of 3`}><span style={{ width: `${(plannerStep + 1) / 3 * 100}%` }}/></div>
    </section>

    {plannerStep === 0 && <section className="panel topic-panel section-block">
      <div className="section-heading"><div><p className="eyebrow">CHOOSE ONE</p><h3>How do you want to study?</h3></div><Badge tone="neutral">{studyMode}</Badge></div>
      <div className="learning-styles">{modeDetails.map(mode => <button key={mode.name} className={studyMode === mode.name ? "selected" : ""} onClick={() => setStudyMode(mode.name)} aria-pressed={studyMode === mode.name}><span><Icon name={mode.icon}/></span><div><strong>{mode.name}</strong><p>{mode.copy}</p></div><i>{studyMode === mode.name && <Icon name="check" size={15}/>}</i></button>)}</div>
      <div className="setup-actions"><Button onClick={() => setPlannerStep(1)} icon="arrow">Choose topics</Button></div>
    </section>}

    {plannerStep === 1 && <section className="panel topic-panel section-block">
      <div className="section-heading"><div><p className="eyebrow">LOAD FOR STUDY</p><h3>Which materials do you want?</h3></div><Badge tone="neutral">{selectedMaterials.length} selected</Badge></div>
      <p className="muted">Choose one or more saved resources to use in this session.</p>
      <div className="learning-styles">{materialOptions.map(material => <button key={material.name} className={selectedMaterials.includes(material.name) ? "selected" : ""} onClick={() => toggleMaterial(material.name)} aria-pressed={selectedMaterials.includes(material.name)}><span><Icon name={material.icon}/></span><div><strong>{material.name}</strong><p>{material.copy}</p></div><i>{selectedMaterials.includes(material.name) && <Icon name="check" size={15}/>}</i></button>)}</div>
      <div className="setup-actions"><Button variant="secondary" onClick={() => setPlannerStep(0)}>Back</Button><Button disabled={selectedMaterials.length === 0} onClick={() => setPlannerStep(2)} icon="arrow">Review plan</Button></div>
    </section>}

    {plannerStep === 2 && <section className="panel schedule-panel section-block">
      <div className="section-heading"><div><p className="eyebrow">{studyMode.toUpperCase()} SESSION</p><h3>Materials ready to load</h3></div><span className="time-total"><Icon name="clock" size={16}/> {totalMinutes} min</span></div>
      <div className="schedule-list">{loadedMaterials.map((material, index) => <div className="schedule-item" key={material.name}><span className={`schedule-index ${material.tone}`}><Icon name={material.icon} size={15}/></span><span><strong>{material.name}</strong><small>{material.copy}</small></span><div className="schedule-time"><strong>{material.time}</strong><small>min</small></div><Icon name="check" size={17}/></div>)}</div>
      <div className="planner-reason"><Icon name="spark"/><p><strong>{studyMode} mode selected.</strong> Study Mode will load only the {selectedMaterials.length === 1 ? "resource" : "resources"} you selected.</p></div>
      <div className="setup-actions"><Button variant="secondary" onClick={() => setPlannerStep(1)}>Back</Button><Button onClick={start} icon="play">Start {studyMode.toLowerCase()} session</Button></div>
    </section>}
  </div>;
}

function Focus({ exit, completeSession }: { exit: () => void; completeSession: (score: number, total: number) => void }) {
  const [step, setStep] = useState(0);
  const [paused, setPaused] = useState(false);
  const [flipped, setFlipped] = useState(false);
  const [answer, setAnswer] = useState<number | null>(null);
  return <div className="focus-shell">
    <header className="focus-header"><button className="brand" onClick={exit}><span className="brand-mark"><Icon name="spark" size={18}/></span><span>Calibrat8</span></button><div className="focus-progress"><span><strong>Quadratic equations</strong><small>Activity {step + 1} of 3 · {25 - step * 8} min remaining</small></span><div><i style={{ width: `${(step + 1) * 33}%` }}/></div></div><Button onClick={() => setPaused(!paused)} variant="secondary" icon={paused ? "play" : "pause"}>{paused ? "Resume" : "Pause"}</Button></header>
    <main className="focus-main">
      {paused ? <div className="pause-state"><div className="complete-mark"><Icon name="pause"/></div><h2>Session paused.</h2><p>Take the time you need. Your place is saved on this device.</p><Button onClick={() => setPaused(false)} icon="play">Resume when ready</Button></div> :
      <><div className="focus-kicker"><span>ACTIVITY {step + 1}</span><Badge tone="blue">{step === 0 ? "CONCEPT" : step === 1 ? "FLASHCARD" : "QUICK CHECK"}</Badge></div>
      {step === 0 && <article className="learning-card"><p className="eyebrow">THE KEY IDEA</p><h2>Undo each operation in reverse order.</h2><p>To isolate <b>x</b>, treat the equation like a wrapped gift. Remove the outermost “layer” first, and do the same thing to both sides.</p><div className="equation"><span>2x + 6 = 18</span><Icon name="arrow"/><span>2x = 12</span><Icon name="arrow"/><span>x = 6</span></div><div className="callout"><Icon name="spark"/><p><strong>Notice the order:</strong> subtract 6 first, then divide by 2. This reverses the original operations.</p></div></article>}
      {step === 1 && <button className={`flashcard ${flipped ? "flipped" : ""}`} onClick={() => setFlipped(!flipped)}><span className="eyebrow">{flipped ? "ANSWER" : "TAP TO REVEAL"}</span><strong>{flipped ? "Apply the inverse operation to both sides." : "How do you keep an equation balanced?"}</strong><small>{flipped ? "Whatever you do to one side, do to the other." : "Think about the balance-scale analogy."}</small></button>}
      {step === 2 && <article className="learning-card quiz-card"><p className="eyebrow">TRY THIS</p><h2>What is the first step to solve 3x − 4 = 11?</h2>{["Divide both sides by 3", "Add 4 to both sides", "Subtract 11 from both sides"].map((x, i) => <button key={x} className={`answer-option ${answer === i ? "selected" : ""}`} onClick={() => setAnswer(i)} aria-pressed={answer === i}><span>{String.fromCharCode(65 + i)}</span>{x}</button>)}</article>}
      <div className="focus-footer"><p>{step === 0 ? "Read at your own pace." : step === 1 ? "Retrieval practice strengthens memory." : "Choose the best first step."}</p><Button disabled={step === 2 && answer === null} onClick={() => step === 2 ? completeSession(answer === 1 ? 1 : 0, 1) : setStep(step + 1)} icon="arrow">{step === 2 ? "Finish session" : "Next"}</Button></div></>}
    </main>
  </div>;
}

type IngestedFile = { name: string; size: string; type: string };
type Attempt = {
  score: number;
  total: number;
  completedAt: string;
  source: "quiz" | "study";
  concepts: { name: string; correct: boolean }[];
};

function ContentIngestion({ online, done }: { online: boolean; done: (next?: "library" | "generation") => void }) {
  const [topic, setTopic] = useState("");
  const [notes, setNotes] = useState("");
  const [files, setFiles] = useState<IngestedFile[]>([]);
  const [inputMethod, setInputMethod] = useState<"text" | "voice" | "camera" | "files">("text");
  const [stage, setStage] = useState<"add" | "ready">("add");
  const hasContent = topic.trim().length >= 2 && (notes.trim().length >= 20 || files.length > 0);
  const wordCount = notes.trim() ? notes.trim().split(/\s+/).length : 0;
  const chunkCount = Math.max(1, Math.ceil(wordCount / 350) + files.length);
  const addFiles = (list: FileList | null) => {
    if (!list) return;
    setFiles(current => [...current, ...Array.from(list).map(file => ({
      name: file.name,
      size: file.size > 1048576 ? `${(file.size / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(file.size / 1024))} KB`,
      type: file.name.split(".").pop()?.toUpperCase() || "FILE",
    }))].slice(0, 6));
  };

  if (stage === "ready") return <div className="page ingestion-page">
    <button className="back-link" onClick={() => done("library")}>← Learning Resources</button>
    <section className="ingest-success panel">
      <div className="complete-mark"><Icon name="check" size={30}/></div>
      <Badge>CONTENT READY</Badge>
      <h2>Your topic is ready.</h2>
      <p>Your captured material is linked to “{topic}” and ready for the next prototype step. Audio, images, and documents were not parsed, and no AI resources were generated.</p>
      <div className="ingest-results">
        <span><strong>1</strong><small>Topic added</small></span>
        <span><strong>{files.length + (notes.trim() ? 1 : 0)}</strong><small>Sources added</small></span>
        <span><strong>{chunkCount}</strong><small>Planned sections</small></span>
      </div>
      <div className="pipeline-summary">
        <div><span><Icon name="check" size={15}/></span><p><strong>Material captured</strong><small>{files.length} file{files.length === 1 ? "" : "s"} · {wordCount} written words</small></p></div>
        <i/>
        <div><span><Icon name="check" size={15}/></span><p><strong>Topic linked</strong><small>{topic}</small></p></div>
        <i/>
        <div><span><Icon name={online ? "wifi" : "offline"} size={15}/></span><p><strong>Generation is optional</strong><small>{online ? "A connected model would be needed next" : "Wait for a connection or configured local AI"}</small></p></div>
      </div>
      <div className="success-actions"><Button onClick={() => done("generation")} icon="spark">Choose learning resources</Button><Button variant="secondary" onClick={() => done("library")} icon="book">Save without generating</Button><Button variant="ghost" onClick={() => { setStage("add"); setTopic(""); setNotes(""); setFiles([]); }} icon="plus">Add another</Button></div>
    </section>
  </div>;

  return <div className="page ingestion-page">
    <button className="back-link" onClick={() => done("library")}>← Learning Resources</button>
    <section className="ingest-head">
      <div><Badge tone="blue">NEW LEARNING SET</Badge><h2>What would you like to learn?</h2><p>Name the topic, then add free text, record your voice, use your camera, or upload a file.</p></div>
      <div className="ingest-steps" aria-label="Ingestion progress">
        {["Topic & material", "Ready"].map((label, index) => <span className={index === 0 ? "active" : ""} key={label}><i>{index + 1}</i>{label}</span>)}
      </div>
    </section>

    <div className="ingestion-grid">
      <section className="panel ingest-source">
        <label className="setup-field"><span>Topic</span><input value={topic} onChange={e => setTopic(e.target.value)} placeholder="For example: Cell division, budgeting, or Spanish basics"/></label>
        <div className="source-tabs" role="tablist" aria-label="Choose how to add learning material">
          <button role="tab" aria-selected={inputMethod === "text"} className={inputMethod === "text" ? "active" : ""} onClick={() => setInputMethod("text")}><Icon name="edit"/> Text</button>
          <button role="tab" aria-selected={inputMethod === "voice"} className={inputMethod === "voice" ? "active" : ""} onClick={() => setInputMethod("voice")}><Icon name="mic"/> Voice</button>
          <button role="tab" aria-selected={inputMethod === "camera"} className={inputMethod === "camera" ? "active" : ""} onClick={() => setInputMethod("camera")}><Icon name="image"/> Camera</button>
          <button role="tab" aria-selected={inputMethod === "files"} className={inputMethod === "files" ? "active" : ""} onClick={() => setInputMethod("files")}><Icon name="upload"/> Files</button>
        </div>
        {inputMethod === "text" && <div className="notes-input"><label htmlFor="material-notes">Free text</label><textarea id="material-notes" value={notes} onChange={e => setNotes(e.target.value)} placeholder={"Paste notes, write an explanation, or add the information you want to study…\n\nTip: include enough detail for useful notes, flashcards, and questions."}/><span>{wordCount} words</span></div>}
        {inputMethod === "voice" && <label className="drop-zone compact-drop-zone">
          <input type="file" accept="audio/*" capture="user" onChange={e => { addFiles(e.target.files); e.currentTarget.value = ""; }}/>
          <span className="drop-icon"><Icon name="mic" size={24}/></span>
          <strong>Record a voice command</strong>
          <p>Tell Calibrat8 what you want to learn or explain what you already know.</p>
          <small>Uses your device’s recorder when supported · microphone permission may be requested</small>
        </label>}
        {inputMethod === "camera" && <label className="drop-zone compact-drop-zone">
          <input type="file" accept="image/*" capture="environment" onChange={e => { addFiles(e.target.files); e.currentTarget.value = ""; }}/>
          <span className="drop-icon"><Icon name="image" size={24}/></span>
          <strong>Open your camera</strong>
          <p>Take a photo of a page, diagram, object, or whiteboard.</p>
          <small>Uses your device’s camera when supported · camera permission may be requested</small>
        </label>}
        {inputMethod === "files" && <label className="drop-zone compact-drop-zone">
          <input type="file" multiple accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md,image/*,audio/*" onChange={e => { addFiles(e.target.files); e.currentTarget.value = ""; }}/>
          <span className="drop-icon"><Icon name="upload" size={24}/></span>
          <strong>Browse files</strong>
          <p>PDF, DOCX, PPTX, TXT, Markdown, images, or audio</p>
          <small>Up to 6 files · selected files can be removed before continuing</small>
        </label>}
        {files.length > 0 && <div className="file-queue">{files.map((file, index) => <div key={`${file.name}-${index}`}><span className="file-type">{file.type.slice(0, 4)}</span><p><strong>{file.name}</strong><small>{file.size} · Ready to add</small></p><button onClick={() => setFiles(files.filter((_, fileIndex) => fileIndex !== index))} aria-label={`Remove ${file.name}`}><Icon name="close" size={17}/></button></div>)}</div>}
        <div className="format-note"><Icon name="file"/><p><strong>Prototype capture</strong><br/>Text is kept in this session. Audio, photos, and files can be selected and reviewed, but are not transcribed, analyzed, or uploaded to an AI service.</p></div>
      </section>
      <aside className="panel ingest-help"><div className="icon-tile"><Icon name="spark"/></div><p className="eyebrow">CHOOSE YOUR WAY</p><h3>Show or tell Calibrat8.</h3><div className="help-step"><span>1</span><p><strong>Name the topic</strong><small>Use any subject, skill, or idea you want to learn.</small></p></div><div className="help-step"><span>2</span><p><strong>Add learning material</strong><small>Type, speak, take a photo with your camera, or choose a saved file.</small></p></div><div className="availability"><Icon name={online ? "wifi" : "offline"}/><p><strong>{online ? "Online" : "Working offline"}</strong><br/>{online ? "Selected material can enter the prototype workflow." : "You can capture material now. New AI processing is unavailable."}</p></div></aside>
      <div className="ingest-footer"><p>{hasContent ? "Your topic and learning material are ready." : "Add a topic, then type, record, capture, or upload learning material."}</p><Button disabled={!hasContent} onClick={() => setStage("ready")} icon="check">Prepare material</Button></div>
    </div>
  </div>;
}

function Generation({ online, finish, back }: { online: boolean; finish: () => void; back: () => void }) {
  const [selected, setSelected] = useState(["notes", "cards", "quiz"]);
  const [prepared, setPrepared] = useState(false);
  const resources = [
    { id: "notes", icon: "book" as IconName, title: "Key notes", copy: "Important concepts, definitions, and takeaways" },
    { id: "cards", icon: "cards" as IconName, title: "Flashcards", copy: "Short question-and-answer recall cards" },
    { id: "quiz", icon: "quiz" as IconName, title: "Quiz & reviewer", copy: "Practice questions with explanations" },
  ];
  const toggle = (id: string) => setSelected(current => current.includes(id) ? current.filter(item => item !== id) : [...current, id]);
  return <div className="page workflow-page">
    <button className="back-link" onClick={back}>← Back to imported material</button>
    <section className="workflow-hero">
      <div><Badge tone="peach">PROTOTYPE GENERATION</Badge><h2>What should Calibrat8 prepare?</h2><p>Select the resources you want. This prototype uses clearly labeled sample content; no local or cloud AI model is connected.</p></div>
      <Lumi size="medium"/>
    </section>
    <div className="generation-layout">
      <section className="panel generation-card">
        <div className="section-heading"><div><p className="eyebrow">LEARNING RESOURCES</p><h3>Choose one or more</h3></div><Badge tone="neutral">{selected.length} selected</Badge></div>
        <div className="resource-select-list">{resources.map(resource => <button key={resource.id} className={selected.includes(resource.id) ? "selected" : ""} onClick={() => toggle(resource.id)} aria-pressed={selected.includes(resource.id)}>
          <span><Icon name={resource.icon}/></span><span><strong>{resource.title}</strong><small>{resource.copy}</small></span><i>{selected.includes(resource.id) && <Icon name="check" size={15}/>}</i>
        </button>)}</div>
        {!online && <div className="status-callout warning"><Icon name="offline"/><p><strong>New generation is unavailable offline.</strong><br/>Reconnect or configure a genuine local model. Saved resources remain available.</p></div>}
        {prepared && <div className="generation-progress" aria-live="polite">{resources.filter(item => selected.includes(item.id)).map(item => <div key={item.id}><span><Icon name="check" size={15}/></span><p><strong>{item.title}</strong><small>Sample resource prepared from the Cell division demo source</small></p><Badge>Ready</Badge></div>)}</div>}
        <div className="generation-actions">
          {!prepared ? <Button disabled={!online || selected.length === 0} onClick={() => setPrepared(true)} icon="spark">Prepare sample resources</Button> : <Button onClick={finish} icon="arrow">Open learning set</Button>}
        </div>
      </section>
      <aside className="panel source-proof"><p className="eyebrow">SOURCE BOUNDARY</p><h3>Grounded in your material</h3><p>The demo resources are tied to the built-in Cell division lesson and are labeled as samples. Uploaded files are not parsed in this prototype.</p><div><Icon name="file"/><span><strong>Biology lesson notes</strong><small>Cell division & mitosis · demo source</small></span></div><div><Icon name="offline"/><span><strong>Offline after saving</strong><small>Prepared samples stay available in this browser session</small></span></div></aside>
    </div>
  </div>;
}

function ResourceLibrary({ go, create }: { go: (page: Page) => void; create: () => void }) {
  const [filter, setFilter] = useState<"all" | "notes" | "cards" | "quiz">("all");
  const actions = [
    { id: "notes", label: "Key notes", icon: "book" as IconName, page: "notes" as Page, meta: "4 sections" },
    { id: "cards", label: "Flashcards", icon: "cards" as IconName, page: "flashcards" as Page, meta: "6 cards" },
    { id: "quiz", label: "Quiz & reviewer", icon: "quiz" as IconName, page: "quiz" as Page, meta: "3 questions" },
  ];
  return <div className="page library-page">
    <section className="workflow-hero"><div><Badge tone="blue">LEARNING RESOURCES</Badge><h2>Everything you need, in one learning set.</h2><p>Open saved material, continue studying, or create a new set from your own notes and files.</p></div><Button onClick={create} icon="plus">Create learning set</Button></section>
    <div className="library-tabs" role="tablist" aria-label="Filter learning resources">{[["all", "All resources"], ["notes", "Notes"], ["cards", "Flashcards"], ["quiz", "Quizzes"]].map(([id, label]) => <button role="tab" aria-selected={filter === id} className={filter === id ? "active" : ""} onClick={() => setFilter(id as typeof filter)} key={id}>{label}</button>)}</div>
    <section className="panel learning-set">
      <div className="learning-set-head"><div className="set-art"><Icon name="book" size={28}/></div><div><span><Badge>Biology</Badge><Badge tone="neutral">Available offline</Badge></span><h3>Cell division & mitosis</h3><p>Source: Biology lesson notes · Updated today · Version 1</p></div><Button onClick={() => go("focus")} icon="play">Start studying</Button></div>
      <div className="set-progress"><span><strong>Learning progress</strong><small>No completed quiz yet</small></span><div><i/></div><button onClick={() => go("knowledge")}>View knowledge map <Icon name="arrow" size={15}/></button></div>
      <div className="resource-action-grid">{actions.filter(item => filter === "all" || filter === item.id).map(item => <button key={item.id} onClick={() => go(item.page)}><span><Icon name={item.icon}/></span><span><strong>{item.label}</strong><small>{item.meta} · demo source</small></span><Icon name="chevron"/></button>)}</div>
      <div className="version-row"><span><Icon name="layers"/><strong>Version 1</strong><small>Original sample set · no adaptive updates yet</small></span><button onClick={() => go("recommendations")}>Check recommendations</button></div>
    </section>
    <section className="library-empty panel"><div><Icon name="plus"/></div><span><strong>Create another learning set</strong><small>Import notes, PDFs, text files, or paste text manually.</small></span><Button variant="secondary" onClick={create} icon="upload">Add material</Button></section>
  </div>;
}

function NotesViewer({ back, start }: { back: () => void; start: () => void }) {
  return <div className="page viewer-page"><button className="back-link" onClick={back}>← Learning Resources</button>
    <div className="viewer-layout"><article className="panel note-document"><div className="document-head"><div><Badge>DEMO KEY NOTES · VERSION 1</Badge><h2>Cell division & mitosis</h2><p>Referenced source: Biology lesson notes</p></div><Badge tone="neutral">Available offline</Badge></div>
      <div className="key-takeaway"><Icon name="spark"/><p><strong>Key takeaway</strong><br/>Cell division supports growth, repair, and reproduction. Mitosis produces two genetically identical daughter cells.</p></div>
      <h3>Before division</h3><p>During interphase, a cell grows, performs its normal functions, and copies its DNA so each new cell can receive a complete set.</p>
      <h3>The four phases of mitosis</h3><ol><li><strong>Prophase:</strong> Chromosomes condense and become visible.</li><li><strong>Metaphase:</strong> Chromosomes line up at the cell equator.</li><li><strong>Anaphase:</strong> Sister chromatids move to opposite poles.</li><li><strong>Telophase:</strong> New nuclei form around each chromosome set.</li></ol>
      <h3>Cytokinesis</h3><p>The cytoplasm divides, completing the formation of two daughter cells.</p>
    </article><aside className="stack"><section className="panel viewer-side"><p className="eyebrow">CONTINUE LEARNING</p><h3>Ready to recall this?</h3><p>Use the same source material in a focused study session.</p><Button onClick={start} icon="play" className="full-button">Start study mode</Button></section><section className="panel source-proof compact"><p className="eyebrow">SOURCE</p><div><Icon name="file"/><span><strong>Biology lesson notes</strong><small>Built-in demo content</small></span></div></section></aside></div>
  </div>;
}

const demoCards = [
  ["What happens during interphase?", "The cell grows and copies its DNA before division."],
  ["Where do chromosomes line up during metaphase?", "At the cell’s equator."],
  ["What does mitosis produce?", "Two genetically identical daughter cells."],
];

function FlashcardsViewer({ back, takeQuiz }: { back: () => void; takeQuiz: () => void }) {
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [ratings, setRatings] = useState<Record<number, "understood" | "practice">>({});
  const move = (next: number) => { setIndex(next); setFlipped(false); };
  return <div className="page cards-page"><button className="back-link" onClick={back}>← Learning Resources</button><div className="cards-header"><div><Badge tone="blue">DEMO FLASHCARDS</Badge><h2>Cell division & mitosis</h2><p>Card {index + 1} of {demoCards.length} · saved offline</p></div><div className="card-count">{Object.keys(ratings).length}/{demoCards.length}<small>reviewed</small></div></div>
    <button className={`study-flashcard ${flipped ? "flipped" : ""}`} onClick={() => setFlipped(!flipped)} aria-label={flipped ? "Showing answer. Activate to show question." : "Showing question. Activate to reveal answer."}><span className="eyebrow">{flipped ? "ANSWER" : "QUESTION"}</span><strong>{demoCards[index][flipped ? 1 : 0]}</strong><small>{flipped ? "Tap to see the question" : "Tap to reveal the answer"}</small></button>
    <div className="rating-row"><button className={ratings[index] === "practice" ? "selected" : ""} onClick={() => setRatings({ ...ratings, [index]: "practice" })}>Needs more practice</button><button className={ratings[index] === "understood" ? "selected" : ""} onClick={() => setRatings({ ...ratings, [index]: "understood" })}>I understand this</button></div>
    <div className="deck-nav"><Button variant="secondary" disabled={index === 0} onClick={() => move(index - 1)}>Previous</Button>{index < demoCards.length - 1 ? <Button onClick={() => move(index + 1)} icon="arrow">Next card</Button> : <Button onClick={takeQuiz} icon="quiz">Take the quiz</Button>}</div>
  </div>;
}

const quizQuestions = [
  { question: "What is the main result of mitosis?", options: ["Four different cells", "Two genetically identical cells", "One larger cell"], answer: 1, concept: "Purpose of mitosis", explanation: "Mitosis produces two daughter cells with the same genetic information." },
  { question: "During which phase do chromosomes line up at the cell equator?", options: ["Prophase", "Metaphase", "Telophase"], answer: 1, concept: "Mitosis phases", explanation: "Meta means middle: chromosomes align across the middle during metaphase." },
  { question: "What happens before mitosis during interphase?", options: ["DNA is copied", "The cytoplasm splits", "Chromatids move apart"], answer: 0, concept: "Interphase", explanation: "The cell grows and duplicates its DNA during interphase." },
];

function QuizViewer({ back, submit }: { back: () => void; submit: (attempt: Attempt) => void }) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const current = quizQuestions[index];
  const selected = answers[index];
  const finish = () => {
    const concepts = quizQuestions.map((question, questionIndex) => ({ name: question.concept, correct: answers[questionIndex] === question.answer }));
    submit({ score: concepts.filter(item => item.correct).length, total: quizQuestions.length, completedAt: new Date().toISOString(), source: "quiz", concepts });
  };
  return <div className="page quiz-page"><button className="back-link" onClick={back}>← Learning Resources</button><section className="quiz-shell panel"><div className="quiz-progress"><span><strong>Cell division quiz</strong><small>Question {index + 1} of {quizQuestions.length}</small></span><div><i style={{ width: `${((index + 1) / quizQuestions.length) * 100}%` }}/></div></div><Badge tone="peach">DEMO QUIZ · SAVES LOCALLY</Badge><h2>{current.question}</h2><div className="quiz-options">{current.options.map((option, optionIndex) => <button className={selected === optionIndex ? "selected" : ""} aria-pressed={selected === optionIndex} onClick={() => setAnswers({ ...answers, [index]: optionIndex })} key={option}><span>{String.fromCharCode(65 + optionIndex)}</span>{option}</button>)}</div>
      {selected !== undefined && <div className={`answer-feedback ${selected === current.answer ? "correct" : "incorrect"}`} aria-live="polite"><Icon name={selected === current.answer ? "check" : "spark"}/><p><strong>{selected === current.answer ? "That’s right." : "No worries—this is useful evidence."}</strong><br/>{current.explanation}</p></div>}
      <div className="quiz-footer"><Button variant="secondary" disabled={index === 0} onClick={() => setIndex(index - 1)}>Previous</Button>{index < quizQuestions.length - 1 ? <Button disabled={selected === undefined} onClick={() => setIndex(index + 1)} icon="arrow">Next question</Button> : <Button disabled={selected === undefined} onClick={finish} icon="check">Submit quiz</Button>}</div></section>
  </div>;
}

function SessionCompletion({ attempt, go }: { attempt: Attempt; go: (page: Page) => void }) {
  const percentage = Math.round((attempt.score / attempt.total) * 100);
  return <div className="page completion-page"><section className="completion-card panel"><div className="completion-lumi"><Lumi size="medium"/></div><Badge>SESSION COMPLETED</Badge><h2>{percentage === 100 ? "Wonderful focus—you understood every check." : "Nice progress. Every answer gives us a clearer next step."}</h2><p>Calibrat8 saved this result locally and used only your submitted answers to update the knowledge map.</p><div className="summary-stats"><span><strong>{attempt.score}/{attempt.total}</strong><small>Correct answers</small></span><span><strong>{attempt.concepts.filter(item => !item.correct).length}</strong><small>Topics to revisit</small></span><span><strong>Saved</strong><small>On this device</small></span></div><div className="recalc-state"><span><Icon name="check"/></span><p><strong>Knowledge map updated</strong><small>Recommendations now reflect this session’s evidence.</small></p></div><div className="completion-actions"><Button onClick={() => go("knowledge")} icon="layers">View knowledge map</Button><Button variant="secondary" onClick={() => go("recommendations")} icon="spark">See next steps</Button></div></section></div>;
}

function KnowledgeMap({ attempt, recommendations }: { attempt: Attempt | null; recommendations: () => void }) {
  const topics = Array.from(new Set([...(attempt?.concepts.map(item => item.name) || []), "Purpose of mitosis", "Mitosis phases", "Interphase", "Cytokinesis"]));
  return <div className="page knowledge-page"><section className="workflow-hero"><div><Badge tone="blue">KNOWLEDGE MAP</Badge><h2>See what the evidence supports.</h2><p>Topic states come from completed answers—not guesses about your ability.</p></div>{attempt && <Button onClick={recommendations} icon="spark">Knowledge Analysis</Button>}</section>
    {!attempt ? <section className="empty-evidence panel"><div><Icon name="layers" size={28}/></div><h3>No assessed topics yet</h3><p>Complete a quiz or focused study session to begin your knowledge map. Calibrat8 won’t invent mastery scores without evidence.</p></section> :
    <div className="knowledge-layout"><section className="panel map-card"><div className="map-legend"><span><i className="strong"/>Strong understanding</span><span><i className="developing"/>Developing</span><span><i className="practice"/>Needs practice</span><span><i className="unassessed"/>Not assessed</span></div><div className="topic-map">{topics.map(topic => { const result = attempt.concepts.find(item => item.name === topic); const state = result ? result.correct ? "strong" : "practice" : "unassessed"; return <div className={`topic-state ${state}`} key={topic}><span><Icon name={result?.correct ? "check" : result ? "spark" : "more"}/></span><p><strong>{topic}</strong><small>{state === "strong" ? "Correct in your latest quiz" : state === "practice" ? "Incorrect in your latest quiz" : "No submitted answer yet"}</small></p><Badge tone={state === "strong" ? "sage" : state === "practice" ? "peach" : "neutral"}>{state === "strong" ? "Strong" : state === "practice" ? "Needs practice" : "Not assessed"}</Badge></div>})}</div></section><aside className="panel evidence-panel"><p className="eyebrow">LATEST EVIDENCE</p><h3>{attempt.score} of {attempt.total} correct</h3><p>{new Date(attempt.completedAt).toLocaleDateString()} · {attempt.source === "quiz" ? "Quiz" : "Study session"}</p><hr/><strong>How this works</strong><p>Correct answers support “strong” for this attempt. Incorrect answers flag practice. More sessions are needed before claiming lasting mastery.</p></aside></div>}
  </div>;
}

function Recommendations({ attempt, start, library }: { attempt: Attempt | null; start: () => void; library: () => void }) {
  const gaps = attempt?.concepts.filter(item => !item.correct) || [];
  return <div className="page recommendation-page"><button className="back-link" onClick={library}>← Learning Resources</button><section className="workflow-hero"><div><Badge tone="peach">ADAPTIVE PRACTICE</Badge><h2>{gaps.length ? "Let’s strengthen the parts that need another look." : "Your next step will appear here."}</h2><p>Recommendations use your latest submitted answers and preserve the original resource version.</p></div><Lumi size="medium"/></section>
    {!attempt ? <section className="empty-evidence panel"><div><Icon name="spark"/></div><h3>Complete one activity first</h3><p>Once Calibrat8 has real answer evidence, targeted notes, cards, and practice will appear here.</p><Button onClick={start} icon="play">Start study mode</Button></section> :
    <div className="recommendation-grid">{gaps.length ? gaps.map((gap, index) => <section className="panel recommendation-card" key={gap.name}><span className="recommendation-icon"><Icon name={index % 2 ? "cards" : "quiz"}/></span><Badge tone="peach">BASED ON LATEST QUIZ</Badge><h3>Review {gap.name.toLowerCase()}</h3><p>You missed the question connected to this concept. Try a short explanation, then answer a similar check.</p><div className="version-note"><Icon name="layers"/><span><strong>Suggested update · Version 2</strong><small>Version 1 remains available</small></span></div><Button onClick={start} icon="play" className="full-button">Start targeted practice</Button></section>) : <section className="panel recommendation-card"><span className="recommendation-icon"><Icon name="check"/></span><Badge>NO GAPS IN LATEST QUIZ</Badge><h3>Revisit later for spaced practice</h3><p>Your latest answers were correct. Calibrat8 will not invent a weakness; review again later to strengthen retention.</p><Button onClick={library} variant="secondary">Back to resources</Button></section>}</div>}
  </div>;
}

function ComparisonReport({ attempts, takeQuiz }: { attempts: Attempt[]; takeQuiz: () => void }) {
  if (!attempts.length) return <div className="page report-page"><section className="workflow-hero"><div><Badge tone="blue">REPORT LEARNING</Badge><h2>Your learning insights will appear here.</h2><p>Complete a study session or quiz to begin a report based on your actual answers.</p></div></section><section className="empty-evidence panel"><div><Icon name="chart" size={28}/></div><h3>No learning evidence yet</h3><p>Calibrat8 won’t invent strengths, gaps, or weekly trends. Your first completed activity will start this report.</p><Button onClick={takeQuiz} icon="quiz">Take a quiz</Button></section></div>;

  const conceptEvidence = new Map<string, { correct: number; total: number }>();
  attempts.forEach(attempt => attempt.concepts.forEach(concept => {
    const evidence = conceptEvidence.get(concept.name) || { correct: 0, total: 0 };
    conceptEvidence.set(concept.name, { correct: evidence.correct + (concept.correct ? 1 : 0), total: evidence.total + 1 });
  }));
  const concepts = Array.from(conceptEvidence, ([name, evidence]) => ({ name, ...evidence, accuracy: Math.round(evidence.correct / evidence.total * 100) }));
  const strengths = concepts.filter(concept => concept.correct > concept.total - concept.correct).sort((a, b) => b.accuracy - a.accuracy);
  const needsPractice = concepts.filter(concept => concept.correct <= concept.total - concept.correct).sort((a, b) => a.accuracy - b.accuracy);
  const overallScore = Math.round(attempts.reduce((sum, attempt) => sum + attempt.score, 0) / attempts.reduce((sum, attempt) => sum + attempt.total, 0) * 100);
  const currentWeek = new Date();
  currentWeek.setHours(0, 0, 0, 0);
  currentWeek.setDate(currentWeek.getDate() - ((currentWeek.getDay() + 6) % 7));
  const weeks = Array.from({ length: 6 }, (_, index) => {
    const start = new Date(currentWeek);
    start.setDate(start.getDate() - (5 - index) * 7);
    const end = new Date(start);
    end.setDate(end.getDate() + 7);
    const weekAttempts = attempts.filter(attempt => { const date = new Date(attempt.completedAt); return date >= start && date < end; });
    const answered = weekAttempts.reduce((sum, attempt) => sum + attempt.total, 0);
    const correct = weekAttempts.reduce((sum, attempt) => sum + attempt.score, 0);
    return { label: start.toLocaleDateString(undefined, { month: "short", day: "numeric" }), sessions: weekAttempts.length, average: answered ? Math.round(correct / answered * 100) : 0 };
  });

  return <div className="page report-page">
    <section className="workflow-hero"><div><Badge tone="blue">REPORT LEARNING</Badge><h2>What’s working—and what to practice next.</h2><p>Insights and weekly analysis use only your saved quiz and study-session answers.</p></div><Button onClick={takeQuiz} variant="secondary" icon="quiz">Add quiz evidence</Button></section>
    <div className="report-grid">
      <section className="panel weekly-report"><div className="section-heading"><div><p className="eyebrow">WEEKLY ANALYSIS</p><h3>Performance across six weeks</h3></div><Badge tone="neutral">Actual activity</Badge></div><div className="weekly-chart" aria-label="Average answer performance by week">{weeks.map(week => <div className="weekly-column" key={week.label}><div className="weekly-value">{week.sessions ? `${week.average}%` : "—"}</div><div className="weekly-track"><i className={week.sessions ? "has-data" : ""} style={{ height: `${week.sessions ? Math.max(12, week.average) : 4}%` }}/></div><strong>{week.label}</strong><small>{week.sessions} session{week.sessions === 1 ? "" : "s"}</small></div>)}</div><p className="report-caveat">Weekly bars show average correct answers only when activity exists. A score change alone does not prove long-term learning.</p></section>
      <section className="panel report-summary"><p className="eyebrow">AT A GLANCE</p><div><strong>{attempts.length}</strong><small>Sessions completed</small></div><div><strong>{overallScore}%</strong><small>Correct across saved answers</small></div><div><strong>{concepts.length}</strong><small>Concepts assessed</small></div></section>
    </div>
    <div className="report-details">
      <section className="panel"><div className="insight-title"><span><Icon name="check"/></span><div><p className="eyebrow">YOU EXCEL AT</p><h3>Evidence-backed strengths</h3></div></div>{strengths.length ? strengths.map(concept => <p key={concept.name}><Icon name="check"/><span><strong>{concept.name}</strong><small>{concept.correct} of {concept.total} checks correct · {concept.accuracy}%</small></span></p>) : <p className="muted">Complete more questions correctly to establish a strength.</p>}</section>
      <section className="panel"><div className="insight-title practice"><span><Icon name="spark"/></span><div><p className="eyebrow">PRACTICE NEXT</p><h3>Concepts needing attention</h3></div></div>{needsPractice.length ? needsPractice.map(concept => <p key={concept.name}><Icon name="spark"/><span><strong>{concept.name}</strong><small>{concept.correct} of {concept.total} checks correct · review, then retry</small></span></p>) : <p className="muted">No practice gap is supported by your saved answers right now.</p>}</section>
    </div>
  </div>;
}

function Settings({ online, setOnline, editProfile, profile }: { online: boolean; setOnline: (online: boolean) => void; editProfile: () => void; profile: ProfileData }) {
  return <div className="page settings-page"><section className="workflow-hero"><div><Badge tone="neutral">SETTINGS & OFFLINE STATUS</Badge><h2>Clear controls, honest capability states.</h2><p>Manage your learning profile and simulate connectivity for prototype testing.</p></div></section><div className="settings-grid"><section className="panel setting-card"><span className={`setting-icon ${online ? "" : "muted"}`}><Icon name={online ? "wifi" : "offline"}/></span><div><h3>{online ? "You’re online" : "You’re offline"}</h3><p>{online ? "Connected prototype features are available. No real AI model is connected." : "Saved notes, cards, quizzes, and results remain available. New generation is unavailable."}</p></div><Button variant={online ? "secondary" : "primary"} onClick={() => setOnline(!online)} icon={online ? "offline" : "wifi"}>{online ? "Simulate offline" : "Reconnect"}</Button></section><section className="panel setting-card"><span className="setting-icon"><Icon name="download"/></span><div><h3>Offline library</h3><p>Cell division notes, flashcards, quiz, and saved results are available in this browser session.</p></div><Badge>Ready</Badge></section><section className="panel setting-card"><span className="setting-icon"><Icon name="spark"/></span><div><h3>Local AI device profile</h3><p>{profile.deviceType} · {profile.deviceMemory} RAM · {profile.modelPreference} preference. No model is installed or tested by this prototype.</p></div><Badge tone="neutral">Recommendation saved</Badge></section><section className="panel setting-card"><span className="setting-icon"><Icon name="edit"/></span><div><h3>Learning profile</h3><p>Update subjects, study routine, learning style, device fit, and personalization preferences.</p></div><Button variant="secondary" onClick={editProfile}>Edit profile</Button></section></div></div>;
}

function Lessons({ online, addMaterial }: { online: boolean; addMaterial: () => void }) {
  const [stage, setStage] = useState<"consent" | "recording" | "notes">("consent");
  const [paused, setPaused] = useState(false);
  const [cards, setCards] = useState(false);
  return <div className="page lessons-page">
    <div className="lesson-layout">
      <aside className="lesson-library panel"><div className="section-heading"><div><p className="eyebrow">MY LESSONS</p><h3>Saved lessons</h3></div><button className="square-button" onClick={addMaterial} aria-label="Add study material"><Icon name="plus"/></button></div><Button onClick={addMaterial} variant="soft" icon="upload" className="full-button lesson-add">Add study material</Button><div className="search-box"><Icon name="search" size={17}/><input placeholder="Search lessons…" aria-label="Search lessons"/></div>
        <button className="lesson-list-item active"><span className="subject-dot biology"/><span><strong>Cell division & mitosis</strong><small>Biology · Today</small></span><Badge>Saved</Badge></button>
        <button className="lesson-list-item"><span className="subject-dot maths"/><span><strong>Quadratic functions</strong><small>Maths · Monday</small></span></button>
        <button className="lesson-list-item"><span className="subject-dot history"/><span><strong>Industrial Revolution</strong><small>History · May 16</small></span></button>
      </aside>
      <section className="lesson-main">
        {stage === "consent" && <div className="consent-card panel"><div className="record-illustration"><Icon name="mic" size={30}/><i/></div><Badge tone="peach">BEFORE YOU RECORD</Badge><h2>Make sure everyone is comfortable.</h2><p>Only record after your teacher and anyone speaking have clearly agreed. Recording rules may differ at your school or location.</p><label className="consent-check"><input type="checkbox" id="consent"/><span><Icon name="check" size={15}/></span><strong>I have permission from everyone being recorded.</strong></label><div className="consent-actions"><Button onClick={() => setStage("recording")} icon="mic">Start recording</Button><Button onClick={addMaterial} variant="secondary" icon="upload">Add notes or files</Button></div><p className="prototype-note">Prototype only: microphone capture and transcription are not connected.</p></div>}
        {stage === "recording" && <div className="recording-card panel"><Badge tone="peach"><span className="record-dot"/> {paused ? "PAUSED" : "RECORDING"}</Badge><div className="timer">08:42</div><p>Biology · Cell division</p><div className={`waveform ${paused ? "paused" : ""}`}>{Array.from({ length: 42 }).map((_, i) => <i key={i} style={{ height: `${16 + (i * 17) % 52}%` }}/>)}</div><div className="record-controls"><button onClick={() => setPaused(!paused)}><Icon name={paused ? "play" : "pause"}/><span>{paused ? "Resume" : "Pause"}</span></button><button className="stop-control" onClick={() => setStage("notes")}><Icon name="stop"/><span>Stop & save</span></button></div><p className="prototype-note">Visual recording demo only. No audio is being captured.</p></div>}
        {stage === "notes" && <div className="notes-view"><div className="notes-head"><div><Badge>Biology · Saved on device</Badge><h2>Cell division & mitosis</h2><p>Today, 10:20 AM · 32 min lesson</p></div><Button variant="secondary" icon="download">Available offline</Button></div>
          <div className="notes-grid"><article className="panel generated-notes"><p className="eyebrow">DEMO GENERATED NOTES</p><h3>Lesson summary</h3><p>Cell division allows organisms to grow, repair tissue, and reproduce. Mitosis creates two genetically identical daughter cells through a sequence of distinct phases.</p><h3>Key concepts</h3><ul><li><strong>Interphase:</strong> The cell grows and copies its DNA before division.</li><li><strong>Mitosis:</strong> Prophase, metaphase, anaphase, and telophase.</li><li><strong>Cytokinesis:</strong> The cytoplasm divides to form two cells.</li></ul><div className="transcript-preview"><span>12:18</span><p>“During metaphase, the chromosomes line up at the cell’s equator…”</p></div></article>
          <aside className="stack"><div className="panel create-materials"><p className="eyebrow">STUDY MATERIALS</p><button onClick={() => setCards(true)}><Icon name="cards"/><span><strong>Generate flashcards</strong><small>8 key concepts found</small></span><Icon name="arrow"/></button><button><Icon name="quiz"/><span><strong>Create a practice quiz</strong><small>6 suggested questions</small></span><Icon name="arrow"/></button></div>{cards && <div className="panel success-card"><span><Icon name="check"/></span><div><strong>8 demo flashcards ready</strong><p>Saved with this lesson for offline study.</p></div></div>}<div className="panel availability"><Icon name={online ? "wifi" : "offline"}/><p><strong>{online ? "Online processing available" : "Offline limitation"}</strong><br/>{online ? "In a connected product, transcription could process now." : "New transcription requires a connection. Saved notes remain available."}</p></div></aside></div>
        </div>}
      </section>
    </div>
  </div>;
}

function Progress({ openCoach }: { openCoach: () => void }) {
  return <div className="page progress-page">
    <section className="progress-hero"><div><Badge tone="blue">PRACTICE & PROGRESS</Badge><h2>You’re building a stronger foundation.</h2><p>Here’s what your saved practice data suggests—and what to focus on next.</p></div><Button onClick={openCoach} icon="play">Start recommended practice</Button></section>
    <div className="progress-grid">
      <section className="panel narrative-card"><p className="eyebrow">THIS WEEK’S STORY</p><div className="story-lead"><ProgressRing value={72} label="3 topics"/><div><h3>Your algebra steps are becoming more consistent.</h3><p>You correctly used inverse operations in 6 of 8 recent questions. Sign changes still need one more focused round.</p></div></div><div className="evidence-row"><span><Icon name="check"/><p><strong>Strength</strong> Solving one-step equations</p></span><span><Icon name="spark"/><p><strong>Focus next</strong> Negative coefficients</p></span></div></section>
      <section className="panel next-card"><p className="eyebrow">RECOMMENDED NEXT</p><Badge tone="peach">12 MINUTES</Badge><h3>Practice sign changes</h3><p>Based on two incorrect answers from your May 21 algebra quiz.</p><Button onClick={openCoach} variant="soft" icon="arrow">Review mistakes</Button></section>
    </div>
    <section className="panel attempts"><div className="section-heading"><div><p className="eyebrow">RECENT ATTEMPTS</p><h3>Learning history</h3></div><span className="demo-label">SAMPLE DATA</span></div>
      {[["Algebra practice", "6 of 8 correct", "May 21", "Improved from last attempt"], ["Cell biology quick quiz", "7 of 10 correct", "May 19", "Review mitosis phases"], ["French Revolution recall", "8 of 9 correct", "May 17", "Strong understanding"]].map((x, i) => <button className="attempt-row" key={x[0]}><span className={`attempt-icon a${i}`}><Icon name={i === 0 ? "quiz" : i === 1 ? "book" : "file"}/></span><span><strong>{x[0]}</strong><small>{x[2]} · {x[1]}</small></span><Badge tone={i === 2 ? "sage" : i === 0 ? "peach" : "blue"}>{x[3]}</Badge><Icon name="chevron"/></button>)}
    </section>
  </div>;
}

function Coach({ back }: { back: () => void }) {
  const [practice, setPractice] = useState(false);
  if (practice) return <div className="page coach-page"><button className="back-link" onClick={() => setPractice(false)}>← Back to analysis</button><div className="practice-question panel"><Badge tone="peach">TARGETED PRACTICE · 1 OF 4</Badge><h2>Solve: −2x + 6 = 14</h2><p>What should you do first?</p>{["Subtract 6 from both sides", "Divide both sides by −2", "Add 2 to both sides"].map((x, i) => <button key={x}><span>{String.fromCharCode(65 + i)}</span>{x}</button>)}</div></div>;
  return <div className="page coach-page"><button className="back-link" onClick={back}>← Practice & Progress</button><section className="coach-head"><div><Badge tone="peach">ADAPTIVE LEARNING COACH</Badge><h2>You’re getting closer.</h2><p>Let’s look at the evidence, then practice this concept one more time.</p></div><div className="score-card"><strong>6<span>/8</span></strong><small>Algebra quiz · May 21</small></div></section>
    <div className="coach-grid"><section className="panel mistakes"><p className="eyebrow">WHAT NEEDS ATTENTION</p><h3>Two answers share the same pattern.</h3><p>In both questions, the negative sign was lost while isolating <b>x</b>. That suggests the inverse-operation step needs review. One quiz is not enough to label this a lasting misconception.</p>
      <div className="mistake-item"><div><span>QUESTION 4</span><strong>Solve: −3x = 12</strong></div><div className="answer-compare"><span className="wrong">Your answer: x = 4</span><span className="right">Correct: x = −4</span></div><button>See explanation <Icon name="chevron" size={15}/></button></div>
      <div className="mistake-item"><div><span>QUESTION 7</span><strong>Solve: 5 − 2x = 11</strong></div><div className="answer-compare"><span className="wrong">Your answer: x = 3</span><span className="right">Correct: x = −3</span></div><button>See explanation <Icon name="chevron" size={15}/></button></div>
    </section><aside className="stack"><section className="panel practice-plan"><p className="eyebrow">YOUR PRACTICE PLAN</p><h3>12 focused minutes</h3><div><span>1</span><p><strong>Review the rule</strong><small>2 min · inverse operations</small></p></div><div><span>2</span><p><strong>Try four questions</strong><small>8 min · negative coefficients</small></p></div><div><span>3</span><p><strong>Explain one answer</strong><small>2 min · check understanding</small></p></div><Button onClick={() => setPractice(true)} icon="play" className="full-button">Start practice</Button></section><section className="panel strength-note"><Icon name="check"/><p><strong>What’s already working</strong><br/>You set up both equations correctly and handled addition consistently.</p></section></aside></div>
  </div>;
}

const defaultProfile: ProfileData = {
  name: "Calibrat8 Learner",
  level: "Senior high school",
  subjects: ["Mathematics", "Biology", "History"],
  examDate: "",
  dailyMinutes: "60",
  studyTime: "After school",
  learningStyle: "Examples, then practice",
  personalization: true,
  deviceType: "Laptop",
  deviceMemory: "8 GB",
  modelPreference: "Balanced",
  learningTopic: "",
  learningSources: [],
};

function readSavedProfile() {
  try {
    const saved = localStorage.getItem("calibrat8-profile") || localStorage.getItem("studypath-profile");
    if (!saved) return null;
    const parsed = JSON.parse(saved) as Partial<ProfileData>;
    return {
      ...defaultProfile,
      ...parsed,
      learningTopic: typeof parsed.learningTopic === "string" ? parsed.learningTopic : "",
      learningSources: Array.isArray(parsed.learningSources) ? parsed.learningSources : [],
    } as ProfileData;
  } catch {
    return null;
  }
}

function readSavedAttempts(): Attempt[] {
  try {
    const saved = localStorage.getItem("calibrat8-attempts");
    return saved ? JSON.parse(saved) as Attempt[] : [];
  } catch {
    return [];
  }
}

function readSavedPage(): Page {
  const availablePages: Page[] = ["home", "tutor", "planner", "lessons", "ingest", "generation", "library", "notes", "flashcards", "quiz", "knowledge", "recommendations", "report", "settings", "coach", "progress"];
  try {
    const saved = localStorage.getItem("calibrat8-last-page") as Page | null;
    return saved && availablePages.includes(saved) ? saved : "home";
  } catch {
    return "home";
  }
}

function MascotFlightOverlay({ onEnd }: { onEnd: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onEnd, 2400);
    return () => clearTimeout(timer);
  }, [onEnd]);

  return (
    <div className="mascot-flight-overlay">
      <div className="mascot-flight-container">
        <Calibrat8Mascot size="large" expression="excited" />
      </div>
    </div>
  );
}

function ProfileSetup({ initial, editing, returning, onComplete, onCancel, onResume, onStartNew }: {
  initial: ProfileData;
  editing: boolean;
  returning: boolean;
  onComplete: (profile: ProfileData) => void;
  onCancel: () => void;
  onResume: () => void;
  onStartNew: () => void;
}) {
  const [step, setStep] = useState(editing ? 1 : 0);
  const [profile, setProfile] = useState(initial);
  const [analysisStage, setAnalysisStage] = useState(0);
  const [detectedCores, setDetectedCores] = useState<number | null>(null);
  const [topicMethod, setTopicMethod] = useState<"text" | "voice" | "camera" | "files">("text");
  const [topicFiles, setTopicFiles] = useState<IngestedFile[]>(() => (initial.learningSources || []).map(name => ({ name, size: "Saved source", type: name.split(".").pop()?.toUpperCase() || "FILE" })));
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [recordingError, setRecordingError] = useState("");
  const recorderRef = useRef<MediaRecorder | null>(null);
  const recordingStreamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const memoryAmount = Number.parseInt(profile.deviceMemory, 10);
  const isMobileDevice = profile.deviceType === "Phone" || profile.deviceType === "Tablet";
  const modelFit = isMobileDevice
    ? memoryAmount >= 8
      ? { tier: "3B–4B mobile-friendly model", detail: "This is a practical upper range for a modern mobile device. Close other apps during local processing.", tone: "blue" as const }
      : { tier: "1B–2B compact model", detail: "A compact model is the safer mobile choice for lower memory use, heat, and battery impact.", tone: "peach" as const }
    : memoryAmount >= 16 && (detectedCores || 0) >= 8
      ? { tier: "7B–8B quantized model", detail: "A balanced local model should fit comfortably for study tasks while leaving room for other apps.", tone: "sage" as const }
      : memoryAmount >= 8 || (!Number.isFinite(memoryAmount) && (detectedCores || 0) >= 6)
        ? { tier: "3B–4B quantized model", detail: "A smaller local model is the safer default for responsive tutoring and summaries.", tone: "blue" as const }
        : { tier: "1B–2B compact model", detail: "Use a compact model to reduce memory pressure and avoid slowdowns. Larger models should use a connected service.", tone: "peach" as const };
  useEffect(() => {
    if (step !== 2) return;
    setAnalysisStage(0);
    setDetectedCores(16);
    const timers = [
      window.setTimeout(() => setAnalysisStage(1), 350),
      window.setTimeout(() => setAnalysisStage(2), 950),
      window.setTimeout(() => {
        setProfile(current => ({
          ...current,
          deviceType: "Windows 11 desktop",
          deviceMemory: "15.9 GB",
          modelPreference: "",
        }));
        setAnalysisStage(3);
      }, 1550),
      window.setTimeout(() => setAnalysisStage(4), 2250),
    ];
    return () => timers.forEach(timer => window.clearTimeout(timer));
  }, [step]);
  useEffect(() => {
    if (!isRecording) return;
    const timer = window.setInterval(() => setRecordingSeconds(seconds => seconds + 1), 1000);
    return () => window.clearInterval(timer);
  }, [isRecording]);
  useEffect(() => () => {
    if (recorderRef.current?.state === "recording") recorderRef.current.stop();
    recordingStreamRef.current?.getTracks().forEach(track => track.stop());
  }, []);
  const toggleSubject = (subject: string) => setProfile(current => ({
    ...current,
    subjects: current.subjects.includes(subject) ? current.subjects.filter(item => item !== subject) : [...current.subjects, subject].slice(0, 4),
  }));
  const addTopicFiles = (list: FileList | null) => {
    if (!list) return;
    const additions = Array.from(list).map(file => ({
      name: file.name,
      size: file.size > 1048576 ? `${(file.size / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(file.size / 1024))} KB`,
      type: file.name.split(".").pop()?.toUpperCase() || "FILE",
    }));
    const nextFiles = [...topicFiles, ...additions].slice(0, 4);
    setTopicFiles(nextFiles);
    setProfile(current => ({ ...current, learningSources: nextFiles.map(file => file.name) }));
  };
  const removeTopicFile = (index: number) => {
    const nextFiles = topicFiles.filter((_, fileIndex) => fileIndex !== index);
    setTopicFiles(nextFiles);
    setProfile(current => ({ ...current, learningSources: nextFiles.map(file => file.name) }));
  };
  const startVoiceRecording = async () => {
    setRecordingError("");
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      setRecordingError("In-app recording is not supported by this browser. You can use File to add an audio recording instead.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      recordingStreamRef.current = stream;
      recorderRef.current = recorder;
      audioChunksRef.current = [];
      recorder.ondataavailable = event => {
        if (event.data.size) audioChunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: recorder.mimeType || "audio/webm" });
        const extension = recorder.mimeType.includes("mp4") ? "m4a" : "webm";
        const recording: IngestedFile = {
          name: `Voice topic ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}.${extension}`,
          size: `${Math.max(1, Math.round(blob.size / 1024))} KB`,
          type: extension.toUpperCase(),
        };
        setTopicFiles(current => {
          const nextFiles = [...current, recording].slice(0, 4);
          setProfile(currentProfile => ({ ...currentProfile, learningSources: nextFiles.map(file => file.name) }));
          return nextFiles;
        });
        stream.getTracks().forEach(track => track.stop());
        recordingStreamRef.current = null;
        audioChunksRef.current = [];
      };
      recorder.start();
      setRecordingSeconds(0);
      setIsRecording(true);
    } catch {
      setRecordingError("Microphone access was not available. Check your browser permission and try again.");
    }
  };
  const stopVoiceRecording = () => {
    if (recorderRef.current?.state === "recording") recorderRef.current.stop();
    setIsRecording(false);
  };

  return <div className="onboarding-shell">
    <header className="onboarding-header">
      <button className="brand" aria-label="Calibrat8 home"><span className="brand-mark"><Icon name="spark" size={18}/></span><span>Calibrat8</span></button>
      <div className="onboarding-progress" aria-label={`Setup step ${step + 1} of 5`}><span style={{ width: `${(step + 1) * 20}%` }}/></div>
      <span className="setup-count">{step + 1} of 5</span>
    </header>

    {step === 0 && <main className="welcome-step">
      <div className="welcome-lumi"><div className="welcome-glow"/><Lumi size="large"/></div>
      <Badge tone="peach">{returning ? "WELCOME BACK" : "WELCOME TO CALIBRAT8"}</Badge>
      <h1>{returning ? `Ready when you are, ${initial.name.trim().split(" ")[0] || "Learner"}.` : "A little light for every learning moment."}</h1>
      <p>{returning ? "Resume where you stopped, review your learning preferences, or begin a fresh journey. Nothing changes until you choose." : "Tell us a little about how you study. We’ll use your choices to make recommendations more relevant—and you can change them anytime."}</p>
      <div className="welcome-promises"><span><Icon name="check"/><strong>{returning ? "Progress saved" : "About 2 minutes"}</strong></span><span><Icon name="offline"/><strong>Works offline</strong></span><span><Icon name="edit"/><strong>Always editable</strong></span></div>
      {returning ? <div className="returning-actions">
        <div className="returning-buttons-row">
          <Button onClick={onResume} icon="play">Resume my learning</Button>
          <Button variant="secondary" onClick={() => setStep(1)} icon="edit">Review personalization</Button>
        </div>
        <button className="new-journey-button" onClick={() => { onStartNew(); setProfile(defaultProfile); setTopicFiles([]); setTopicMethod("text"); setStep(1); }}><Icon name="plus"/><span><strong>Start a new learning journey</strong><small>Clear the saved profile and learning history on this device</small></span><Icon name="chevron"/></button>
      </div> : <>
        <Button onClick={() => setStep(1)} icon="arrow">Set up my learning space</Button>
        <button className="setup-skip" onClick={() => onComplete(defaultProfile)}>Explore with a sample profile</button>
      </>}
    </main>}

    {step === 1 && <main className="setup-card">
      <div className="setup-heading"><Badge tone="blue">ABOUT YOU</Badge><h1>Let’s make this space yours.</h1><p>We only need enough detail to organize subjects and suggest useful next steps.</p></div>
      <div className="setup-form">
        <label className="setup-field"><span>What should Calibrat8 call you?</span><input value={profile.name} onChange={e => setProfile({ ...profile, name: e.target.value })} placeholder="Your name"/></label>
        <label className="setup-field"><span>Age range</span><select value={profile.level} onChange={e => setProfile({ ...profile, level: e.target.value })}><option>Under 13</option><option>13–17</option><option>18–24</option><option>25–34</option><option>35–49</option><option>50 or older</option><option>Prefer not to say</option></select></label>
        <div className="setup-field"><span>Your interests <small>Choose up to four</small></span><div className="choice-grid">{["Science & nature", "Math & logic", "History & culture", "Languages", "Technology", "Arts & creativity"].map(interest => <button key={interest} className={profile.subjects.includes(interest) ? "selected" : ""} onClick={() => toggleSubject(interest)}><span>{interest.slice(0, 2)}</span>{interest}{profile.subjects.includes(interest) && <Icon name="check" size={15}/>}</button>)}</div><input aria-label="Add a custom interest" placeholder="Add another interest and press Enter…" disabled={profile.subjects.length >= 4} onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); const interest = e.currentTarget.value.trim(); if (interest && !profile.subjects.includes(interest)) { toggleSubject(interest); e.currentTarget.value = ""; } } }}/></div>
      </div>
      <div className="setup-actions">{editing && <Button variant="ghost" onClick={onCancel}>Cancel</Button>}<Button variant="secondary" onClick={() => setStep(0)}>Back</Button><Button disabled={!profile.name.trim() || profile.subjects.length === 0} onClick={() => setStep(2)} icon="arrow">Analyze my device</Button></div>
    </main>}

    {step === 2 && <main className="setup-card">
      <div className="setup-heading"><Badge tone="blue">{analysisStage < 4 ? "ANALYZING DEVICE" : "CHOOSE YOUR MODEL"}</Badge><h1>{analysisStage < 4 ? "Finding the smoothest fit for your device." : "Select the local model you prefer."}</h1><p>This prototype uses the device specifications you provided to compare models. No model is downloaded or installed during setup.</p></div>
      <div className="panel automatic-analysis" aria-live="polite">
        {analysisStage < 4 ? <>
          <div className="analysis-orb"><Icon name={analysisStage < 4 ? "spark" : "check"} size={27}/><i/></div>
          <div className="analysis-copy"><p className="eyebrow">AUTOMATIC CHECK</p><h3>{analysisStage < 4 ? "Reading safe browser signals…" : "Analysis complete"}</h3><p>{analysisStage < 4 ? "This takes only a moment." : "Your recommendation favors smooth performance and leaves room for study materials."}</p></div>
          <div className="animated-analysis">
            {["Reading system and memory", "Checking GPU and VRAM", "Reviewing storage and CPU", "Matching compatible models"].map((message, index) => <div className={analysisStage > index ? "complete" : analysisStage === index ? "active" : ""} key={message}><span>{analysisStage > index ? <Icon name="check" size={14}/> : <i/>}</span><p><strong>{message}</strong><small>{analysisStage > index ? "Complete" : analysisStage === index ? "Analyzing…" : "Waiting"}</small></p></div>)}
          </div>
        </> : <div>
          <div className="device-analysis-head"><span><Icon name="check"/></span><div><p className="eyebrow">ANALYSIS COMPLETE</p><h3>Your device can run compact and 7B quantized models.</h3></div></div>
          <div className="summary-stats">
            <span><strong>15.9 GB</strong><small>RAM</small></span>
            <span><strong>6 GB</strong><small>GTX 1660 SUPER VRAM</small></span>
            <span><strong>16</strong><small>CPU cores</small></span>
            <span><strong>52.1 GB</strong><small>Free storage</small></span>
            <span><strong>Windows 11</strong><small>Operating system</small></span>
            <span><strong>NVIDIA</strong><small>GPU acceleration</small></span>
          </div>
          <div className="section-heading"><div><p className="eyebrow">COMPATIBLE MODELS</p><h3>Choose one model</h3></div><Badge tone="neutral">{profile.modelPreference || "Not selected"}</Badge></div>
          <div className="learning-styles">
            {[
              ["Llama 3.2 3B Instruct · Q4", "Recommended · Fast and responsive for tutoring, summaries, and flashcards.", "spark"],
              ["Phi-3.5 Mini · Q4", "Balanced · Strong reasoning in a compact model with comfortable memory headroom.", "layers"],
              ["Qwen2.5 7B Instruct · Q4", "Best quality · Uses more of the 6 GB VRAM and may respond more slowly.", "book"],
            ].map(([name, copy, icon]) => <button key={name} className={profile.modelPreference === name ? "selected" : ""} onClick={() => setProfile({ ...profile, modelPreference: name })} aria-pressed={profile.modelPreference === name}><span><Icon name={icon as IconName}/></span><div><strong>{name}</strong><p>{copy}</p></div><i>{profile.modelPreference === name && <Icon name="check" size={15}/>}</i></button>)}
          </div>
        </div>}
      </div>
      <div className="hardware-note"><Icon name="settings"/><p><strong>Provided device profile</strong><br/>15.9 GB RAM · NVIDIA GeForce GTX 1660 SUPER · 6 GB VRAM · 16 CPU cores · 52.1 GB free · Windows 11.</p></div>
      <div className="setup-actions"><Button variant="secondary" onClick={() => setStep(1)}>Back</Button><Button disabled={analysisStage < 4 || !profile.modelPreference} onClick={() => setStep(3)} icon="arrow">Use selected model</Button></div>
    </main>}

    {step === 3 && <main className="setup-card">
      <div className="completion-lumi topic-welcome-lumi"><Lumi size="large"/></div>
      <div className="setup-heading"><Badge tone="peach">CALIBRAT8 IS READY TO HELP</Badge><h1>Hi! What would you like to learn?</h1><p>I’m happy you’re here. Type a topic, tell me by voice, show me a photo, or choose a file—we’ll take it one step at a time.</p></div>
      <section className="setup-form">
        <div className="source-tabs" role="tablist" aria-label="Choose how to add a topic">
          <button role="tab" aria-selected={topicMethod === "text"} className={topicMethod === "text" ? "active" : ""} onClick={() => setTopicMethod("text")}><Icon name="edit"/> Text</button>
          <button role="tab" aria-selected={topicMethod === "voice"} className={topicMethod === "voice" ? "active" : ""} onClick={() => setTopicMethod("voice")}><Icon name="mic"/> Voice</button>
          <button role="tab" aria-selected={topicMethod === "camera"} className={topicMethod === "camera" ? "active" : ""} onClick={() => setTopicMethod("camera")}><Icon name="image"/> Camera</button>
          <button role="tab" aria-selected={topicMethod === "files"} className={topicMethod === "files" ? "active" : ""} onClick={() => setTopicMethod("files")}><Icon name="upload"/> File</button>
        </div>
        {topicMethod === "text" && <label className="setup-field"><span>Topic you want to learn</span><input value={profile.learningTopic} onChange={e => setProfile({ ...profile, learningTopic: e.target.value })} placeholder="For example: How solar panels work"/></label>}
        {topicMethod === "voice" && <div className={`drop-zone compact-drop-zone voice-recorder ${isRecording ? "is-recording" : ""}`}>
          <Badge tone={isRecording ? "peach" : "neutral"}>{isRecording ? `RECORDING · ${Math.floor(recordingSeconds / 60)}:${String(recordingSeconds % 60).padStart(2, "0")}` : "VOICE INPUT"}</Badge>
          <span className="drop-icon voice-mic"><Icon name="mic" size={24}/><i/></span>
          <strong>{isRecording ? "I’m listening…" : "Record your topic"}</strong>
          <p>{isRecording ? "Describe what you want to learn. Speak naturally and stop when you’re finished." : "Use your microphone to tell Calibrat8 what you want to learn."}</p>
          <div className={`voice-waveform ${isRecording ? "active" : ""}`} aria-hidden="true">{Array.from({ length: 24 }).map((_, index) => <i key={index}/>)}</div>
          {isRecording ? <Button variant="secondary" onClick={stopVoiceRecording} icon="stop">Stop recording</Button> : <Button onClick={startVoiceRecording} icon="mic">Start recording</Button>}
          {recordingError && <small className="recording-error" role="alert">{recordingError}</small>}
          {!recordingError && <small>Your browser will ask for microphone permission.</small>}
        </div>}
        {topicMethod === "camera" && <label className="drop-zone compact-drop-zone"><input type="file" accept="image/*" capture="environment" onChange={e => { addTopicFiles(e.target.files); e.currentTarget.value = ""; }}/><span className="drop-icon"><Icon name="image" size={24}/></span><strong>Open your camera</strong><p>Take a photo of a page, object, diagram, or whiteboard.</p><small>Uses your device camera when supported</small></label>}
        {topicMethod === "files" && <label className="drop-zone compact-drop-zone"><input type="file" multiple accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md,image/*,audio/*" onChange={e => { addTopicFiles(e.target.files); e.currentTarget.value = ""; }}/><span className="drop-icon"><Icon name="upload" size={24}/></span><strong>Choose a learning file</strong><p>Documents, text, images, or audio</p><small>Up to 4 files during onboarding</small></label>}
        {topicFiles.length > 0 && <div className="file-queue">{topicFiles.map((file, index) => <div key={`${file.name}-${index}`}><span className="file-type">{file.type.slice(0, 4)}</span><p><strong>{file.name}</strong><small>{file.size} · Topic source added</small></p><button onClick={() => removeTopicFile(index)} aria-label={`Remove ${file.name}`}><Icon name="close" size={17}/></button></div>)}</div>}
        <div className="format-note"><Icon name="spark"/><p><strong>Prototype capture</strong><br/>Voice, photos, and files are saved as source names only. Their contents are not analyzed or uploaded to an AI service.</p></div>
      </section>
      <div className="setup-actions"><Button variant="secondary" onClick={() => setStep(2)}>Back</Button><Button disabled={profile.learningTopic.trim().length < 2 && topicFiles.length === 0} onClick={() => setStep(4)} icon="arrow">Choose learning style</Button></div>
    </main>}

    {step === 4 && <main className="setup-card">
      <div className="setup-heading"><Badge tone="peach">PERSONALIZATION</Badge><h1>How do you like to learn?</h1><p>Choose a starting preference. Calibrat8 can still explain something differently whenever you ask.</p></div>
      <div className="learning-styles">{[
        ["Learn", "Build understanding with key notes, explanations, and guided examples.", "book"],
        ["Practice", "Answer targeted questions and get immediate feedback on each concept.", "quiz"],
        ["Review", "Refresh earlier material with summaries, recall cards, and quick checks.", "cards"],
      ].map(([title, copy, icon]) => {
        const selected = profile.learningStyle === title || (title === "Learn" && profile.learningStyle === "Examples, then practice");
        return <button key={title} className={selected ? "selected" : ""} aria-pressed={selected} onClick={() => setProfile({ ...profile, learningStyle: title })}><span><Icon name={icon as IconName}/></span><div><strong>{title}</strong><p>{copy}</p></div><i>{selected && <Icon name="check" size={15}/>}</i></button>;
      })}</div>
      <label className="personalization-toggle"><span><Icon name="spark"/><p><strong>Personalized recommendations</strong><small>Use saved quiz attempts, completed activities, and your preferences to suggest what to study next.</small></p></span><input type="checkbox" checked={profile.personalization} onChange={e => setProfile({ ...profile, personalization: e.target.checked })}/><i/></label>
      <div className="local-ai-note"><Icon name="offline"/><p><strong>Local AI is not configured on this device.</strong><br/>Saved lessons, plans, flashcards, and supported quizzes still work offline. Live AI features require a connection.</p></div>
      <div className="setup-actions"><Button variant="secondary" onClick={() => setStep(3)}>Back</Button><Button onClick={() => onComplete(profile)} icon="check">{editing ? "Save preferences" : "Finish setup"}</Button></div>
    </main>}
  </div>;
}

function OfflineModal({ online, close, toggle }: { online: boolean; close: () => void; toggle: () => void }) {
  const [saved, setSaved] = useState(false);
  return <div className="modal-backdrop" onMouseDown={close}><section className="offline-modal" onMouseDown={e => e.stopPropagation()}><button className="modal-close" onClick={close}><Icon name="close"/></button><div className="modal-icon"><Icon name="download"/></div><Badge tone={online ? "sage" : "neutral"}>{online ? "ONLINE NOW" : "OFFLINE MODE"}</Badge><h2>{online ? "Keep learning without a connection." : "Your saved learning is ready."}</h2><p>{online ? "Save today’s essentials to this device before you go offline." : "You can use downloaded notes, flashcards, quizzes, and your current study plan."}</p>
    <div className="download-list"><span><Icon name="calendar"/><p><strong>Today’s study plan</strong><small>6 activities · 120 min</small></p><Icon name="check"/></span><span><Icon name="book"/><p><strong>3 saved lessons</strong><small>Notes and transcripts</small></p><Icon name="check"/></span><span><Icon name="cards"/><p><strong>34 flashcards</strong><small>Across 4 topics</small></p><Icon name="check"/></span></div>
    {online ? <Button onClick={() => setSaved(true)} icon={saved ? "check" : "download"} className="full-button">{saved ? "Saved to this device" : "Save for offline"}</Button> : <Button onClick={toggle} variant="secondary" icon="wifi" className="full-button">Simulate reconnection</Button>}
    <p className="prototype-note">Local AI is not configured. Live tutoring and new content generation require internet.</p></section></div>;
}

export default function App() {
  const savedProfile = readSavedProfile();
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    try {
      const saved = localStorage.getItem("calibrat8-theme");
      if (saved === "dark" || saved === "light") return saved;
      return window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
    } catch {
      return "dark";
    }
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("calibrat8-theme", theme);
    } catch {}
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === "dark" ? "light" : "dark");
  const [page, setPage] = useState<Page>(readSavedPage);
  const [online, setOnline] = useState(true);
  const [offlineOpen, setOfflineOpen] = useState(false);
  const [profile, setProfile] = useState<ProfileData>(savedProfile || defaultProfile);
  const [attempts, setAttempts] = useState<Attempt[]>(readSavedAttempts);
  const [latestAttempt, setLatestAttempt] = useState<Attempt | null>(() => readSavedAttempts().at(-1) || null);
  const [setupOpen, setSetupOpen] = useState(true);
  const [returningLearner, setReturningLearner] = useState(Boolean(savedProfile));
  const [editingProfile, setEditingProfile] = useState(false);
  const [isFlying, setIsFlying] = useState(false);
  useEffect(() => {
    localStorage.setItem("calibrat8-last-page", page);
  }, [page]);
  const saveProfile = (nextProfile: ProfileData) => {
    setProfile(nextProfile);
    localStorage.setItem("calibrat8-profile", JSON.stringify(nextProfile));
    setReturningLearner(true);
    setSetupOpen(false);
    setEditingProfile(false);
    setIsFlying(true);
  };
  const startNewJourney = () => {
    localStorage.removeItem("calibrat8-profile");
    localStorage.removeItem("studypath-profile");
    localStorage.removeItem("calibrat8-attempts");
    localStorage.removeItem("calibrat8-last-page");
    setProfile(defaultProfile);
    setAttempts([]);
    setLatestAttempt(null);
    setPage("home");
    setReturningLearner(false);
  };
  const saveAttempt = (attempt: Attempt) => {
    const next = [...attempts, attempt];
    setAttempts(next);
    setLatestAttempt(attempt);
    localStorage.setItem("calibrat8-attempts", JSON.stringify(next));
    setPage("completion");
  };
  const completeStudy = (score: number, total: number) => saveAttempt({
    score,
    total,
    completedAt: new Date().toISOString(),
    source: "study",
    concepts: [{ name: "Inverse operations", correct: score === total }],
  });
  if (setupOpen) return <ProfileSetup initial={profile} editing={editingProfile} returning={returningLearner && !editingProfile} onComplete={saveProfile} onResume={() => setSetupOpen(false)} onStartNew={startNewJourney} onCancel={() => { setSetupOpen(false); setEditingProfile(false); }}/>;
  if (page === "focus") return <Focus exit={() => setPage("library")} completeSession={completeStudy}/>;
  const titles: Record<Page, string> = {
    home: "Home", tutor: "AI Tutor", planner: "Study Mode", focus: "Focus", lessons: "Lessons",
    ingest: "Import Materials", generation: "AI Processing", library: "Learning Resources",
    notes: "Key Notes", flashcards: "Flashcards", quiz: "Quiz & Reviewer", completion: "Session Complete",
    knowledge: "Knowledge Map", recommendations: "Adaptive Practice", report: "Learning Report",
    settings: "Settings", coach: "Learning Coach", progress: "Practice & Progress",
  };
  return <div className="app-shell">
    <Sidebar page={page} setPage={setPage} online={online} setOnline={setOnline} profile={profile} editProfile={() => { setEditingProfile(true); setSetupOpen(true); }} theme={theme} toggleTheme={toggleTheme}/>
    <main className="main-shell"><Topbar title={titles[page]} online={online} setOnline={setOnline} theme={theme} toggleTheme={toggleTheme}/>
      {page === "home" && <Home go={setPage} online={online} openOffline={() => setOfflineOpen(true)} profile={profile}/>}
      {page === "tutor" && <Tutor online={online}/>}
      {page === "planner" && <Planner start={() => setPage("focus")}/>}
      {page === "lessons" && <Lessons online={online} addMaterial={() => setPage("ingest")}/>}
      {page === "ingest" && <ContentIngestion online={online} done={next => setPage(next || "library")}/>}
      {page === "generation" && <Generation online={online} back={() => setPage("ingest")} finish={() => setPage("library")}/>}
      {page === "library" && <ResourceLibrary go={setPage} create={() => setPage("ingest")}/>}
      {page === "notes" && <NotesViewer back={() => setPage("library")} start={() => setPage("focus")}/>}
      {page === "flashcards" && <FlashcardsViewer back={() => setPage("library")} takeQuiz={() => setPage("quiz")}/>}
      {page === "quiz" && <QuizViewer back={() => setPage("library")} submit={saveAttempt}/>}
      {page === "completion" && latestAttempt && <SessionCompletion attempt={latestAttempt} go={setPage}/>}
      {page === "knowledge" && <KnowledgeMap attempt={latestAttempt} recommendations={() => setPage("recommendations")}/>}
      {page === "recommendations" && <Recommendations attempt={latestAttempt} start={() => setPage("focus")} library={() => setPage("library")}/>}
      {page === "report" && <ComparisonReport attempts={attempts} takeQuiz={() => setPage("quiz")}/>}
      {page === "settings" && <Settings online={online} setOnline={setOnline} profile={profile} editProfile={() => { setEditingProfile(true); setSetupOpen(true); }} theme={theme} setTheme={setTheme}/>}
      {page === "progress" && <Progress openCoach={() => setPage("coach")}/>}
      {page === "coach" && <Coach back={() => setPage("progress")}/>}
    </main>
    <MobileNav page={page} setPage={setPage}/>
    {offlineOpen && <OfflineModal online={online} close={() => setOfflineOpen(false)} toggle={() => setOnline(true)}/>}
    {isFlying && <MascotFlightOverlay onEnd={() => setIsFlying(false)} />}
  </div>;
}
