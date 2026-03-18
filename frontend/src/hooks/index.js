/**
 * Custom React hooks for Teleios application
 * Providing reusable logic and state management
 */

import { useState, useCallback } from 'react';

/**
 * Hook for managing document state and operations
 */
export const useDocuments = () => {
    const [documents, setDocuments] = useState([]);
    const [activeDocumentId, setActiveDocumentId] = useState(null);
    const [activeFile, setActiveFile] = useState(null);

    const addDocument = useCallback((document) => {
        setDocuments((prev) => [...prev, document]);
        setActiveDocumentId(document.id);
        setActiveFile(document.file || null);
    }, []);

    const removeDocument = useCallback((docId) => {
        setDocuments((prev) => prev.filter((doc) => doc.id !== docId));
        if (activeDocumentId === docId) {
            setActiveDocumentId(null);
            setActiveFile(null);
        }
    }, [activeDocumentId]);

    const selectDocument = useCallback((docId) => {
        const doc = documents.find((d) => d.id === docId);
        if (doc) {
            setActiveDocumentId(docId);
            setActiveFile(doc.file || null);
        }
    }, [documents]);

    return {
        documents,
        activeDocumentId,
        activeFile,
        addDocument,
        removeDocument,
        selectDocument,
    };
};

/**
 * Hook for managing chat history
 */
export const useChatHistory = () => {
    const [history, setHistory] = useState([]);

    const addMessage = useCallback((message) => {
        setHistory((prev) => [...prev, { ...message, timestamp: new Date().toISOString() }]);
    }, []);

    const addMessages = useCallback((messages) => {
        setHistory((prev) => [
            ...prev,
            ...messages.map((msg) => ({ ...msg, timestamp: new Date().toISOString() })),
        ]);
    }, []);

    const clearHistory = useCallback(() => {
        setHistory([]);
    }, []);

    return {
        history,
        addMessage,
        addMessages,
        clearHistory,
    };
};

/**
 * Hook for managing loading and error states
 */
export const useAsyncState = (initialState = { loading: false, error: null, data: null }) => {
    const [state, setState] = useState(initialState);

    const setLoading = useCallback((loading) => {
        setState((prev) => ({ ...prev, loading }));
    }, []);

    const setError = useCallback((error) => {
        setState((prev) => ({ ...prev, error, loading: false }));
    }, []);

    const setData = useCallback((data) => {
        setState((prev) => ({ ...prev, data, loading: false, error: null }));
    }, []);

    const reset = useCallback(() => {
        setState(initialState);
    }, [initialState]);

    return {
        ...state,
        setLoading,
        setError,
        setData,
        reset,
    };
};

/**
 * Hook for managing UI panel state
 */
export const useActivePanel = (initialPanel = 'chat') => {
    const [activePanel, setActivePanel] = useState(initialPanel);

    const switchPanel = useCallback((panelId) => {
        setActivePanel(panelId);
    }, []);

    return {
        activePanel,
        switchPanel,
    };
};

/**
 * Hook for data filtering and searching
 */
export const useFilter = (items = []) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [filteredItems, setFilteredItems] = useState(items);

    const filter = useCallback(
        (term, filterFn = (item, term) => JSON.stringify(item).toLowerCase().includes(term.toLowerCase())) => {
            setSearchTerm(term);
            if (term.trim() === '') {
                setFilteredItems(items);
            } else {
                setFilteredItems(items.filter((item) => filterFn(item, term)));
            }
        },
        [items]
    );

    const reset = useCallback(() => {
        setSearchTerm('');
        setFilteredItems(items);
    }, [items]);

    return {
        searchTerm,
        filteredItems,
        filter,
        reset,
    };
};

/**
 * Hook for managing execution results
 */
export const useExecutionOutput = () => {
    const [output, setOutput] = useState(null);
    const [error, setError] = useState(null);
    const [figures, setFigures] = useState([]);
    const [isExecuting, setIsExecuting] = useState(false);

    const setExecutionResult = useCallback((result) => {
        if (result.success) {
            setOutput(result.data?.stdout || '');
            setFigures(result.data?.figures || []);
            setError(null);
        } else {
            setError(result.error);
            setOutput(null);
            setFigures([]);
        }
        setIsExecuting(false);
    }, []);

    const clear = useCallback(() => {
        setOutput(null);
        setError(null);
        setFigures([]);
        setIsExecuting(false);
    }, []);

    return {
        output,
        error,
        figures,
        isExecuting,
        setExecutionResult,
        setIsExecuting,
        clear,
    };
};

/**
 * Hook for managing highlighted text in PDF
 */
export const useHighlightedText = () => {
    const [highlightedText, setHighlightedText] = useState(null);
    const [highlightPosition, setHighlightPosition] = useState(null);

    const updateHighlight = useCallback((text, position = null) => {
        setHighlightedText(text);
        setHighlightPosition(position);
    }, []);

    const clearHighlight = useCallback(() => {
        setHighlightedText(null);
        setHighlightPosition(null);
    }, []);

    return {
        highlightedText,
        highlightPosition,
        updateHighlight,
        clearHighlight,
    };
};
