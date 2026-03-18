import React, { useState, useCallback, useRef } from 'react';
import StudyLayout from './components/StudyLayout';
import ThemeToggle from './components/ThemeToggle';
import gateway from './api/gateway';
import './styles/App.css';

/**
 * Main Teleios application component
 * Manages global state and coordinates data flow between panels
 */
function App() {
    // PDF and document state
    const [activePdf, setActivePdf] = useState(null);
    const [pdfFile, setPdfFile] = useState(null);
    const [documentId, setDocumentId] = useState(null);
    const [documents, setDocuments] = useState([]);

    // Chat and interaction state
    const [chatHistory, setChatHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    // Predictions and analysis state
    const [questions, setQuestions] = useState([]);
    const [questionAnalysis, setQuestionAnalysis] = useState(null);

    // Execution state
    const [executionOutput, setExecutionOutput] = useState(null);
    const [executionError, setExecutionError] = useState(null);

    // Highlighted text for explanation
    const [highlightedText, setHighlightedText] = useState(null);

    // Active panel (Chat, Predict, Execute, Ingest)
    const [activePanel, setActivePanel] = useState('chat');

    /**
     * Handle PDF file selection and ingestion
     */
    const handleFileSelected = useCallback(async (file) => {
        setPdfFile(file);
        setActivePdf(file.name);
        setIsLoading(true);

        try {
            const result = await gateway.ingestDocument(file);
            if (result.success) {
                const docId = result.data.doc_id || 'doc_' + Date.now();
                setDocumentId(docId);
                setDocuments((prev) => [
                    ...prev,
                    {
                        id: docId,
                        name: file.name,
                        uploadDate: new Date().toISOString(),
                    },
                ]);

                setChatHistory((prev) => [
                    ...prev,
                    {
                        role: 'system',
                        content: `Document "${file.name}" ingested successfully. Ready for analysis.`,
                        timestamp: new Date().toISOString(),
                    },
                ]);
            } else {
                setChatHistory((prev) => [
                    ...prev,
                    {
                        role: 'error',
                        content: `Failed to ingest document: ${result.error}`,
                        timestamp: new Date().toISOString(),
                    },
                ]);
            }
        } catch (error) {
            console.error('Ingest error:', error);
            setChatHistory((prev) => [
                ...prev,
                {
                    role: 'error',
                    content: `Error ingesting document: ${error.message}`,
                    timestamp: new Date().toISOString(),
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    }, []);

    /**
     * Handle text explanation request
     */
    const handleExplain = useCallback(
        async (query, highlightedSection = null) => {
            if (!documentId) {
                setChatHistory((prev) => [
                    ...prev,
                    {
                        role: 'error',
                        content: 'Please ingest a document first.',
                        timestamp: new Date().toISOString(),
                    },
                ]);
                return;
            }

            setIsLoading(true);
            const userMessage = {
                role: 'user',
                content: query,
                timestamp: new Date().toISOString(),
            };

            setChatHistory((prev) => [...prev, userMessage]);

            try {
                const response = await gateway.explainText(
                    query,
                    documentId,
                    highlightedSection || highlightedText || ''
                );

                const assistantMessage = {
                    role: 'assistant',
                    content: response.answer || response.explanation || 'No explanation available.',
                    citations: response.citations || [],
                    timestamp: new Date().toISOString(),
                };

                setChatHistory((prev) => [...prev, assistantMessage]);
            } catch (error) {
                console.error('Explain error:', error);
                setChatHistory((prev) => [
                    ...prev,
                    {
                        role: 'error',
                        content: `Error generating explanation: ${error.message}`,
                        timestamp: new Date().toISOString(),
                    },
                ]);
            } finally {
                setIsLoading(false);
            }
        },
        [documentId, highlightedText]
    );

    /**
     * Handle exam question prediction
     */
    const handlePredict = useCallback(async (difficulty = 'medium') => {
        if (!documentId) {
            setChatHistory((prev) => [
                ...prev,
                {
                    role: 'error',
                    content: 'Please ingest a document first.',
                    timestamp: new Date().toISOString(),
                },
            ]);
            return;
        }

        setIsLoading(true);

        try {
            const response = await gateway.predictQuestions([documentId], difficulty);
            setQuestions(response.questions || []);

            const analysisMsg = {
                role: 'system',
                content: `Generated ${response.questions?.length || 0} exam questions at ${difficulty} difficulty.`,
                timestamp: new Date().toISOString(),
            };

            setChatHistory((prev) => [...prev, analysisMsg]);
        } catch (error) {
            console.error('Predict error:', error);
            setChatHistory((prev) => [
                ...prev,
                {
                    role: 'error',
                    content: `Error predicting questions: ${error.message}`,
                    timestamp: new Date().toISOString(),
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    }, [documentId]);

    /**
     * Handle code execution
     */
    const handleExecute = useCallback(
        async (code) => {
            setIsLoading(true);
            setExecutionOutput(null);
            setExecutionError(null);

            try {
                const response = await gateway.executeCode(code, {}, documentId || null);

                if (response.status === 'ok') {
                    setExecutionOutput(response.output || '');
                    if (response.figures?.length > 0) {
                        // Handle figure URLs or data
                        console.log('Generated figures:', response.figures);
                    }

                    setChatHistory((prev) => [
                        ...prev,
                        {
                            role: 'system',
                            content: `Code executed successfully. Output length: ${(response.output || '').length} chars.`,
                            timestamp: new Date().toISOString(),
                        },
                    ]);
                } else {
                    setExecutionError(response.error || 'Unknown error');
                    setChatHistory((prev) => [
                        ...prev,
                        {
                            role: 'error',
                            content: `Execution failed: ${response.error}`,
                            timestamp: new Date().toISOString(),
                        },
                    ]);
                }
            } catch (error) {
                console.error('Execute error:', error);
                setExecutionError(error.message);
                setChatHistory((prev) => [
                    ...prev,
                    {
                        role: 'error',
                        content: `Error executing code: ${error.message}`,
                        timestamp: new Date().toISOString(),
                    },
                ]);
            } finally {
                setIsLoading(false);
            }
        },
        [documentId]
    );

    /**
     * Handle document analysis
     */
    const handleAnalyze = useCallback(async (groupBy = 'topic') => {
        if (!documentId) {
            setChatHistory((prev) => [
                ...prev,
                {
                    role: 'error',
                    content: 'Please ingest a document first.',
                    timestamp: new Date().toISOString(),
                },
            ]);
            return;
        }

        setIsLoading(true);

        try {
            const response = await gateway.analyzeDocuments([documentId], groupBy);
            setQuestionAnalysis(response);

            const analysisMsg = {
                role: 'system',
                content: `Analysis complete. Found ${Object.keys(response.groups || {}).length} topic groups.`,
                timestamp: new Date().toISOString(),
            };

            setChatHistory((prev) => [...prev, analysisMsg]);
        } catch (error) {
            console.error('Analyze error:', error);
            setChatHistory((prev) => [
                ...prev,
                {
                    role: 'error',
                    content: `Error analyzing document: ${error.message}`,
                    timestamp: new Date().toISOString(),
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    }, [documentId]);

    return (
        <div className="app-container">
            <ThemeToggle />
            <StudyLayout
                // Props for PDF viewer
                pdfFile={pdfFile}
                documentName={activePdf}
                onTextHighlighted={setHighlightedText}
                // Props for panel interactions
                activePanel={activePanel}
                onPanelChange={setActivePanel}
                // Data props
                chatHistory={chatHistory}
                questions={questions}
                questionAnalysis={questionAnalysis}
                executionOutput={executionOutput}
                executionError={executionError}
                isLoading={isLoading}
                // Callback props
                onFileSelected={handleFileSelected}
                onExplain={handleExplain}
                onPredict={handlePredict}
                onExecute={handleExecute}
                onAnalyze={handleAnalyze}
                documents={documents}
            />
        </div>
    );
}

export default App;
