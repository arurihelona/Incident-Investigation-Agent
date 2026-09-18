import React from 'react';
import { AlertTriangle, ArrowRight, ShieldCheck } from 'lucide-react';

export function ContradictionCard({ contradictions }) {
  if (!contradictions || contradictions.length === 0) return null;

  return (
    <div className="contradiction-box">
      <div className="contradiction-header">
        <AlertTriangle size={18} />
        <span>Contradiction / Outdated Guidance Detected</span>
      </div>

      {contradictions.map((c, idx) => {
        const isDocBNewer = c.newer_doc_id === c.doc_b.document_id;
        const olderDoc = isDocBNewer ? c.doc_a : c.doc_b;
        const newerDoc = isDocBNewer ? c.doc_b : c.doc_a;

        return (
          <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div className="contradiction-compare">
              <div className="compare-doc">
                <div className="compare-doc-header">
                  <span className="doc-chip">{olderDoc.document_id}</span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    Older ({olderDoc.date} | {olderDoc.version})
                  </span>
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#f3f4f6', marginBottom: '0.25rem' }}>
                  {olderDoc.title}
                </div>
                <div className="compare-guidance">
                  "{olderDoc.guidance}"
                </div>
              </div>

              <div className="compare-doc newer">
                <div className="compare-doc-header">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <span className="doc-chip" style={{ color: '#34d399', background: 'rgba(16, 185, 129, 0.15)', borderColor: 'rgba(16, 185, 129, 0.3)' }}>
                      {newerDoc.document_id}
                    </span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--accent-green)', fontWeight: 600 }}>
                      [Newer Guidance]
                    </span>
                  </div>
                  <span style={{ fontSize: '0.72rem', color: '#34d399' }}>
                    {newerDoc.date} | {newerDoc.version}
                  </span>
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#f3f4f6', marginBottom: '0.25rem' }}>
                  {newerDoc.title}
                </div>
                <div className="compare-guidance">
                  "{newerDoc.guidance}"
                </div>
              </div>
            </div>

            <div style={{ fontSize: '0.86rem', color: '#fef3c7', lineHeight: 1.45, background: 'rgba(0,0,0,0.2)', padding: '0.6rem 0.8rem', borderRadius: '6px' }}>
              <strong>Operational Directive: </strong>
              {c.explanation}
            </div>
          </div>
        );
      })}
    </div>
  );
}
