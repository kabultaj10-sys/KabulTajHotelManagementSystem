/**
 * Theme Management System
 * Handles light/dark mode switching with smooth transitions and persistence
 */

class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        this.themeToggleBtn = null;
        this.transitionTimeout = null;
        
        this.init();
    }
    
    init() {
        // Set initial theme
        this.setTheme(this.currentTheme, false);
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupEventListeners());
        } else {
            this.setupEventListeners();
        }
        
        // Listen for system theme changes
        this.watchSystemTheme();
    }
    
    setupEventListeners() {
        this.themeToggleBtn = document.getElementById('themeToggle');
        
        if (this.themeToggleBtn) {
            this.themeToggleBtn.addEventListener('click', () => this.toggleTheme());
        }
        
        // Keyboard shortcut (Ctrl/Cmd + Shift + T)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }
    
    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }
    
    getStoredTheme() {
        try {
            return localStorage.getItem('kabul-taj-theme');
        } catch (e) {
            console.warn('localStorage not available, using system theme');
            return null;
        }
    }
    
    storeTheme(theme) {
        try {
            localStorage.setItem('kabul-taj-theme', theme);
        } catch (e) {
            console.warn('localStorage not available, theme preference will not persist');
        }
    }
    
    setTheme(theme, animate = true) {
        // Add transition class for smooth animation
        if (animate && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.classList.add('theme-transitioning');
            
            // Remove transition class after animation completes
            clearTimeout(this.transitionTimeout);
            this.transitionTimeout = setTimeout(() => {
                document.documentElement.classList.remove('theme-transitioning');
            }, 300);
        }
        
        // Set theme attribute
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update current theme
        this.currentTheme = theme;
        
        // Store theme preference
        this.storeTheme(theme);
        
        // Update theme toggle button state
        this.updateThemeToggleState();
        
        // Dispatch theme change event
        this.dispatchThemeChangeEvent(theme);
        
        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(theme);
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
        
        // Add visual feedback
        this.addToggleFeedback();
    }
    
    updateThemeToggleState() {
        if (!this.themeToggleBtn) return;
        
        const isDark = this.currentTheme === 'dark';
        this.themeToggleBtn.setAttribute('aria-label', 
            isDark ? 'Switch to light mode' : 'Switch to dark mode'
        );
        this.themeToggleBtn.setAttribute('title', 
            isDark ? 'Switch to light mode' : 'Switch to dark mode'
        );
    }
    
    addToggleFeedback() {
        if (!this.themeToggleBtn) return;
        
        // Add scale animation
        this.themeToggleBtn.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
            this.themeToggleBtn.style.transform = '';
        }, 150);
    }
    
    watchSystemTheme() {
        if (!window.matchMedia) return;
        
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        mediaQuery.addEventListener('change', (e) => {
            // Only change theme if user hasn't manually set a preference
            if (!this.getStoredTheme()) {
                const systemTheme = e.matches ? 'dark' : 'light';
                this.setTheme(systemTheme);
            }
        });
    }
    
    dispatchThemeChangeEvent(theme) {
        const event = new CustomEvent('themechange', {
            detail: { theme, previousTheme: this.currentTheme }
        });
        document.dispatchEvent(event);
    }
    
    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        const color = theme === 'dark' ? '#0f0f0f' : '#ffffff';
        metaThemeColor.content = color;
    }
    
    // Public API methods
    getCurrentTheme() {
        return this.currentTheme;
    }
    
    isDarkMode() {
        return this.currentTheme === 'dark';
    }
    
    isLightMode() {
        return this.currentTheme === 'light';
    }
    
    // Force theme without animation (useful for initial load)
    forceTheme(theme) {
        this.setTheme(theme, false);
    }
    
    // Reset to system preference
    resetToSystemTheme() {
        try {
            localStorage.removeItem('kabul-taj-theme');
        } catch (e) {
            console.warn('Could not clear theme preference');
        }
        
        const systemTheme = this.getSystemTheme();
        this.setTheme(systemTheme);
    }
}

// Utility functions for theme-aware components
const ThemeUtils = {
    // Get CSS custom property value
    getCSSProperty(property) {
        return getComputedStyle(document.documentElement).getPropertyValue(property).trim();
    },
    
    // Set CSS custom property
    setCSSProperty(property, value) {
        document.documentElement.style.setProperty(property, value);
    },
    
    // Check if user prefers reduced motion
    prefersReducedMotion() {
        return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },
    
    // Check if user prefers high contrast
    prefersHighContrast() {
        return window.matchMedia && window.matchMedia('(prefers-contrast: high)').matches;
    },
    
    // Get theme-appropriate color
    getThemeColor(lightColor, darkColor) {
        const theme = window.themeManager?.getCurrentTheme() || 'light';
        return theme === 'dark' ? darkColor : lightColor;
    },
    
    // Apply theme-aware styles to element
    applyThemeStyles(element, lightStyles, darkStyles) {
        const theme = window.themeManager?.getCurrentTheme() || 'light';
        const styles = theme === 'dark' ? darkStyles : lightStyles;
        
        Object.assign(element.style, styles);
    }
};

// Initialize theme manager when script loads
window.themeManager = new ThemeManager();

// Export utilities for other scripts
window.ThemeUtils = ThemeUtils;

// Theme change event listeners for other components
document.addEventListener('themechange', (e) => {
    console.log(`Theme changed to: ${e.detail.theme}`);
    
    // You can add custom logic here that should run when theme changes
    // For example, updating chart colors, map themes, etc.
});

// Console utilities for debugging
if (typeof window !== 'undefined' && window.console) {
    window.console.info('🎨 Theme Manager loaded. Available commands:');
    window.console.info('- themeManager.toggleTheme()');
    window.console.info('- themeManager.setTheme("light" | "dark")');
    window.console.info('- themeManager.resetToSystemTheme()');
    window.console.info('- ThemeUtils.getCSSProperty("--color-primary")');
}