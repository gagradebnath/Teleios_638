# CSS Theming Update Progress

## Files Updated ✅
- [x] App.css - Background colors
- [x] ChatPanel.css - All colors using variables
- [x] globals.css - Added message backgrounds, scrollbar, input focus variables

## Files Remaining
- [ ] PDFViewer.css
- [ ] StudyLayout.css
- [ ] LeftPanel.css
- [ ] TabBar.css
- [ ] IngestPanel.css
- [ ] PredictionPanel.css
- [ ] ExecutionPanel.css

## Color Mapping Reference

### Light Theme → Variables
- `#fff`, `#ffffff` → `var(--bg-primary)`
- `#f9f9f9` → `var(--bg-secondary)`
- `#f5f5f5`, `#fafafa` → `var(--bg-tertiary)`
- `#f0f0f0` → `var(--bg-hover)`
- `#333`, `#1a1a1a` → `var(--text-primary)`
- `#666`, `#555` → `var(--text-secondary)`
- `#999`, `#aaa` → `var(--text-tertiary)`
- `#e0e0e0` → `var(--border-color)`
- `#ddd`, `#e8e8e8` → `var(--border-light)`
- `#667eea` → `var(--primary-color)`
- `#4caf50` → `var(--success-color)`
- `#ff9800` → `var(--warning-color)`
- `#f44336` → `var(--error-color)`

### Dark Theme (Auto-applied)
CSS variables automatically switch when data-theme="dark"

## Next Steps
1. Update PDF Viewer CSS
2. Update StudyLayout CSS
3. Update LeftPanel CSS
4. Update TabBar CSS
5. Update IngestPanel CSS
6. Update PredictionPanel CSS
7. Update ExecutionPanel CSS
