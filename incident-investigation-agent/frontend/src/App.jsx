import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { QuestionInput } from './components/QuestionInput';
import { InvestigationTimeline } from './components/InvestigationTimeline';
import { EvidenceSufficiencyBadge } from './components/EvidenceSufficiencyBadge';
import { InvestigationAnswer } from './components/InvestigationAnswer';
import { EvidenceConnectionGraph } from './components/EvidenceConnectionGraph';
import { ContradictionCard } from './components/ContradictionCard';
import { EvidenceList } from './components/EvidenceList';
import { DocumentCatalogModal } from './components/DocumentCatalogModal';
import { checkHealth, getDocuments, reindexDocuments, runInvestigation } from './services/api';
import { AlertCircle } from 'lucide-react';

export default function App() {
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const [health, setHealth] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [isCatalogOpen, setIsCatalogOpen] = useState(false);
  const [isReindexing, setIsReindexing] = useState(false);

  useEffect(() => {
    loadSystemInfo();
  }, []);

  const loadSystemInfo = async () => {
    try {
      const [hData, dData] = await Promise.all([checkHealth(), getDocuments()]);
      setHealth(hData);
      setDocuments(dData.documents || []);
    } catch (err) {
      console.warn('Backend not yet reachable on initial load:', err.message);
    }
  };

  const handleReindex = async () => {
    setIsReindexing(true);
    try {
      await reindexDocuments();
      await loadSystemInfo();
    } catch (err) {
      setError(`Reindexing error: ${err.message}`);
    } finally {
      setIsReindexing(false);
    }
  };

  const handleInvestigate = async (queryText) => {
    if (!queryText) return;
    setIsLoading(true);
    setError(null);
    try {
      const resp = await runInvestigation(queryText);
      setResult(resp);
    } catch (err) {
      setError(
        `Investigation could not be completed.\nReason: ${err.message || 'The AI investigation service is unavailable.'}\nPlease check the configured service or retry.`
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header
        health={health}
        onOpenCatalog={() => setIsCatalogOpen(true)}
        onReindex={handleReindex}
        isReindexing={isReindexing}
      />

      <QuestionInput
        question={question}
        setQuestion={setQuestion}
        onInvestigate={handleInvestigate}
        isLoading={isLoading}
      />

      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '1rem',
          color: '#f87171',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.6rem'
        }}>
          <AlertCircle size={18} style={{ marginTop: '2px', flexShrink: 0 }} />
          <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem' }}>{error}</div>
        </div>
      )}

      {result && (
        <div className="results-grid">
          <main className="main-results">
            <EvidenceSufficiencyBadge
              status={result.evidence_status}
              uncertainty={result.uncertainty}
            />

            <InvestigationAnswer
              answer={result.answer}
              dateVersionAnalysis={result.date_version_analysis}
              similarVsIdentical={result.similar_vs_identical}
            />

            <ContradictionCard
              contradictions={result.contradictions}
            />

            <EvidenceConnectionGraph
              links={result.evidence_links}
            />

            <EvidenceList
              evidence={result.evidence}
            />
          </main>

          <aside className="sidebar-column">
            <InvestigationTimeline
              steps={result.investigation_steps}
              isLoading={isLoading}
            />
          </aside>
        </div>
      )}

      <DocumentCatalogModal
        isOpen={isCatalogOpen}
        onClose={() => setIsCatalogOpen(false)}
        documents={documents}
      />
    </div>
  );
}
