import React, { useRef, useState, useEffect } from 'react';
import FileSystemExplorer from './FileSystemExplorer';
import '../styles/components/IngestPanel.css';

/**
 * Enhanced IngestPanel component
 * - File system integration for organizing uploads
 * - Page range selection for partial ingestion
 * - Processing status tracking
 */
function IngestPanel({ isLoading, onFileSelected, selectedCourse }) {
    const fileInputRef = useRef(null);
    const [selectedFile, setSelectedFile] = useState(null);
    const [selectedNode, setSelectedNode] = useState(null);
    const [showFileSystem, setShowFileSystem] = useState(false);
    const [pageRangeMode, setPageRangeMode] = useState('all');
    const [startPage, setStartPage] = useState('');
    const [endPage, setEndPage] = useState('');

    const handleFileChange = (e) => {
        const file = e.target.files?.[0];
        if (file && file.type === 'application/pdf') {
            setSelectedFile(file);
        } else if (file) {
            alert('Please select a PDF file.');
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.currentTarget.classList.add('drag-over');
    };

    const handleDragLeave = (e) => {
        e.currentTarget.classList.remove('drag-over');
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-over');

        const file = e.dataTransfer.files?.[0];
        if (file && file.type === 'application/pdf') {
            setSelectedFile(file);
        } else if (file) {
            alert('Please drop a PDF file.');
        }
    };

    const handleIngest = () => {
        if (!selectedFile) {
            alert('Please select a file first.');
            return;
        }

        const options = {
            file_system_node_id: selectedNode?.id,
        };

        if (pageRangeMode === 'range') {
            const start = parseInt(startPage);
            const end = parseInt(endPage);
            
            if (isNaN(start) || isNaN(end) || start < 1 || end < start) {
                alert('Please enter a valid page range.');
                return;
            }
            
            options.start_page = start;
            options.end_page = end;
        } else if (pageRangeMode === 'specific') {
            const pages = startPage.split(',').map(p => parseInt(p.trim())).filter(p => !isNaN(p));
            if (pages.length === 0) {
                alert('Please enter valid page numbers (e.g., 1, 3, 5-7).');
                return;
            }
            options.specific_pages = pages;
        }

        onFileSelected(selectedFile, options);
        setSelectedFile(null);
        setSelectedNode(null);
        setPageRangeMode('all');
        setStartPage('');
        setEndPage('');
    };

    return (
        <div className="ingest-panel">
            <div className="ingest-header">
                <h3>📤 Upload & Ingest Document</h3>
                <p>Upload PDF and organize in your file system</p>
            </div>

            {/* File Selection */}
            <div
                className="drop-zone"
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                    disabled={isLoading}
                />

                <div className="drop-zone-content">
                    {selectedFile ? (
                        <>
                            <p className="drop-icon">✅</p>
                            <p className="drop-text">{selectedFile.name}</p>
                            <p className="file-size">
                                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                            <button
                                className="browse-btn secondary"
                                onClick={() => fileInputRef.current?.click()}
                                disabled={isLoading}
                            >
                                Change File
                            </button>
                        </>
                    ) : (
                        <>
                            <p className="drop-icon">📄</p>
                            <p className="drop-text">Drag and drop your PDF here</p>
                            <p className="drop-separator">or</p>
                            <button
                                className="browse-btn"
                                onClick={() => fileInputRef.current?.click()}
                                disabled={isLoading}
                            >
                                🔍 Browse Files
                            </button>
                        </>
                    )}
                </div>
            </div>

            {/* File System Location */}
            {selectedFile && selectedCourse && (
                <div className="ingest-section">
                    <h4>📁 Save Location</h4>
                    <button
                        className="toggle-filesystem-btn"
                        onClick={() => setShowFileSystem(!showFileSystem)}
                    >
                        {showFileSystem ? '▼' : '▶'} {selectedNode ? `📂 ${selectedNode.name}` : '🏠 Root Folder'}
                    </button>
                    
                    {showFileSystem && (
                        <div className="filesystem-container">
                            <FileSystemExplorer
                                courseId={selectedCourse.id}
                                onNodeSelected={setSelectedNode}
                                selectedNode={selectedNode}
                                compact={true}
                            />
                        </div>
                    )}
                </div>
            )}

            {/* Page Range Selection */}
            {selectedFile && (
                <div className="ingest-section">
                    <h4>📄 Page Selection</h4>
                    <div className="page-range-options">
                        <label className="radio-option">
                            <input
                                type="radio"
                                value="all"
                                checked={pageRangeMode === 'all'}
                                onChange={(e) => setPageRangeMode(e.target.value)}
                            />
                            <span>All pages</span>
                        </label>
                        
                        <label className="radio-option">
                            <input
                                type="radio"
                                value="range"
                                checked={pageRangeMode === 'range'}
                                onChange={(e) => setPageRangeMode(e.target.value)}
                            />
                            <span>Page range</span>
                        </label>
                        
                        {pageRangeMode === 'range' && (
                            <div className="page-range-inputs">
                                <input
                                    type="number"
                                    placeholder="Start"
                                    value={startPage}
                                    onChange={(e) => setStartPage(e.target.value)}
                                    min="1"
                                />
                                <span>to</span>
                                <input
                                    type="number"
                                    placeholder="End"
                                    value={endPage}
                                    onChange={(e) => setEndPage(e.target.value)}
                                    min="1"
                                />
                            </div>
                        )}
                        
                        <label className="radio-option">
                            <input
                                type="radio"
                                value="specific"
                                checked={pageRangeMode === 'specific'}
                                onChange={(e) => setPageRangeMode(e.target.value)}
                            />
                            <span>Specific pages</span>
                        </label>
                        
                        {pageRangeMode === 'specific' && (
                            <input
                                type="text"
                                className="page-list-input"
                                placeholder="e.g., 1, 3, 5-7, 10"
                                value={startPage}
                                onChange={(e) => setStartPage(e.target.value)}
                            />
                        )}
                    </div>
                </div>
            )}

            {/* Ingest Button */}
            {selectedFile && (
                <button
                    className="ingest-btn"
                    onClick={handleIngest}
                    disabled={isLoading}
                >
                    {isLoading ? '⏳ Processing...' : '🚀 Ingest Document'}
                </button>
            )}

            {/* Info Sections */}
            <div className="ingest-info">
                <h4>📋 Features</h4>
                <ul>
                    <li>✅ OCR for scanned documents</li>
                    <li>✅ Mathematical equation extraction</li>
                    <li>✅ Figure and diagram recognition</li>
                    <li>✅ Smart text chunking with LLM cleaning</li>
                    <li>✅ Vector embeddings for RAG</li>
                </ul>
            </div>

            <div className="ingest-tips">
                <h4>💡 Tips</h4>
                <ul>
                    <li>Use page ranges to focus on specific chapters</li>
                    <li>Organize documents in folders by topic or chapter</li>
                    <li>Clear PDFs work better than low-quality scans</li>
                    <li>Processing time depends on document length and complexity</li>
                </ul>
            </div>
        </div>
    );
}

export default IngestPanel;
