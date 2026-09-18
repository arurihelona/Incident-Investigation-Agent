import React from 'react';
import { ShieldAlert, Database, RefreshCw, FileText } from 'lucide-react';

export function Header({ health, onOpenCatalog, onReindex, isReindexing }) {
  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-icon">
          <ShieldAlert size={22} />
        </div>
        <div>
          <h1 className="brand-title">Incident Investigation Agent</h1>
          <p className="brand-subtitle">Evidence-driven operational incident analysis</p>
        </div>
      </div>

      <div className="header-actions">
        <div className="status-badge" title="Vector Database & System Health">
          <span className="status-dot"></span>
          <span>
            ChromaDB Active | {health?.documents_indexed ?? 7} Docs
          </span>
        </div>

        <button
          className="btn-secondary"
          onClick={onOpenCatalog}
          title="Browse internal incident & deployment documents"
        >
          <FileText size={15} />
          <span>Internal Documents</span>
        </button>

        <button
          className="btn-secondary"
          onClick={onReindex}
          disabled={isReindexing}
          title="Reindex ChromaDB vector store"
        >
          <RefreshCw size={15} className={isReindexing ? 'spin' : ''} />
          <span>{isReindexing ? 'Reindexing...' : 'Sync Index'}</span>
        </button>
      </div>
    </header>
  );
}
