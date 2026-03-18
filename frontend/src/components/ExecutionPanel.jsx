import React, { useState } from 'react';
import '../styles/components/ExecutionPanel.css';

/**
 * ExecutionPanel component
 * Allows users to execute Python code in sandboxed environment
 */
function ExecutionPanel({ output, error, isLoading, onExecute }) {
    const [code, setCode] = useState('# Write Python code here\nimport numpy as np\n\n# Example:\nprint("Hello from Teleios!")');

    const handleExecute = () => {
        if (!code.trim()) return;
        onExecute(code);
    };

    const handleLoadTemplate = (template) => {
        const templates = {
            stats: `import numpy as np
import json

# Example: Calculate statistics
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(f"Mean: {np.mean(data)}")
print(f"Std Dev: {np.std(data)}")
print(f"Min: {np.min(data)}")
print(f"Max: {np.max(data)}")`,
            plot: `import matplotlib.pyplot as plt
import numpy as np

# Example: Simple plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.title('Sin Wave')
plt.grid(True)
plt.show()`,
            analysis: `# Example: Text analysis
text = "Lorem ipsum dolor sit amet"
words = text.split()
word_freq = {}

for word in words:
    word_freq[word] = word_freq.get(word, 0) + 1

print("Word frequencies:")
for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True):
    print(f"  {word}: {freq}")`,
        };
        setCode(templates[template] || '');
    };

    return (
        <div className="execution-panel">
            <div className="execution-header">
                <h3>⚙️ Python Code Execution</h3>
                <p>Execute Python code in a sandboxed environment</p>
            </div>

            <div className="code-editor-area">
                <div className="editor-toolbar">
                    <button
                        className="template-btn"
                        onClick={() => handleLoadTemplate('stats')}
                        disabled={isLoading}
                    >
                        📊 Stats Template
                    </button>
                    <button
                        className="template-btn"
                        onClick={() => handleLoadTemplate('plot')}
                        disabled={isLoading}
                    >
                        📈 Plot Template
                    </button>
                    <button
                        className="template-btn"
                        onClick={() => handleLoadTemplate('analysis')}
                        disabled={isLoading}
                    >
                        🔍 Analysis Template
                    </button>
                    <div style={{ flex: 1 }} />
                    <button
                        className="execute-btn"
                        onClick={handleExecute}
                        disabled={isLoading || !code.trim()}
                    >
                        {isLoading ? '⏳ Running...' : '▶️ Execute'}
                    </button>
                </div>

                <textarea
                    className="code-editor"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="Write Python code here..."
                    disabled={isLoading}
                    spellCheck="false"
                />
            </div>

            {(output || error) && (
                <div className="output-section">
                    <h4>Output:</h4>
                    {error && (
                        <div className="output-error">
                            <pre>{error}</pre>
                        </div>
                    )}
                    {output && (
                        <div className="output-success">
                            <pre>{output}</pre>
                        </div>
                    )}
                </div>
            )}

            <div className="execution-info">
                <h4>🔒 Security & Limitations</h4>
                <ul>
                    <li>Code runs in a sandboxed environment</li>
                    <li>File system access is restricted</li>
                    <li>Network access is disabled</li>
                    <li>Timeout: 30 seconds per execution</li>
                    <li>Available libraries: numpy, matplotlib, pandas, scipy</li>
                </ul>
            </div>
        </div>
    );
}

export default ExecutionPanel;
