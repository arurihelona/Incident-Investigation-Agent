import React from 'react';
import { Database, FileText } from 'lucide-react';

export function EvidenceList({ evidence }) {
  if (!evidence || evidence.length === 0) return null;

  return (
    <div className="card">
      <div className="card-title">
        <Database size={18} />
        <span>Retrieved Evidence Records ({evidence.length})</span>
      </div>

      <div className="evidence-grid">
        {evidence.map((doc) => (
          <div key={doc.document_id} className="doc-card" id={`evidence-${doc.document_id}`}>
            <div className="doc-card-top">
              <span className="doc-card-id">{doc.document_id}</span>
              <div className="doc-card-badges">
                <span className="meta-pill">{doc.type}</span>
                {doc.service && <span className="meta-pill">{doc.service}</span>}
                <span className="meta-pill">{doc.version}</span>
                <span className="meta-pill">{doc.date}</span>
                {doc.relevance_score !== undefined && (
                  <span className="meta-pill" style={{ color: '#34d399' }}>
                    {(doc.relevance_score * 100).toFixed(0)}% Match
                  </span>
                )}
              </div>
            </div>
            <div className="doc-card-title">{doc.title}</div>
            <div className="doc-card-body">{doc.content}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
