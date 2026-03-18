import React, { useState } from 'react';
import './PredictionPanel.css';

/**
 * PredictionPanel component
 * Displays predicted exam questions and document analysis
 */
function PredictionPanel({
    questions,
    questionAnalysis,
    isLoading,
    onPredict,
    onAnalyze,
}) {
    const [selectedDifficulty, setSelectedDifficulty] = useState('medium');
    const [groupBy, setGroupBy] = useState('topic');

    return (
        <div className="prediction-panel">
            <div className="prediction-controls">
                <div className="control-group">
                    <label>Difficulty Level:</label>
                    <select
                        value={selectedDifficulty}
                        onChange={(e) => setSelectedDifficulty(e.target.value)}
                        disabled={isLoading}
                    >
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                    </select>
                    <button
                        className="predict-btn"
                        onClick={() => onPredict(selectedDifficulty)}
                        disabled={isLoading}
                    >
                        {isLoading ? '⏳ Generating...' : '❓ Generate Questions'}
                    </button>
                </div>

                <div className="control-group">
                    <label>Group By:</label>
                    <select
                        value={groupBy}
                        onChange={(e) => setGroupBy(e.target.value)}
                        disabled={isLoading}
                    >
                        <option value="topic">Topic</option>
                        <option value="difficulty">Difficulty</option>
                        <option value="type">Question Type</option>
                    </select>
                    <button
                        className="analyze-btn"
                        onClick={() => onAnalyze(groupBy)}
                        disabled={isLoading}
                    >
                        {isLoading ? '⏳ Analyzing...' : '📊 Analyze'}
                    </button>
                </div>
            </div>

            {questions.length > 0 && (
                <div className="questions-section">
                    <h4>Generated Questions ({questions.length})</h4>
                    <div className="questions-list">
                        {questions.map((q, idx) => (
                            <div key={idx} className="question-card">
                                <div className="question-header">
                                    <span className="question-num">Q{idx + 1}</span>
                                    <span className="question-difficulty">
                                        {q.difficulty && `[${q.difficulty.toUpperCase()}]`}
                                    </span>
                                </div>
                                <div className="question-text">{q.question}</div>
                                {q.options && (
                                    <div className="question-options">
                                        {q.options.map((opt, oidx) => (
                                            <div key={oidx} className="option">
                                                {String.fromCharCode(65 + oidx)}) {opt}
                                            </div>
                                        ))}
                                    </div>
                                )}
                                {q.answer && (
                                    <div className="question-answer">
                                        <strong>Answer:</strong> {q.answer}
                                    </div>
                                )}
                                {q.explanation && (
                                    <div className="question-explanation">
                                        <strong>Why:</strong> {q.explanation}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {questionAnalysis && (
                <div className="analysis-section">
                    <h4>Document Analysis</h4>
                    <div className="analysis-groups">
                        {Object.entries(questionAnalysis.groups || {}).map(([group, data]) => (
                            <div key={group} className="analysis-group">
                                <h5>{group}</h5>
                                <div className="group-stats">
                                    <span className="stat">
                                        Questions: {data.question_count || 0}
                                    </span>
                                    <span className="stat">
                                        Avg Difficulty: {(data.avg_difficulty || 0).toFixed(1)}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {questions.length === 0 && !questionAnalysis && (
                <div className="empty-state">
                    <p>No questions generated yet.</p>
                    <p>Click "Generate Questions" to create exam questions from the document.</p>
                </div>
            )}
        </div>
    );
}

export default PredictionPanel;
