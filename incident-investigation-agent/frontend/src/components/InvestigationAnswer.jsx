import React from 'react';
import { FileCheck, Calendar, GitCompare, Info } from 'lucide-react';

export function InvestigationAnswer({ answer, dateVersionAnalysis, similarVsIdentical }) {
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
