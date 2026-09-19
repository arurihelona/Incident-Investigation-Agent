import React from 'react';
import { GitCommit, Search, CheckCircle2, Link2, AlertCircle, BarChart2 } from 'lucide-react';

export function InvestigationTimeline({ steps, metrics, isLoading }) {
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

      {metrics && (
        <div style={{
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '8px',
          padding: '0.75rem',
          marginBottom: '1rem',
          fontSize: '0.8rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
            <BarChart2 size={14} />
            <span>Investigation Statistics</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.35rem', color: 'var(--text-secondary)' }}>
            <div>Follow-up Searches: <strong style={{ color: 'var(--text-primary)' }}>{metrics.follow_up_searches}</strong></div>
            <div>Total Calls: <strong style={{ color: 'var(--text-primary)' }}>{metrics.total_retrieval_calls}</strong></div>
            <div>Hops: <strong style={{ color: 'var(--text-primary)' }}>{metrics.investigation_hops}</strong></div>
            <div>Unique Docs: <strong style={{ color: 'var(--text-primary)' }}>{metrics.unique_documents_retrieved}</strong></div>
            <div>Cycles Detected: <strong style={{ color: metrics.cycles_detected > 0 ? '#f59e0b' : 'var(--text-primary)' }}>{metrics.cycles_detected}</strong></div>
            <div>Max Hops: <strong style={{ color: 'var(--text-primary)' }}>{metrics.max_hop_limit}</strong></div>
          </div>
          <div style={{ marginTop: '0.5rem', paddingTop: '0.4rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <div style={{ color: 'var(--text-secondary)' }}>
              Status: <strong style={{ color: metrics.investigation_status === 'Completed' ? '#10b981' : '#f59e0b' }}>{metrics.investigation_status}</strong>
            </div>
            <div style={{ color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              Stop Reason: <span style={{ color: 'var(--text-primary)' }}>{metrics.stop_reason}</span>
            </div>
          </div>
        </div>
      )}

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
