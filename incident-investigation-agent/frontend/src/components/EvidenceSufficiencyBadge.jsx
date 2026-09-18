import React from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';

export function EvidenceSufficiencyBadge({ status, uncertainty }) {
  const isSufficient = status?.toLowerCase() === 'sufficient';

  return (
    <div className={`sufficiency-banner ${isSufficient ? 'sufficient' : 'insufficient'}`}>
      <div className="sufficiency-badge-tag">
        {isSufficient ? 'Status: Sufficient' : 'Status: Insufficient'}
      </div>
      <div className="sufficiency-content">
        <strong>
          {isSufficient ? 'Evidence Grounded Conclusion' : 'Insufficient Evidence Notice'}
        </strong>
        <p>{uncertainty}</p>
      </div>
    </div>
  );
}
