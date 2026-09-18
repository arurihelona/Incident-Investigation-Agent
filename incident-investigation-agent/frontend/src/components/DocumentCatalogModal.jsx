import React from 'react';
import { X, FileText, Database } from 'lucide-react';

export function DocumentCatalogModal({ isOpen, onClose, documents }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Database size={20} color="#3b82f6" />
            <h2 className="modal-title">Internal Incident & Operational Document Store</h2>
          </div>
          <button className="btn-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            The internal document store contains incident reports, postmortems, deployment notes, and runbooks.
            The agent autonomously queries and evaluates these documents during investigations.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {documents.map((doc) => (
              <div key={doc.document_id} className="doc-card" style={{ background: 'var(--bg-primary)' }}>
                <div className="doc-card-top">
                  <span className="doc-card-id">{doc.document_id}</span>
                  <div className="doc-card-badges">
                    <span className="meta-pill">{doc.type}</span>
                    {doc.service && <span className="meta-pill">{doc.service}</span>}
                    <span className="meta-pill">{doc.version}</span>
                    <span className="meta-pill">{doc.date}</span>
                  </div>
                </div>
                <div className="doc-card-title">{doc.title}</div>
                <div className="doc-card-body">{doc.content}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
