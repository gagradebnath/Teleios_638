import React from 'react';
import PDFViewer from './PDFViewer';
import '../styles/components/LeftPanel.css';

/**
 * LeftPanel component
 * Displays PDF documents and allows text selection
 */
function LeftPanel({ pdfFile, documentName, onTextHighlighted, documents }) {
    return (
        <div className="left-panel">
            <div className="left-panel-header">
                <h2>📄 Document</h2>
                {documentName && <span className="doc-name">{documentName}</span>}
            </div>

            <div className="left-panel-content">
                {pdfFile ? (
                    <PDFViewer
                        file={pdfFile}
                        onTextSelected={onTextHighlighted}
                    />
                ) : (
                    <div className="no-document">
                        <p>No document loaded.</p>
                        <p>Use the <strong>Ingest</strong> tab to upload a PDF.</p>
                    </div>
                )}
            </div>

            {documents.length > 0 && (
                <div className="document-list">
                    <h4>Recent Documents</h4>
                    <ul>
                        {documents.slice(-5).reverse().map((doc) => (
                            <li key={doc.id} className={doc.name === documentName ? 'active' : ''}>
                                {doc.name}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default LeftPanel;
