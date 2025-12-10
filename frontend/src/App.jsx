import React, { useState, useRef } from "react";
import Header from "./components/Header";
import Footer from "./components/Footer";

/* ---------- helpers ---------- */
function filesize(n) {
  if (!n && n !== 0) return "";
  const units = ["B","KB","MB","GB"];
  let i = 0;
  while (n >= 1024 && i < units.length-1) { n /= 1024; i++; }
  return `${Math.round(n*10)/10} ${units[i]}`;
}

function ScoreBar({score}) {
  const color = score >= 80 ? "bar--green" : score >= 50 ? "bar--orange" : "bar--red";
  return (
    <div className="scorebar" aria-hidden>
      <div className={`bar ${color}`} style={{width: `${Math.max(0, Math.min(100, score))}%`}} />
      <div className="score-label">{Math.round((score||0)*100)/100}%</div>
    </div>
  );
}

/* ---------- App ---------- */
export default function App(){
  const [files, setFiles] = useState([]);
  const [jobDesc, setJobDesc] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef();

  const onFilesSelected = (fileList) => {
    const arr = Array.from(fileList).filter(f => f.type === "application/pdf");
    // dedupe by name+size
    const uniq = [];
    const seen = new Set();
    for (const f of arr) {
      const key = `${f.name}::${f.size}`;
      if (!seen.has(key)) { seen.add(key); uniq.push(f); }
    }
    setFiles(uniq);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    onFilesSelected(e.dataTransfer.files);
  };

  const handlePick = (e) => onFilesSelected(e.target.files);

  const buildFormData = () => {
    const fd = new FormData();
    fd.append('job_description', jobDesc);
    for (const f of files) fd.append('files', f);
    return fd;
  };

  const onSubmit = async (e) => {
    e && e.preventDefault();
    if (!jobDesc.trim()) return alert("Please paste the job description");
    if (!files.length) return alert("Please select at least one PDF file");
    setLoading(true);
    setResults(null);
    try {
      const fd = buildFormData();
      // relative path so dev proxy or same-origin works
      const res = await fetch('/api/upload/', { method: 'POST', body: fd });
      const contentType = res.headers.get('content-type') || "";
      if (!res.ok) {
        const txt = contentType.includes('application/json') ? await res.json() : await res.text();
        const msg = typeof txt === 'string' ? txt : JSON.stringify(txt);
        throw new Error(msg);
      }
      const data = contentType.includes('application/json') ? await res.json() : null;
      setResults(data);
      setTimeout(()=> document.getElementById('results')?.scrollIntoView({behavior:'smooth'}), 150);
    } catch (err) {
      console.error(err);
      alert("Upload failed: " + (err.message || err));
    } finally {
      setLoading(false);
    }
  };

  const onUpdate = async () => {
    if (!results) return alert('No previous analysis to update. Use Upload first.');
    await onSubmit();
  };

  const clearAll = () => { setFiles([]); setResults(null); setJobDesc(""); }

  return (
    <div className="app">
      <Header onOpenDocs={() => window.open('https://example.com/docs','_blank')} />

      <main className="main" role="main">
        <section className="panel left" aria-label="Controls">
          <form onSubmit={onSubmit} className="form">
            <label className="label">Job description</label>
            <textarea
              placeholder="Paste the job description (plain text recommended)"
              value={jobDesc}
              onChange={e=>setJobDesc(e.target.value)}
              rows={8}
              className="input textarea"
            />

            <label className="label" style={{marginTop:12}}>Resumes (PDF)</label>

            <div
              className={`dropzone ${dragOver ? 'dropzone--over' : ''}`}
              onDragOver={(e)=>{ e.preventDefault(); setDragOver(true); }}
              onDragLeave={()=>setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => inputRef.current.click()}
              role="button"
              tabIndex={0}
              aria-label="Drop PDF resumes here or click to select"
            >
              <input
                ref={inputRef}
                type="file"
                accept="application/pdf"
                multiple
                onChange={handlePick}
                style={{display:'none'}}
              />
              <div>
                <strong>Drag & drop PDFs here</strong>
                <div className="muted">or click to select</div>
              </div>
            </div>

            <div className="file-chips" aria-live="polite">
              {files.length === 0 && <div className="muted">No files selected</div>}
              {files.map(f => (
                <div key={f.name + f.size} className="chip" title={f.name}>
                  <div className="chip-title">{f.name}</div>
                  <div className="chip-sub">{filesize(f.size)}</div>
                </div>
              ))}
            </div>

            <div className="actions" style={{marginTop:14}}>
              <button className="btn primary" type="submit" disabled={loading}>
                {loading ? "Analyzing..." : "Upload & Analyze"}
              </button>
              <button type="button" className="btn" onClick={onUpdate} disabled={loading || !results}>
                Update
              </button>
              <button type="button" className="btn ghost" onClick={clearAll}>
                Clear
              </button>
            </div>
          </form>

          <aside className="panel help" aria-hidden>
            <h3>Tips for better matching</h3>
            <ul>
              <li>Use plain-text / bullet-resumes (avoid tables & heavy graphics)</li>
              <li>Include contact fields: Name, Email, Phone, LinkedIn/GitHub</li>
              <li>Make skills and experience easy to find (Skills, Experience, Education headers)</li>
            </ul>
          </aside>
        </section>

        <section className="panel right" id="results" aria-live="polite">
          {results ? (
            <>
              <div className="results-header">
                <h2>Results</h2>
                <div className="muted small">Keywords: {results.keywords?.slice(0,40).join(', ')}</div>
              </div>

              <div className="results-list">
                {results.results.map((r) => (
                  <article key={r.filename} className="result-card" aria-labelledby={r.filename}>
                    <div className="result-left">
                      <div className="result-title" id={r.filename}>{r.filename}</div>
                      <div className="badges" aria-hidden>
                        {r.parsed?.contacts?.emails?.length ? <span className="badge">Email</span> : <span className="badge badge--muted">No Email</span>}
                        {r.parsed?.contacts?.phones?.length ? <span className="badge">Phone</span> : <span className="badge badge--muted">No Phone</span>}
                        {(r.parsed?.contacts?.linkedin?.length || r.parsed?.contacts?.github?.length) ? <span className="badge">Links</span> : <span className="badge badge--muted">No Links</span>}
                      </div>

                      <div className="meta small" style={{marginTop:6}}>
                        <div>Matches: {r.parsed?.matches?.length || 0} / {results.keywords?.length || 0}</div>
                        <div>Contact: {r.parsed?.contacts?.name || <span className="muted">Unknown</span>}</div>
                      </div>
                    </div>

                    <div className="result-right">
                      <ScoreBar score={r.score || 0} />
                      <div className="card-actions">
                        <button className="btn small" onClick={()=>setPreview({filename: r.filename, text: r.excerpt || r.parsed?.contacts?.name || 'No preview available'})}>
                          Preview
                        </button>
                        <a className="btn small ghost" href="#" onClick={(e)=>{ e.preventDefault(); alert('Download not implemented'); }}>
                          Download
                        </a>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </>
          ) : (
            <div className="empty">
              <h3>No results yet</h3>
              <p className="muted">Upload resumes to see ranked results here.</p>
            </div>
          )}
        </section>
      </main>

      {/* Preview modal */}
      {preview && (
        <div className="modal" onClick={() => setPreview(null)} role="dialog" aria-modal="true">
          <div className="modal-body" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <strong>{preview.filename}</strong>
              <button className="btn small ghost" onClick={() => setPreview(null)}>Close</button>
            </div>
            <pre className="preview-text">{preview.text}</pre>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
}
