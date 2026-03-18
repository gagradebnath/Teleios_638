import React from 'react';
import ChatPanel from './ChatPanel';
import IngestPanel from './IngestPanel';
import PredictionPanel from './PredictionPanel';
import ExecutionPanel from './ExecutionPanel';
import './RightPanel.css';

/**
 * RightPanel component
 * Routes to appropriate panel based on activePanel prop
 */
function RightPanel({
    activePanel,
    chatHistory,
    questions,
    questionAnalysis,
    executionOutput,
    executionError,
    isLoading,
    onFileSelected,
    onExplain,
    onPredict,
    onExecute,
    onAnalyze,
}) {
    switch (activePanel) {
        case 'chat':
            return (
                <ChatPanel
                    chatHistory={chatHistory}
                    isLoading={isLoading}
                    onExplain={onExplain}
                />
            );
        case 'ingest':
            return (
                <IngestPanel
                    isLoading={isLoading}
                    onFileSelected={onFileSelected}
                />
            );
        case 'predict':
            return (
                <PredictionPanel
                    questions={questions}
                    questionAnalysis={questionAnalysis}
                    isLoading={isLoading}
                    onPredict={onPredict}
                    onAnalyze={onAnalyze}
                />
            );
        case 'execute':
            return (
                <ExecutionPanel
                    output={executionOutput}
                    error={executionError}
                    isLoading={isLoading}
                    onExecute={onExecute}
                />
            );
        default:
            return <ChatPanel chatHistory={chatHistory} isLoading={isLoading} onExplain={onExplain} />;
    }
}

export default RightPanel;
