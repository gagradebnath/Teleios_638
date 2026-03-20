import React, { useState, useCallback, useEffect } from 'react';
import StudyLayout from './components/StudyLayout';
import ThemeToggle from './components/ThemeToggle';
import CourseSelector from './components/CourseSelector';
import gateway from './api/gateway';
import './styles/App.css';

/**
 * Main Teleios application component
 * Manages global state and coordinates data flow between panels
 * Enhanced with course management and file system integration
 */
function App() {
    // Course state
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [showCourseSelector, setShowCourseSelector] = useState(true);

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
     * Load documents for selected course
     */
    useEffect(() => {
        if (selectedCourse) {
            loadCourseDocuments();
        }
    }, [selectedCourse]);

    const loadCourseDocuments = async () => {
        if (!selectedCourse) return;
        
        try {
            const docs = await gateway.listDocuments(selectedCourse.id);
            setDocuments(docs);
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    };

    /**
     * Handle course selection
     */
    const handleCourseSelected = useCallback((course) => {
        setSelectedCourse(course);
        setShowCourseSelector(false);
        setChatHistory((prev) => [
            ...prev,
            {
                role: 'system',
                content: `Course "${course.name}" selected. You can now upload and study documents for this course.`,
                timestamp: new Date().toISOString(),
            },
        ]);
    }, []);

    /**
     * Handle PDF file selection and ingestion
     */
    const handleFileSelected = useCallback(async (file, fileSystemNodeId = null) => {
        if (!selectedCourse) {
            setChatHistory((prev) => [
                ...prev,
                {
                    role: 'error',
                    content: 'Please select a course first.',
                    timestamp: new Date().toISOString(),
                },
            ]);
            return;
        }

        setPdfFile(file);
        setActivePdf(file.name);
        setIsLoading(true);

        try {
            const result = await gateway.ingestDocument(file, {
                course_id: selectedCourse.id,
                file_system_node_id: fileSystemNodeId,
            });
            
            if (result.success) {
                const docId = result.data.doc_id || 'doc_' + Date.now();
                setDocumentId(docId);
                await loadCourseDocuments();

                setChatHistory((prev) => [
                    ...prev,
                    {
                        role: 'system',
                        content: `Document "${file.name}" ingested successfully for course "${selectedCourse.name}". Ready for analysis.`,
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
    }, [selectedCourse]);

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
            
            {/* Course Selection Overlay */}
            {showCourseSelector && (
                <div className="course-selector-overlay">
                    <div className="course-selector-modal">
                        <h2>Welcome to Study Assistant</h2>
                        <p>Select a course to get started, or create a new one.</p>
                        <CourseSelector 
                            onCourseSelected={handleCourseSelected}
                            showAsModal={true}
                        />
                    </div>
                </div>
            )}

            {/* Main Study Interface */}
            {!showCourseSelector && (
                <>
                    {/* Course Header */}
                    <div className="course-header">
                        <div 
                            className="course-badge" 
                            style={{ backgroundColor: selectedCourse?.color || '#3b82f6' }}
                        >
                            {selectedCourse?.name}
                        </div>
                        <button 
                            className="change-course-btn"
                            onClick={() => setShowCourseSelector(true)}
                        >
                            Change Course
                        </button>
                    </div>

                    <StudyLayout
                        // Course context
                        selectedCourse={selectedCourse}
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
                </>
            )}
        </div>
    );
}

export default App;
