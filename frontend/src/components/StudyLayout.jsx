import React from 'react';
import LeftPanel from './LeftPanel';
import RightPanel from './RightPanel';
import TabBar from './TabBar';
import '../styles/components/StudyLayout.css';

/**
 * StudyLayout component
 * Implements 50/50 CSS Grid split layout:
 * - Left: PDF viewer
 * - Right: Interactive panels (Chat, Predict, Execute, Ingest)
 */
function StudyLayout({
    // Course context
    selectedCourse,
    
    // PDF viewer props
    pdfFile,
    documentName,
    onTextHighlighted,

    // Panel props
    activePanel,
    onPanelChange,

    // Data props
    chatHistory,
    questions,
    questionAnalysis,
    executionOutput,
    executionError,
    isLoading,

    // Callbacks
    onFileSelected,
    onExplain,
    onPredict,
    onExecute,
    onAnalyze,
    documents,
}) {
    return (
        <div className="study-layout-container">
            {/* Left Panel: PDF Viewer */}
            <div className="layout-left">
                <LeftPanel
                    pdfFile={pdfFile}
                    documentName={documentName}
                    onTextHighlighted={onTextHighlighted}
                    documents={documents}
                />
            </div>

            {/* Divider */}
            <div className="layout-divider" />

            {/* Right Panel: Interactive Components */}
            <div className="layout-right">
                {/* Tab navigation */}
                <TabBar activeTab={activePanel} onTabChange={onPanelChange} />

                {/* Tab content */}
                <div className="tab-content">
                    <RightPanel
                        activePanel={activePanel}
                        chatHistory={chatHistory}
                        questions={questions}
                        questionAnalysis={questionAnalysis}
                        executionOutput={executionOutput}
                        executionError={executionError}
                        isLoading={isLoading}
                        onFileSelected={onFileSelected}
                        onExplain={onExplain}
                        onPredict={onPredict}
                        onExecute={onExecute}
                        onAnalyze={onAnalyze}
                        selectedCourse={selectedCourse}
                    />
                </div>
            </div>
        </div>
    );
}

export default StudyLayout;
