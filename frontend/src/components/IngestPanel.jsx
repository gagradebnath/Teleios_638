import React, { useRef } from 'react';
import './IngestPanel.css';

/**
 * IngestPanel component
 * Allows users to upload PDF documents
 */
function IngestPanel({ isLoading, onFileSelected }) {
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const file = e.target.files?.[0];
        if (file && file.type === 'application/pdf') {
            onFileSelected(file);
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
            onFileSelected(file);
        } else if (file) {
            alert('Please drop a PDF file.');
        }
    };

    return (
        <div className="ingest-panel">
            <div className="ingest-header">
                <h3>📤 Upload Document</h3>
                <p>Upload a PDF file to begin analysis</p>
            </div>

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
                    <p className="drop-icon">📄</p>
                    <p className="drop-text">
                        Drag and drop your PDF here
                    </p>
                    <p className="drop-separator">or</p>
                    <button
                        className="browse-btn"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isLoading}
                    >
                        {isLoading ? '⏳ Uploading...' : '🔍 Browse Files'}
                    </button>
                </div>
            </div>

            <div className="ingest-info">
                <h4>📋 Supported Formats</h4>
                <ul>
                    <li>PDF files (.pdf)</li>
                    <li>Maximum 50MB per file</li>
                    <li>Recommended: Documents with text (not scanned images only)</li>
                </ul>
            </div>

            <div className="ingest-tips">
                <h4>💡 Tips</h4>
                <ul>
                    <li>For best results, use clear, well-formatted documents</li>
                    <li>Scanned documents work best with good image quality</li>
                    <li>Complex tables and figures are preserved in analysis</li>
                </ul>
            </div>
        </div>
    );
}

export default IngestPanel;
