import React from 'react';
import { Network, ArrowRight } from 'lucide-react';

export function EvidenceConnectionGraph({ links }) {
  if (!links || links.length === 0) return null;

  return (
    <div className="card">
      <div className="card-title">
        <Network size={18} />
        <span>Evidence Relationships ({links.length} Link{links.length > 1 ? 's' : ''})</span>
      </div>

      <div className="evidence-chain">
        {links.map((link, idx) => (
          <div key={idx} className="chain-item">
            <span className="chain-source">{link.source_id}</span>
            <ArrowRight size={14} className="chain-arrow" />
            <span className="chain-target">{link.target_id}</span>
            <span className="chain-desc">{link.description}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
