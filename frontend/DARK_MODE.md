# Dark Mode Implementation Guide

> τέλειος now supports automatic dark mode switching with persistent preferences!

---

## Features

✅ **Light & Dark Themes** — Two beautiful color schemes  
✅ **Toggle Button** — Fixed position for easy access  
✅ **Auto-Detection** — Respects system preference on first load  
✅ **Persistent** — Saves preference to localStorage  
✅ **Smooth Transitions** — All colors animate smoothly  
✅ **Accessible** — ARIA labels and keyboard support

---

## User Experience

### Toggle Button
- **Location:** Fixed in top-right corner
- **Icon:** 
  - 🌙 Moon icon (when in light mode, click for dark)
  - ☀️ Sun icon (when in dark mode, click for light)
- **Label:** Shows "Dark" or "Light" text
- **Responsive:** Hides label on mobile, shows icon only

### Theme Persistence
Your theme choice is automatically saved and restored:
1. First visit → Uses system preference
2. After toggle → Saves to localStorage
3. Next visit → Restores your choice

---

## Technical Implementation

### 1. Theme Context (`src/hooks/useTheme.jsx`)

React Context API manages theme state:

```javascript
import { useTheme } from './hooks/useTheme';

const { theme, toggleTheme, isDark } = useTheme();
```

**API:**
- `theme` — Current theme ('light' | 'dark')
- `toggleTheme()` — Switch between themes
- `isDark` — Boolean helper

### 2. CSS Variables (`src/styles/globals.css`)

All colors defined as CSS custom properties:

```css
/* Light theme */
[data-theme="light"] {
    --text-primary: #1a1a1a;
    --bg-primary: #ffffff;
    --border-color: #e0e0e0;
}

/* Dark theme */
[data-theme="dark"] {
    --text-primary: #e4e4e7;
    --bg-primary: #18181b;
    --border-color: #3f3f46;
}
```

### 3. Theme Toggle Component

Fixed position button with SVG icons:

```jsx
<ThemeToggle /> {/* Add to App.jsx */}
```

---

## Color Palettes

### Light Mode
- **Text:** Dark (#1a1a1a, #666, #999)
- **Background:** White (#ffffff, #f9f9f9, #f5f5f5)
- **Borders:** Light gray (#e0e0e0, #e8e8e8)
- **Shadows:** Subtle black with low opacity

### Dark Mode
- **Text:** Light (#e4e4e7, #a1a1aa, #71717a)
- **Background:** Dark (#18181b, #27272a, #3f3f46)
- **Borders:** Dark gray (#3f3f46, #52525b)
- **Shadows:** Black with higher opacity

### Accent Colors (Both Themes)
- **Primary:** Purple gradient (#667eea → #764ba2)
- **Success:** Green (#4caf50 / #66bb6a)
- **Warning:** Orange (#ff9800 / #ffa726)
- **Error:** Red (#f44336 / #ef5350)
- **Info:** Blue (#2196f3 / #42a5f5)

Accent colors are slightly muted in dark mode for better eye comfort.

---

## Usage in New Components

### Using Theme Variables

```css
/* ✅ Good - Uses CSS variables */
.my-component {
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

/* ❌ Bad - Hardcoded colors */
.my-component {
    background: #ffffff;
    color: #1a1a1a;
    border: 1px solid #e0e0e0;
}
```

### Available Variables

**Colors:**
- `--text-primary`, `--text-secondary`, `--text-tertiary`, `--text-light`
- `--bg-primary`, `--bg-secondary`, `--bg-tertiary`, `--bg-hover`
- `--border-color`, `--border-light`
- `--primary-color`, `--success-color`, `--warning-color`, `--error-color`

**Shadows:**
- `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-xl`

**Spacing:**
- `--spacing-xs` (4px) → `--spacing-2xl` (48px)

**Border Radius:**
- `--radius-sm` (4px) → `--radius-xl` (16px)

**Transitions:**
- `--transition-fast` (0.15s)
- `--transition-normal` (0.3s)
- `--transition-slow` (0.5s)

---

## Accessing Theme in JavaScript

```javascript
import { useTheme } from './hooks/useTheme';

function MyComponent() {
    const { theme, toggleTheme, isDark } = useTheme();
    
    return (
        <div>
            <p>Current theme: {theme}</p>
            <button onClick={toggleTheme}>
                Toggle to {isDark ? 'light' : 'dark'} mode
            </button>
        </div>
    );
}
```

---

## Testing

### Manual Testing
1. **Toggle Test:**
   - Click theme toggle button
   - Verify colors change smoothly
   - Check all panels update

2. **Persistence Test:**
   - Toggle theme
   - Refresh page
   - Verify theme persists

3. **System Preference Test:**
   - Clear localStorage: `localStorage.removeItem('teleios-theme')`
   - Reload page
   - Verify system preference is detected

### Browser DevTools
```javascript
// Check current theme
document.documentElement.getAttribute('data-theme')

// Force theme change
document.documentElement.setAttribute('data-theme', 'dark')

// Check localStorage
localStorage.getItem('teleios-theme')
```

---

## Configuration

### Default Theme

Edit `src/hooks/useTheme.jsx`:

```javascript
const getInitialTheme = () => {
    // Change this line to set default
    return 'dark'; // or 'light'
};
```

### Disable System Preference Detection

```javascript
const getInitialTheme = () => {
    const savedTheme = localStorage.getItem('teleios-theme');
    if (savedTheme) return savedTheme;
    
    // Remove this block to always start with 'light'
    // if (window.matchMedia...) { ... }
    
    return 'light'; // Always default to light
};
```

---

## Accessibility

✅ **ARIA Labels:** Button has descriptive aria-label  
✅ **Keyboard Support:** Fully keyboard accessible  
✅ **Focus Visible:** Clear focus indicators  
✅ **Color Contrast:** WCAG AA compliant in both themes  
✅ **Screen Readers:** Announces current and target theme

---

## Browser Support

**Modern Browsers:**
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**Features Used:**
- CSS Custom Properties (CSS Variables)
- localStorage
- prefers-color-scheme media query
- React Context API

---

## Troubleshooting

### Theme Not Persisting

**Check localStorage:**
```javascript
localStorage.getItem('teleios-theme') // Should return 'light' or 'dark'
```

**Solution:** Ensure ThemeProvider wraps App in main.jsx

### Colors Not Changing

**Check data-theme attribute:**
```javascript
document.documentElement.getAttribute('data-theme')
```

**Solution:** Verify CSS variables are used instead of hardcoded colors

### Toggle Button Not Visible

**Check z-index:**
```css
.theme-toggle {
    z-index: 1000; /* Should be high */
}
```

**Solution:** Increase z-index if covered by other elements

---

## Future Enhancements

Possible improvements:
- [ ] More theme options (blue, green, etc.)
- [ ] Auto-switch based on time of day
- [ ] Custom theme builder
- [ ] High contrast mode
- [ ] Reduced motion support

---

**Last Updated:** 2026-03-18 22:22 UTC  
**Version:** 1.0.0
