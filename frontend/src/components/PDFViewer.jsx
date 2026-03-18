import React, { useEffect, useRef, useState } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import './PDFViewer.css';

// Set up PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

/**
 * PDFViewer component
 * Displays PDF documents with text selection support
 */
function PDFViewer({ file, onTextSelected }) {
    const canvasRef = useRef(null);
    const [numPages, setNumPages] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [scale, setScale] = useState(1.5);
    const [isLoading, setIsLoading] = useState(false);

    // Load PDF when file changes
    useEffect(() => {
        if (!file) return;

        const loadPdf = async () => {
            try {
                setIsLoading(true);
                const arrayBuffer = await file.arrayBuffer();
                const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
                setNumPages(pdf.numPages);
                setCurrentPage(1);
            } catch (error) {
                console.error('Error loading PDF:', error);
            } finally {
                setIsLoading(false);
            }
        };

        loadPdf();
    }, [file]);

    // Render current page
    useEffect(() => {
        if (!file || !canvasRef.current) return;

        const renderPage = async () => {
            try {
                setIsLoading(true);
                const arrayBuffer = await file.arrayBuffer();
                const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
                const page = await pdf.getPage(currentPage);

                const viewport = page.getViewport({ scale });
                const canvas = canvasRef.current;
                const context = canvas.getContext('2d');

                canvas.width = viewport.width;
                canvas.height = viewport.height;

                await page.render({
                    canvasContext: context,
                    viewport: viewport,
                }).promise;
            } catch (error) {
                console.error('Error rendering PDF page:', error);
            } finally {
                setIsLoading(false);
            }
        };

        renderPage();
    }, [file, currentPage, scale]);

    // Handle text selection
    const handleTextSelection = () => {
        const selectedText = window.getSelection().toString();
        if (selectedText && onTextSelected) {
            onTextSelected(selectedText);
        }
    };

    return (
        <div className="pdf-viewer">
            <div className="pdf-controls">
                <div className="pdf-nav">
                    <button
                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                    >
                        ← Prev
                    </button>
                    <span className="page-info">
                        Page {currentPage} of {numPages}
                    </span>
                    <button
                        onClick={() => setCurrentPage(Math.min(numPages, currentPage + 1))}
                        disabled={currentPage === numPages}
                    >
                        Next →
                    </button>
                </div>

                <div className="pdf-zoom">
                    <button onClick={() => setScale(Math.max(0.5, scale - 0.25))}>
                        🔍−
                    </button>
                    <span className="zoom-level">{Math.round(scale * 100)}%</span>
                    <button onClick={() => setScale(scale + 0.25)}>
                        🔍+
                    </button>
                    <button onClick={() => setScale(1.5)}>
                        Reset
                    </button>
                </div>
            </div>

            <div
                className="pdf-canvas-container"
                onMouseUp={handleTextSelection}
            >
                {isLoading && <div className="pdf-loading">Loading...</div>}
                <canvas ref={canvasRef} className="pdf-canvas" />
            </div>

            <div className="pdf-hint">
                Select text to highlight and explain
            </div>
        </div>
    );
}

export default PDFViewer;
