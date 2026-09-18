import React from 'react';
import { GitCommit, Search, CheckCircle2, Link2, AlertCircle } from 'lucide-react';

export function InvestigationTimeline({ steps, isLoading }) {
  if (!steps || steps.length === 0) {
    if (isLoading) {
      return (
        <div className="card">
          <div className="card-title">
            <Search size={18} className="spin" />
            <span>Agent Investigation Trail</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Investigating internal documents across multiple hops...
          </p>
        </div>
      );
    }
    return null;
  }

  const getStepIcon = (action) => {
    switch (action) {
      case 'initial_search':
      case 'follow_up_search':
        return <Search size={12} />;
      case 'fact_extracted':
        return <CheckCircle2 size={12} />;
      case 'evidence_connected':
        return <Link2 size={12} />;
      case 'evidence_reviewed':
        return <AlertCircle size={12} />;
      default:
        return <GitCommit size={12} />;
    }
  };

  return (
    <div className="card">
      <div className="card-title">
        <GitCommit size={18} />
        <span>Investigation Trail ({steps.length} Steps)</span>
      </div>

      <div className="timeline-list">
        {steps.map((s) => (
          <div key={s.step} className="timeline-item">
            <div className="timeline-icon">
              {getStepIcon(s.action)}
            </div>
            <div className="timeline-content">
              <div className="timeline-action">
                Step {s.step}: {s.action.replace(/_/g, ' ')}
              </div>
              {s.query && (
                <div className="timeline-query">
                  Query: {s.query}
                </div>
              )}
              <div className="timeline-desc">
                {s.description}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
