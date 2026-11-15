import { useEffect, useState } from "react";
import * as api from "./api.js";

const FIELDS = [
  ["age", "Age (years)"],
  ["sleep_hours", "Sleep per night (hours)"],
  ["active_minutes_week", "Active minutes per week"],
  ["strength_days_week", "Muscle-strengthening days per week"],
  ["sitting_hours_day", "Sitting hours per day"],
  ["screen_hours_day", "Recreational screen hours per day"],
];

function ConsentScreen({ onAccept }) {
  const [checked, setChecked] = useState(false);
  return (
    <div className="card">
      <h2>Before you start</h2>
      <p>HealthAssist gives <b>general wellness information</b> from Canadian and WHO guidance. It is not medical advice and cannot diagnose anything.</p>
      <ul>
        <li>All profile fields are optional. Only lifestyle habits are asked for.</li>
        <li>Your data is encrypted and stays on this computer. The AI model also runs locally.</li>
        <li>You can edit your profile or delete all your data at any time.</li>
      </ul>
      <label><input type="checkbox" checked={checked} onChange={(e) => setChecked(e.target.checked)} /> I understand and agree</label>
      <br />
      <button disabled={!checked} onClick={onAccept}>Continue</button>
    </div>
  );
}

function ProfileForm({ profile, onSaved }) {
  const [form, setForm] = useState(profile || {});
  const change = (k, v) => setForm({ ...form, [k]: v === "" ? undefined : Number(v) });
  const save = async () => onSaved(await api.saveProfile(form));
  return (
    <div className="card">
      <h2>My habits (optional)</h2>
      {FIELDS.map(([key, label]) => (
        <label key={key} className="field">{label}
          <input type="number" step="0.5" value={form[key] ?? ""} onChange={(e) => change(key, e.target.value)} />
        </label>
      ))}
      <button onClick={save}>Save profile</button>
    </div>
  );
}

function Comparison({ rows }) {
  if (!rows.length) return null;
  return (
    <div className="card">
      <h3>How my habits compare</h3>
      {rows.map((r) => <p key={r.topic} className={`status ${r.status}`}><b>{r.topic}:</b> {r.message}</p>)}
    </div>
  );
}

function Chat({ refreshHistory }) {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [rated, setRated] = useState(false);
  const [model, setModel] = useState("llama3.1:8b");

  const send = async () => {
    setBusy(true); setRated(false);
    try { setResult(await api.askQuestion(text, model)); refreshHistory(); }
    catch (e) { setResult({ answer: e.message, sources: [] }); }
    setBusy(false);
  };
  const rate = async (n) => { await api.sendFeedback(result.history_id, n); setRated(true); };

  return (
    <div className="card">
      <h2>Ask a question</h2>
      <textarea rows="3" value={text} onChange={(e) => setText(e.target.value)} placeholder="e.g. How many hours of sleep do adults need?" />
      <label className="field">Local model
        <select value={model} onChange={(e) => setModel(e.target.value)}>
          <option value="llama3.1:8b">Llama 3.1 8B</option>
          <option value="gemma2:9b">Gemma 2 9B</option>
        </select>
      </label>
      <button disabled={busy || text.length < 3} onClick={send}>{busy ? "Thinking... (the local model can take a little while)" : "Ask"}</button>
      {result && (
        <div className={`answer ${result.outcome}`}>
          <p style={{ whiteSpace: "pre-wrap" }}>{result.answer}</p>
          {result.sources?.length > 0 && (
            <div><b>Sources</b>
              <ul>{result.sources.map((s) => <li key={s.url}><a href={s.url} target="_blank" rel="noreferrer">{s.title}</a> ({s.org})</li>)}</ul>
            </div>
          )}
          {result.history_id && (rated ? <small>Thanks for the feedback!</small> :
            <small>Was this helpful? {[1, 2, 3, 4, 5].map((n) => <button key={n} className="star" onClick={() => rate(n)}>{n}</button>)}</small>)}
        </div>
      )}
    </div>
  );
}

function History({ items }) {
  return (
    <div className="card">
      <h3>History</h3>
      {items.length === 0 && <p>No questions yet.</p>}
      {items.map((h) => (
        <details key={h.id}><summary>{h.question}</summary><p style={{ whiteSpace: "pre-wrap" }}>{h.answer}</p></details>
      ))}
    </div>
  );
}

export default function App() {
  const [consented, setConsented] = useState(null);
  const [profile, setProfile] = useState(null);
  const [comparison, setComparison] = useState([]);
  const [history, setHistory] = useState([]);

  const loadAll = async () => {
    const p = await api.getProfile();
    setProfile(p.profile); setComparison(p.comparison);
    setHistory(await api.getHistory());
  };
  useEffect(() => { api.getConsent().then((c) => { setConsented(c.accepted); if (c.accepted) loadAll(); }); }, []);

  const accept = async () => { await api.acceptConsent(); setConsented(true); loadAll(); };
  const wipe = async () => {
    if (!confirm("Delete your consent, profile, history and feedback?")) return;
    await api.deleteMyData();
    setConsented(false); setProfile(null); setComparison([]); setHistory([]);
  };

  if (consented === null) return <p>Loading...</p>;
  return (
    <div className="page">
      <header><h1>HealthAssist</h1><small>General wellness information. Not medical advice. In an emergency call 9-1-1.</small></header>
      {!consented ? <ConsentScreen onAccept={accept} /> : (
        <>
          <ProfileForm key={profile ? "saved" : "empty"} profile={profile} onSaved={(r) => { setProfile(r.profile); setComparison(r.comparison); }} />
          <Comparison rows={comparison} />
          <Chat refreshHistory={async () => setHistory(await api.getHistory())} />
          <History items={history} />
          <button className="danger" onClick={wipe}>Delete all my data</button>
        </>
      )}
    </div>
  );
}
