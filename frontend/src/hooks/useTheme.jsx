/**
 * ThemeContext - Manages light/dark theme state
 * Provides theme context to all components
 */
import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within ThemeProvider');
    }
    return context;
};

export const ThemeProvider = ({ children }) => {
    // Initialize theme from localStorage or system preference
    const getInitialTheme = () => {
        // Check localStorage first
        const savedTheme = localStorage.getItem('teleios-theme');
        if (savedTheme) {
            return savedTheme;
        }
        
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        
        return 'light';
    };

    const [theme, setTheme] = useState(getInitialTheme);

    // Apply theme to document root
    useEffect(() => {
        console.log('Applying theme:', theme);
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('teleios-theme', theme);
        console.log('DOM data-theme:', document.documentElement.getAttribute('data-theme'));
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prevTheme => {
            const newTheme = prevTheme === 'light' ? 'dark' : 'light';
            console.log('Theme toggled:', prevTheme, '→', newTheme);
            return newTheme;
        });
    };

    const value = {
        theme,
        toggleTheme,
        isDark: theme === 'dark',
    };

    return (
        <ThemeContext.Provider value={value}>
            {children}
        </ThemeContext.Provider>
    );
};

export default ThemeContext;
