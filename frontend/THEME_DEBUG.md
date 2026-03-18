# Theme Switching Debug Guide

## Quick Test

If theme switching isn't working, follow these steps:

### 1. Open Browser Console

Press F12 or right-click → Inspect → Console tab

### 2. Check Current Theme

```javascript
// Should be 'light' or 'dark'
document.documentElement.getAttribute('data-theme')
```

### 3. Check CSS Variables

```javascript
// Should show theme colors
getComputedStyle(document.documentElement).getPropertyValue('--bg-primary')
getComputedStyle(document.documentElement).getPropertyValue('--text-primary')
```

### 4. Manually Toggle Theme

```javascript
// Force dark theme
document.documentElement.setAttribute('data-theme', 'dark')

// Force light theme
document.documentElement.setAttribute('data-theme', 'light')
```

### 5. Check localStorage

```javascript
// Should show saved theme
localStorage.getItem('teleios-theme')

// Clear and reload to reset
localStorage.removeItem('teleios-theme')
location.reload()
```

---

## Common Issues

### Issue 1: CSS Not Loading

**Symptom:** Theme attribute changes but colors don't

**Check:**
```javascript
// Look for @import './globals.css' at the top
fetch('/src/styles/index.css').then(r => r.text()).then(console.log)
```

**Fix:** Ensure `index.css` imports `globals.css`

---

### Issue 2: Button Not Clickable

**Symptom:** Click does nothing

**Check Console for Errors:**
- "useTheme must be used within ThemeProvider"
- React errors

**Fix:** Ensure ThemeProvider wraps App in main.jsx

---

### Issue 3: Variables Not Defined

**Symptom:** Colors are wrong or missing

**Check:**
```javascript
// Should return the color value
getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim()
```

**Fix:** Restart dev server after CSS changes

---

## Step-by-Step Test

1. **Check theme attribute:**
   ```javascript
   document.documentElement.getAttribute('data-theme')
   // Expected: 'light' or 'dark'
   ```

2. **Click toggle button** (top-right corner)

3. **Check attribute changed:**
   ```javascript
   document.documentElement.getAttribute('data-theme')
   // Should be opposite of step 1
   ```

4. **Check colors updated:**
   ```javascript
   getComputedStyle(document.body).backgroundColor
   // Light: rgb(255, 255, 255) - white
   // Dark: rgb(24, 24, 27) - dark gray
   ```

5. **Refresh page:**
   - Theme should persist

---

## Manual Fix

If automatic fix doesn't work, manually apply theme:

```javascript
// Add to browser console
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('teleios-theme', theme);
    console.log('Theme applied:', theme);
}

// Use it
applyTheme('dark')
applyTheme('light')
```

---

## Verification Checklist

- [ ] `index.css` has `@import './globals.css'` at top
- [ ] `globals.css` has `[data-theme="dark"]` section
- [ ] `main.jsx` has `<ThemeProvider>` wrapping `<App />`
- [ ] Dev server restarted after CSS changes
- [ ] No console errors
- [ ] Toggle button visible
- [ ] Console logs show theme changes

---

## Still Not Working?

Try complete cache clear:

1. **Hard refresh:** Ctrl+Shift+R (Cmd+Shift+R on Mac)
2. **Clear storage:**
   ```javascript
   localStorage.clear()
   sessionStorage.clear()
   ```
3. **Restart dev server:**
   ```bash
   # Stop server (Ctrl+C)
   npm run dev
   ```

---

**If issue persists after these steps, check browser console for specific errors.**
