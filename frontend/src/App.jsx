import React, { useMemo, useState } from 'react';
import { Activity, ArrowDownToLine, BrainCircuit, Building2, CheckCircle2, ChevronRight, CircleHelp, ExternalLink, FileSearch, Globe2, LoaderCircle, Search, ShieldCheck, Sparkles, Target, UploadCloud } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const sampleCompanies = 'Salesforce\nZoho\nFreshworks';

export default function App() {
  const [companies, setCompanies] = useState(sampleCompanies);
  const [industries, setIndustries] = useState('SaaS, Financial Services, Healthcare, Manufacturing, Retail, Technology');
  const [geographies, setGeographies] = useState('United States, United Kingdom, India, Canada, Australia');
  const [services, setServices] = useState('cloud, data analytics, AI automation');
  const [minEmployees, setMinEmployees] = useState(50);
  const [live, setLive] = useState(true);
  const [results, setResults] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState('All leads');
  const [health, setHealth] = useState('Checking API');

  React.useEffect(() => { fetch(`${API}/api/health`).then(r => r.ok ? setHealth('API connected') : setHealth('API unavailable')).catch(() => setHealth('API unavailable')); }, []);
  const visibleResults = useMemo(() => filter === 'All leads' ? results : results.filter(r => r.tier === filter), [results, filter]);
  const avg = results.length ? Math.round(results.reduce((s, r) => s + r.score, 0) / results.length) : 0;
  const qualified = results.filter(r => r.tier === 'High fit' || r.tier === 'Potential fit').length;

  async function runQualification() {
    const names = [...new Set(companies.split(/[\n,;]/).map(x => x.trim()).filter(Boolean))];
    if (!names.length) { setError('Enter at least one company name.'); return; }
    if (names.length > 25) { setError('Use 25 companies or fewer per run.'); return; }
    setBusy(true); setError(''); setWarnings([]); setResults([]); setSelected(null);
    try {
      const response = await fetch(`${API}/api/qualify`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ companies: names, research_live: live, icp: { target_industries: industries.split(',').map(s => s.trim()).filter(Boolean), target_geographies: geographies.split(',').map(s => s.trim()).filter(Boolean), min_employee_count: Number(minEmployees), ideal_employee_count: 500, services: services.split(',').map(s => s.trim()).filter(Boolean) } }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Qualification failed.');
      setResults(data.results || []); setWarnings(data.warnings || []); setSelected(data.results?.[0] || null);
    } catch (e) { setError(`${e.message}. Confirm the backend is running at ${API}.`); }
    finally { setBusy(false); }
  }

  function download(kind) { window.open(`${API}/api/export/${kind}`, '_blank', 'noopener,noreferrer'); }
  function onFile(e) {
    const file = e.target.files?.[0]; if (!file) return;
    const reader = new FileReader(); reader.onload = () => setCompanies(String(reader.result).split(/\r?\n/).map(s => s.split(',')[0].replace(/^"|"$/g, '').trim()).filter(Boolean).slice(0, 25).join('\n'));
    reader.readAsText(file); e.target.value = '';
  }
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><BrainCircuit size={22}/></div><div><strong>xdigics<span>.</span></strong><small>LEAD INTELLIGENCE</small></div></div>
      <div className="workspace-label">WORKSPACE</div><button className="nav active"><Activity size={17}/> Lead qualification</button><button className="nav" onClick={() => document.getElementById('icp-panel')?.scrollIntoView({behavior:'smooth'})}><Target size={17}/> ICP configuration</button><button className="nav" onClick={() => document.getElementById('evidence-panel')?.scrollIntoView({behavior:'smooth'})}><FileSearch size={17}/> Evidence review</button>
      <div className="sidebar-bottom"><div className="status-dot"/><div><b>{health}</b><small>Local development environment</small></div></div>
    </aside>
    <main className="main-content">
      <header className="topbar"><div className="crumb">Workspace <ChevronRight size={14}/> <b>Lead qualification</b></div><div className="top-right"><span className="live-pill"><span/> {live ? 'Live research enabled' : 'Research disabled'}</span><div className="avatar">AI</div></div></header>
      <section className="hero"><div><div className="eyebrow"><Sparkles size={14}/> AGENTIC RESEARCH WORKFLOW</div><h1>Find the leads worth<br/><span>your team's attention.</span></h1><p>Research public company signals, score ICP fit transparently, and review the evidence behind every recommendation.</p><div className="hero-tags"><span><Globe2 size={14}/> Public web sources</span><span><ShieldCheck size={14}/> Evidence-backed</span><span><CircleHelp size={14}/> Human review required</span></div></div><div className="hero-art"><div className="orbit orbit-a"/><div className="orbit orbit-b"/><div className="core"><BrainCircuit size={40}/></div><div className="orbit-node node-one"><Search size={17}/></div><div className="orbit-node node-two"><Target size={17}/></div><div className="orbit-node node-three"><CheckCircle2 size={17}/></div></div></section>
      <section className="metric-grid"><Metric icon={<Building2 size={18}/>} label="COMPANIES REVIEWED" value={results.length} note="Current run"/><Metric icon={<Target size={18}/>} label="POTENTIAL FITS" value={qualified} note="High + potential fit"/><Metric icon={<Activity size={18}/>} label="AVERAGE ICP SCORE" value={`${avg}/100`} note="Across reviewed leads"/><Metric icon={<ShieldCheck size={18}/>} label="EVIDENCE FIRST" value="100%" note="Citations shown when found"/></section>
      <section className="work-grid">
        <div className="panel input-panel" id="icp-panel"><div className="panel-heading"><div><div className="section-kicker">01 / INPUT</div><h2>Build your lead shortlist</h2><p>Enter company names and set the ideal customer profile.</p></div><div className="heading-icon"><UploadCloud size={20}/></div></div>
          <label className="field-label">COMPANY NAMES <span>Up to 25</span></label><textarea value={companies} onChange={e => setCompanies(e.target.value)} rows={4} placeholder={'One company per line\nExample: Acme Cloud'} />
          <label className="upload-link"><UploadCloud size={15}/> Import company list (.csv or .txt)<input type="file" accept=".csv,.txt" onChange={onFile}/></label>
          <div className="field-divider"/><div className="subheading"><Target size={16}/> Ideal Customer Profile <span>ICP</span></div>
          <label className="field-label">TARGET INDUSTRIES</label><input value={industries} onChange={e => setIndustries(e.target.value)} />
          <label className="field-label">TARGET GEOGRAPHIES</label><input value={geographies} onChange={e => setGeographies(e.target.value)} />
          <label className="field-label">SERVICES / NEED SIGNALS</label><input value={services} onChange={e => setServices(e.target.value)} />
          <label className="field-label">MINIMUM EMPLOYEE COUNT <b className="range-value">{minEmployees}+</b></label><input className="range" type="range" min="1" max="1000" step="25" value={minEmployees} onChange={e => setMinEmployees(e.target.value)}/><div className="range-labels"><span>Small team</span><span>Enterprise</span></div>
          <div className="toggle-row"><div><b>Live public web research</b><small>Search public pages for company evidence.</small></div><button className={`toggle ${live?'on':''}`} onClick={() => setLive(!live)} aria-label="Toggle live research"><span/></button></div>
          <button className="primary-button" onClick={runQualification} disabled={busy}>{busy ? <><LoaderCircle className="spin" size={17}/> Researching companies…</> : <><Sparkles size={17}/> Research & qualify leads <ChevronRight size={17}/></>}</button>
          {error && <div className="error-box">{error}</div>}<p className="privacy-note"><ShieldCheck size={14}/> Public sources only. No prospect outreach is sent.</p>
        </div>
        <div className="panel results-panel"><div className="panel-heading"><div><div className="section-kicker">02 / RESULTS</div><h2>Qualification overview</h2><p>Ranked by transparent fit score, not buying intent.</p></div><div className="heading-icon"><Activity size={20}/></div></div>
          <div className="results-toolbar"><div className="filter-wrap"><label>SHOW</label><select value={filter} onChange={e => setFilter(e.target.value)}><option>All leads</option><option>High fit</option><option>Potential fit</option><option>Low fit</option><option>Needs research</option></select></div><div className="export-actions"><button title="Export CSV" onClick={() => download('csv')} disabled={!results.length}><ArrowDownToLine size={15}/> CSV</button><button title="Export JSON" onClick={() => download('json')} disabled={!results.length}><ArrowDownToLine size={15}/> JSON</button></div></div>
          {!results.length && !busy ? <div className="empty-state"><div className="empty-icon"><Search size={27}/></div><h3>Your shortlist starts here</h3><p>Run research to see company fit scores, supporting sources, and what information still needs verification.</p><div className="empty-steps"><span><i>1</i> Research public signals</span><span><i>2</i> Score against your ICP</span><span><i>3</i> Review citations</span></div></div> : busy ? <div className="loading-state"><LoaderCircle className="spin" size={32}/><h3>Research agents are working</h3><p>Searching public web results and evaluating available evidence. This can take a little while.</p></div> : <div className="lead-list">{visibleResults.map((r, i) => <button key={r.company} className={`lead-row ${selected?.company===r.company?'selected':''}`} onClick={() => setSelected(r)}><div className="company-avatar">{r.company.slice(0,1).toUpperCase()}</div><div className="lead-info"><b>{r.company}</b><small>{r.industry} · {r.geography}</small><div className="mini-bar"><span style={{width:`${r.score}%`}}/></div></div><div className="lead-score"><strong>{r.score}</strong><small>/ 100</small></div><Tier tier={r.tier}/></button>)}</div>}
          {warnings.length > 0 && <div className="warning-box"><b>Research notes</b>{warnings.slice(0,4).map((w,i)=><p key={i}>• {w}</p>)}</div>}
        </div>
      </section>
      {selected && results.length > 0 && <section className="panel evidence-panel" id="evidence-panel"><div className="panel-heading"><div><div className="section-kicker">03 / EVIDENCE REVIEW</div><h2>{selected.company} <span className="muted-heading">qualification details</span></h2><p>Inspect the reasons, source links, and gaps before deciding whether to pursue this lead.</p></div><Tier tier={selected.tier}/></div>
        <div className="detail-grid"><div className="score-card"><span>ICP FIT SCORE</span><div className="big-score">{selected.score}<small>/100</small></div><div className="score-track"><span style={{width:`${selected.score}%`}}/></div><p>Confidence: <b>{selected.confidence}</b></p><div className="review-badge"><ShieldCheck size={14}/> Human review required</div></div><div className="detail-column"><h3><CheckCircle2 size={16}/> Scoring rationale</h3><ul className="rationale-list">{selected.rationale.map((x,i)=><li key={i}>{x}</li>)}</ul><h3 className="gap-heading"><CircleHelp size={16}/> Missing / uncertain information</h3>{selected.missing_information.length ? <ul className="missing-list">{selected.missing_information.map((x,i)=><li key={i}>{x}</li>)}</ul> : <p className="muted">No explicit gaps detected by this prototype; verify primary sources regardless.</p>}</div></div>
        <div className="source-header"><h3><FileSearch size={17}/> Supporting evidence</h3><span>{selected.evidence.length} source(s)</span></div>{selected.evidence.length ? <div className="source-list">{selected.evidence.map((e,i)=><article className="source-card" key={e.url}><div className="source-number">{String(i+1).padStart(2,'0')}</div><div className="source-content"><a href={e.url} target="_blank" rel="noreferrer">{e.title || e.url} <ExternalLink size={13}/></a><p>{e.snippet || 'No snippet provided by the search provider.'}</p><small>{e.source_domain || e.url}</small></div></article>)}</div> : <div className="no-evidence">No source evidence returned. Do not treat the score as a positive signal. Retry research or add a verified source.</div>}
      </section>}
      <footer><span>XDIGICS · AGENTIC AI ASSESSMENT PROTOTYPE</span><span>Explainable scores. Verifiable sources. Human decisions.</span></footer>
    </main>
  </div>;
}
function Metric({icon,label,value,note}) { return <div className="metric-card"><div className="metric-top"><span className="metric-icon">{icon}</span><span>{label}</span></div><strong>{value}</strong><small>{note}</small></div>; }
function Tier({tier}) { const cls = tier.toLowerCase().replaceAll(' ','-'); return <span className={`tier ${cls}`}>{tier}</span>; }
