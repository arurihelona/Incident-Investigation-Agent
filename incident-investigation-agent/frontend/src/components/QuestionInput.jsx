import React from 'react';
import { Search, Sparkles } from 'lucide-react';

const PRESETS = [
  {
    id: 'test-a',
    tag: 'Demo 1: Deployment Investigation',
    tagClass: 'test-a',
    question: 'Why did the Order API become slow on September 16? Check whether the deployment was related and whether we have seen this before.',
    description: 'Triggers multi-hop retrieval: INC-1042 ➔ orders-api v2.8.1 ➔ DEP-882 ➔ PM-211.'
  },
  {
    id: 'test-b',
    tag: 'Demo 2: Contradictory Guidance',
    tagClass: 'test-b',
    question: 'The service is failing after a deployment. What should the on-call engineer do first?',
    description: 'Detects contradiction: older GUIDE-12 (v1) vs superseding GUIDE-41 (v3).'
  },
  {
    id: 'test-c',
    tag: 'Demo 3: Insufficient Evidence',
    tagClass: 'test-c',
    question: 'Did this exact failure happen before?',
    description: 'Evaluates disparate incidents (INC-300 vs INC-301) and flags Insufficient Evidence.'
  }
];

export function QuestionInput({ question, setQuestion, onInvestigate, isLoading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim()) {
      onInvestigate(question.trim());
    }
  };

  const handleSelectPreset = (presetQuestion) => {
    setQuestion(presetQuestion);
    onInvestigate(presetQuestion);
  };

  return (
    <section className="input-section">
      <form onSubmit={handleSubmit} className="query-box">
        <div className="query-input-row">
          <textarea
            className="query-textarea"
            placeholder="Ask an operational investigation question (e.g. 'Why did the Order API become slow on September 16?')"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            rows={2}
          />
          <button
            type="submit"
            className="btn-investigate"
            disabled={isLoading || !question.trim()}
          >
            <Search size={17} />
            <span>{isLoading ? 'Investigating...' : 'Investigate'}</span>
          </button>
        </div>
      </form>

      <div className="presets-container">
        <div className="presets-label">Select Demo Scenario:</div>
        <div className="preset-cards">
          {PRESETS.map((p) => (
            <button
              key={p.id}
              className="preset-card"
              onClick={() => handleSelectPreset(p.question)}
              disabled={isLoading}
            >
              <span className={`preset-tag ${p.tagClass}`}>{p.tag}</span>
              <span className="preset-text">{p.question}</span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
