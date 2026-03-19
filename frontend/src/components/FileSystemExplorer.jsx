import React, { useState, useEffect } from 'react';
import { gateway } from '../api/gateway';
import './FileSystemExplorer.css';

const FileSystemExplorer = ({ courseId, onFileSelect }) => {
    const [nodes, setNodes] = useState([]);
    const [currentPath, setCurrentPath] = useState([]);
    const [currentParentId, setCurrentParentId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showNewFolderModal, setShowNewFolderModal] = useState(false);
    const [newFolderName, setNewFolderName] = useState('');

    // Load nodes for current location
    const loadNodes = async () => {
        setLoading(true);
        setError(null);
        try {
            const filters = {};
            if (currentParentId) filters.parent_id = currentParentId;
            if (courseId) filters.course_id = courseId;
            
            const fetchedNodes = await gateway.listFileSystemNodes(filters);
            setNodes(fetchedNodes || []);
        } catch (err) {
            setError(err.message);
            console.error('Error loading nodes:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadNodes();
    }, [currentParentId, courseId]);

    // Navigate into a folder
    const handleFolderClick = async (folder) => {
        setCurrentParentId(folder.id);
        setCurrentPath([...currentPath, { id: folder.id, name: folder.name }]);
    };

    // Navigate to breadcrumb
    const handleBreadcrumbClick = (index) => {
        if (index === -1) {
            // Root
            setCurrentParentId(null);
            setCurrentPath([]);
        } else {
            const targetFolder = currentPath[index];
            setCurrentParentId(targetFolder.id);
            setCurrentPath(currentPath.slice(0, index + 1));
        }
    };

    // Create new folder
    const handleCreateFolder = async () => {
        if (!newFolderName.trim()) return;

        try {
            await gateway.createFolder({
                name: newFolderName,
                parent_id: currentParentId,
                course_id: courseId,
            });
            setNewFolderName('');
            setShowNewFolderModal(false);
            loadNodes(); // Refresh
        } catch (err) {
            alert(`Error creating folder: ${err.message}`);
        }
    };

    // Delete node
    const handleDelete = async (nodeId, nodeName) => {
        if (!confirm(`Delete "${nodeName}"?`)) return;

        try {
            await gateway.deleteFileSystemNode(nodeId);
            loadNodes(); // Refresh
        } catch (err) {
            alert(`Error deleting: ${err.message}`);
        }
    };

    // Handle file click
    const handleFileClick = (file) => {
        if (onFileSelect) {
            onFileSelect(file);
        }
    };

    // Format file size
    const formatSize = (bytes) => {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    // Render breadcrumbs
    const renderBreadcrumbs = () => (
        <div className="breadcrumbs">
            <button
                className="breadcrumb-item"
                onClick={() => handleBreadcrumbClick(-1)}
            >
                🏠 Root
            </button>
            {currentPath.map((crumb, index) => (
                <React.Fragment key={crumb.id}>
                    <span className="breadcrumb-separator">/</span>
                    <button
                        className="breadcrumb-item"
                        onClick={() => handleBreadcrumbClick(index)}
                    >
                        {crumb.name}
                    </button>
                </React.Fragment>
            ))}
        </div>
    );

    // Render node list
    const renderNodes = () => {
        if (loading) return <div className="loading">Loading...</div>;
        if (error) return <div className="error">Error: {error}</div>;
        if (nodes.length === 0) return <div className="empty">No files or folders</div>;

        // Sort: folders first, then files
        const sorted = [...nodes].sort((a, b) => {
            if (a.node_type === b.node_type) return a.name.localeCompare(b.name);
            return a.node_type === 'folder' ? -1 : 1;
        });

        return (
            <div className="node-list">
                {sorted.map((node) => (
                    <div
                        key={node.id}
                        className={`node-item node-${node.node_type}`}
                        onClick={() => {
                            if (node.node_type === 'folder') {
                                handleFolderClick(node);
                            } else {
                                handleFileClick(node);
                            }
                        }}
                    >
                        <div className="node-icon">
                            {node.node_type === 'folder' ? '📁' : '📄'}
                        </div>
                        <div className="node-info">
                            <div className="node-name">{node.name}</div>
                            <div className="node-meta">
                                {node.node_type === 'file' && (
                                    <span className="node-size">{formatSize(node.size_bytes)}</span>
                                )}
                                <span className="node-date">
                                    {new Date(node.created_at).toLocaleDateString()}
                                </span>
                            </div>
                        </div>
                        <button
                            className="node-delete"
                            onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(node.id, node.name);
                            }}
                            title="Delete"
                        >
                            🗑️
                        </button>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <div className="file-system-explorer">
            <div className="explorer-toolbar">
                {renderBreadcrumbs()}
                <button
                    className="btn btn-primary btn-sm"
                    onClick={() => setShowNewFolderModal(true)}
                >
                    ➕ New Folder
                </button>
            </div>

            {renderNodes()}

            {/* New Folder Modal */}
            {showNewFolderModal && (
                <div className="modal-overlay" onClick={() => setShowNewFolderModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h3>Create New Folder</h3>
                        <input
                            type="text"
                            className="form-control"
                            placeholder="Folder name"
                            value={newFolderName}
                            onChange={(e) => setNewFolderName(e.target.value)}
                            onKeyPress={(e) => {
                                if (e.key === 'Enter') handleCreateFolder();
                            }}
                            autoFocus
                        />
                        <div className="modal-actions">
                            <button
                                className="btn btn-secondary"
                                onClick={() => setShowNewFolderModal(false)}
                            >
                                Cancel
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={handleCreateFolder}
                            >
                                Create
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FileSystemExplorer;
