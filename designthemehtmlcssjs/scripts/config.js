/**
 * Configuration Management
 * Handles app settings, preferences, and configuration persistence
 */

class ConfigManager {
    constructor() {
        this.defaultConfig = {
            autoSave: true,
            autoSaveInterval: 30000, // 30 seconds
            theme: 'auto', // 'light', 'dark', or 'auto'
            animations: true,
            sounds: false,
            language: 'en',
            notifications: true,
            compactMode: false,
            showTooltips: true,
            keyboardShortcuts: true
        };
        
        this.config = { ...this.defaultConfig };
        this.listeners = new Set();
        this.load();
    }
    
    load() {
        try {
            const savedConfig = localStorage.getItem('kabul-taj-config');
            if (savedConfig) {
                const parsed = JSON.parse(savedConfig);
                this.config = { ...this.defaultConfig, ...parsed };
            }
        } catch (e) {
            console.warn('Could not load saved configuration:', e);
            this.config = { ...this.defaultConfig };
        }
        
        this.notifyListeners('load');
    }
    
    save() {
        try {
            localStorage.setItem('kabul-taj-config', JSON.stringify(this.config));
            this.notifyListeners('save');
            return true;
        } catch (e) {
            console.warn('Could not save configuration:', e);
            return false;
        }
    }
    
    get(key) {
        return this.config[key];
    }
    
    set(key, value) {
        const oldValue = this.config[key];
        this.config[key] = value;
        
        this.notifyListeners('change', { key, value, oldValue });
        this.save();
        
        return this;
    }
    
    update(updates) {
        const oldConfig = { ...this.config };
        this.config = { ...this.config, ...updates };
        
        this.notifyListeners('update', { updates, oldConfig });
        this.save();
        
        return this;
    }
    
    reset() {
        this.config = { ...this.defaultConfig };
        this.save();
        this.notifyListeners('reset');
        return this;
    }
    
    export() {
        return JSON.stringify(this.config, null, 2);
    }
    
    import(configJson) {
        try {
            const imported = JSON.parse(configJson);
            this.config = { ...this.defaultConfig, ...imported };
            this.save();
            this.notifyListeners('import');
            return true;
        } catch (e) {
            console.error('Invalid configuration format:', e);
            return false;
        }
    }
    
    // Event system
    onChange(callback) {
        this.listeners.add(callback);
        return () => this.listeners.delete(callback);
    }
    
    notifyListeners(type, data = {}) {
        this.listeners.forEach(callback => {
            try {
                callback({ type, config: this.config, ...data });
            } catch (e) {
                console.error('Config listener error:', e);
            }
        });
    }
    
    // Convenience methods
    isAutoSaveEnabled() {
        return this.config.autoSave;
    }
    
    getAutoSaveInterval() {
        return this.config.autoSaveInterval;
    }
    
    areAnimationsEnabled() {
        return this.config.animations && !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }
    
    areNotificationsEnabled() {
        return this.config.notifications;
    }
    
    getLanguage() {
        return this.config.language;
    }
}

// Export singleton instance
window.configManager = new ConfigManager();