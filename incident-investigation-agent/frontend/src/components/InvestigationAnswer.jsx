import React from 'react';
import { FileCheck, Calendar, GitCompare, Info, Clock, ArrowDown } from 'lucide-react';

export function InvestigationAnswer({
  answer,
  dateVersionAnalysis,
  similarVsIdentical,
  evidenceGap,
  timeline,
  isTimelineQuery
}) {
  // Utility to render text and format [DOC-ID] as chips
  const formatTextWithChips = (text) => {
    if (!text) return null;
    const parts = text.split(/(\[[A-Z0-9_-]+\])/g);
    return parts.map((part, i) => {
      if (/^\[[A-Z0-9_-]+\]$/.test(part)) {
        return (
          <span key={i} className="doc-chip">
            {part}
          </span>
        );
      }
      return part;
    });
  };

  // Extract core answer paragraphs from the answer text if it contains standard headers
  const getCleanAnswer = () => {
    if (!answer) return '';
    let mainText = answer;
    if (mainText.includes('Investigation Summary')) {
      // If structured with headers, extract the Answer: section
      const match = mainText.match(/Answer:\s*([\s\S]*?)(?=\n\n[A-Z][a-zA-Z\s\/]+:|$)/);
      if (match && match[1]) {
        return match[1].trim();
      }
    }
    return mainText;
  };

  const cleanAnswer = getCleanAnswer();

  return (
    <div className="card">
      <div className="card-title">
        <FileCheck size={18} />
        <span>Investigation Findings & Answer</span>
      </div>

      <div className="answer-body">
        {formatTextWithChips(cleanAnswer)}
      </div>

      {timeline && timeline.length > 0 && (
        <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#38bdf8', fontSize: '0.9rem', fontWeight: 600 }}>
              <Clock size={16} />
              <span>Chronological Event Timeline ({timeline.length} Events)</span>
            </div>
            {isTimelineQuery && (
              <span style={{ fontSize: '0.75rem', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', padding: '0.2rem 0.5rem', borderRadius: '4px', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
                Temporal Query Mode
              </span>
            )}
          </div>

          <div className="timeline-flow" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', position: 'relative' }}>
            {timeline.map((event, idx) => {
              const isDeployment = event.event_type?.includes('deploy') || event.event?.toLowerCase().includes('deploy');
              const isFailure = event.event_type?.includes('incident') || event.event?.toLowerCase().includes('spike') || event.event?.toLowerCase().includes('latency') || event.event?.toLowerCase().includes('fail');
              const isPostmortem = event.event_type === 'postmortem';

              let badgeColor = '#94a3b8';
              let badgeBg = 'rgba(148, 163, 184, 0.1)';
              let badgeLabel = event.event_type || 'Event';

              if (isDeployment) {
                badgeColor = '#60a5fa';
                badgeBg = 'rgba(59, 130, 246, 0.15)';
                badgeLabel = 'Deployment Event';
              } else if (isFailure) {
                badgeColor = '#f87171';
                badgeBg = 'rgba(239, 68, 68, 0.15)';
                badgeLabel = 'Incident / Latency Failure';
              } else if (isPostmortem) {
                badgeColor = '#c084fc';
                badgeBg = 'rgba(168, 85, 247, 0.15)';
                badgeLabel = 'Historical Postmortem';
              }

              return (
                <React.Fragment key={idx}>
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: `1px solid ${isFailure ? 'rgba(239, 68, 68, 0.3)' : isDeployment ? 'rgba(59, 130, 246, 0.3)' : 'var(--border-subtle)'}`,
                    borderRadius: '8px',
                    padding: '0.75rem 1rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.35rem'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{
                          fontFamily: 'var(--font-mono)',
                          fontWeight: 700,
                          fontSize: '0.85rem',
                          color: 'var(--text-primary)'
                        }}>
                          📅 {event.date}
                        </span>
                        {event.time && (
                          <span style={{
                            fontSize: '0.8rem',
                            color: '#fbbf24',
                            background: 'rgba(245, 158, 11, 0.1)',
                            padding: '0.1rem 0.4rem',
                            borderRadius: '4px',
                            fontFamily: 'var(--font-mono)'
                          }}>
                            ⏱ {event.time}
                          </span>
                        )}
                        <span className="doc-chip" style={{ marginLeft: 0 }}>
                          [{event.document_id}]
                        </span>
                      </div>
                      <span style={{
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        color: badgeColor,
                        background: badgeBg,
                        padding: '0.15rem 0.5rem',
                        borderRadius: '4px'
                      }}>
                        {badgeLabel}
                      </span>
                    </div>

                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      {formatTextWithChips(event.event)}
                    </div>

                    {(event.service || event.version) && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        Target: {event.service || 'N/A'} {event.version ? `(${event.version})` : ''}
                      </div>
                    )}
                  </div>

                  {idx < timeline.length - 1 && (
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', color: 'var(--text-muted)', padding: '0.1rem 0' }}>
                      <ArrowDown size={14} />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      )}

      {evidenceGap && evidenceGap.length > 0 && (
        <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#f87171', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem' }}>
            <Info size={15} />
            <span>Evidence Gap & Investigation Boundaries</span>
          </div>
          <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            {evidenceGap.map((gap, i) => (
              <li key={i}>{formatTextWithChips(gap)}</li>
            ))}
          </ul>
        </div>
      )}

      {dateVersionAnalysis && dateVersionAnalysis !== 'N/A' && (
        <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#93c5fd', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem' }}>
            <Calendar size={15} />
            <span>Date & Version Reasoning</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            {formatTextWithChips(dateVersionAnalysis)}
          </p>
        </div>
      )}

      {similarVsIdentical && (
        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#a78bfa', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem' }}>
            <GitCompare size={15} />
            <span>Similar vs. Identical Incident Evaluation</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            {formatTextWithChips(similarVsIdentical.explanation)}
          </p>
        </div>
      )}
    </div>
  );
}

