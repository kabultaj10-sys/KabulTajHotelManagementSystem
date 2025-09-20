/**
 * Data Management System
 * Handles local data storage, auto-save, and data synchronization
 */

class DataManager {
    constructor() {
        this.data = {
            guests: [],
            bookings: [],
            rooms: [],
            staff: [],
            inventory: [],
            orders: [],
            settings: {},
            lastModified: Date.now()
        };
        
        this.autoSaveTimer = null;
        this.isDirty = false;
        this.isLoading = false;
        this.isSaving = false;
        
        this.init();
    }
    
    init() {
        this.loadData();
        this.setupAutoSave();
        this.setupEventListeners();
    }
    
    loadData() {
        this.isLoading = true;
        
        try {
            const savedData = localStorage.getItem('kabul-taj-data');
            if (savedData) {
                const parsed = JSON.parse(savedData);
                this.data = { ...this.data, ...parsed };
            } else {
                // Load demo data if no saved data exists
                this.loadDemoData();
            }
        } catch (e) {
            console.error('Failed to load data:', e);
            this.loadDemoData();
        }
        
        this.isLoading = false;
        this.isDirty = false;
        this.dispatchEvent('dataLoaded');
    }
    
    saveData() {
        if (this.isSaving) return Promise.resolve();
        
        this.isSaving = true;
        
        return new Promise((resolve, reject) => {
            try {
                this.data.lastModified = Date.now();
                localStorage.setItem('kabul-taj-data', JSON.stringify(this.data));
                
                this.isDirty = false;
                this.isSaving = false;
                this.dispatchEvent('dataSaved');
                resolve();
            } catch (e) {
                this.isSaving = false;
                console.error('Failed to save data:', e);
                this.dispatchEvent('saveError', { error: e });
                reject(e);
            }
        });
    }
    
    setupAutoSave() {
        const interval = window.configManager?.getAutoSaveInterval() || 30000;
        
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
        }
        
        if (window.configManager?.isAutoSaveEnabled()) {
            this.autoSaveTimer = setInterval(() => {
                if (this.isDirty) {
                    this.saveData();
                }
            }, interval);
        }
    }
    
    setupEventListeners() {
        // Listen for config changes
        if (window.configManager) {
            window.configManager.onChange((event) => {
                if (event.key === 'autoSave' || event.key === 'autoSaveInterval') {
                    this.setupAutoSave();
                }
            });
        }
        
        // Save data when page is about to unload
        window.addEventListener('beforeunload', () => {
            if (this.isDirty) {
                this.saveData();
            }
        });
        
        // Save data when page becomes hidden (mobile)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isDirty) {
                this.saveData();
            }
        });
    }
    
    // Data access methods
    get(collection, id = null) {
        if (!this.data[collection]) {
            console.warn(`Collection '${collection}' does not exist`);
            return id ? null : [];
        }
        
        if (id === null) {
            return [...this.data[collection]];
        }
        
        return this.data[collection].find(item => item.id === id) || null;
    }
    
    set(collection, data) {
        if (!this.data[collection]) {
            console.warn(`Collection '${collection}' does not exist`);
            return false;
        }
        
        this.data[collection] = Array.isArray(data) ? [...data] : [data];
        this.markDirty();
        this.dispatchEvent('dataChanged', { collection, action: 'set' });
        return true;
    }
    
    add(collection, item) {
        if (!this.data[collection]) {
            console.warn(`Collection '${collection}' does not exist`);
            return false;
        }
        
        const newItem = {
            ...item,
            id: item.id || this.generateId(),
            createdAt: Date.now(),
            updatedAt: Date.now()
        };
        
        this.data[collection].push(newItem);
        this.markDirty();
        this.dispatchEvent('dataChanged', { collection, action: 'add', item: newItem });
        return newItem;
    }
    
    update(collection, id, updates) {
        if (!this.data[collection]) {
            console.warn(`Collection '${collection}' does not exist`);
            return false;
        }
        
        const index = this.data[collection].findIndex(item => item.id === id);
        if (index === -1) {
            console.warn(`Item with id '${id}' not found in collection '${collection}'`);
            return false;
        }
        
        const updatedItem = {
            ...this.data[collection][index],
            ...updates,
            updatedAt: Date.now()
        };
        
        this.data[collection][index] = updatedItem;
        this.markDirty();
        this.dispatchEvent('dataChanged', { collection, action: 'update', item: updatedItem });
        return updatedItem;
    }
    
    remove(collection, id) {
        if (!this.data[collection]) {
            console.warn(`Collection '${collection}' does not exist`);
            return false;
        }
        
        const index = this.data[collection].findIndex(item => item.id === id);
        if (index === -1) {
            console.warn(`Item with id '${id}' not found in collection '${collection}'`);
            return false;
        }
        
        const removedItem = this.data[collection].splice(index, 1)[0];
        this.markDirty();
        this.dispatchEvent('dataChanged', { collection, action: 'remove', item: removedItem });
        return removedItem;
    }
    
    // Query methods
    find(collection, predicate) {
        if (!this.data[collection]) {
            return [];
        }
        
        return this.data[collection].filter(predicate);
    }
    
    findOne(collection, predicate) {
        if (!this.data[collection]) {
            return null;
        }
        
        return this.data[collection].find(predicate) || null;
    }
    
    count(collection, predicate = null) {
        if (!this.data[collection]) {
            return 0;
        }
        
        if (!predicate) {
            return this.data[collection].length;
        }
        
        return this.data[collection].filter(predicate).length;
    }
    
    // Utility methods
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    markDirty() {
        this.isDirty = true;
    }
    
    export() {
        return JSON.stringify(this.data, null, 2);
    }
    
    import(dataJson) {
        try {
            const imported = JSON.parse(dataJson);
            this.data = { ...this.data, ...imported };
            this.markDirty();
            this.saveData();
            this.dispatchEvent('dataImported');
            return true;
        } catch (e) {
            console.error('Invalid data format:', e);
            return false;
        }
    }
    
    clear() {
        const collections = Object.keys(this.data);
        collections.forEach(collection => {
            if (Array.isArray(this.data[collection])) {
                this.data[collection] = [];
            }
        });
        
        this.markDirty();
        this.dispatchEvent('dataCleared');
    }
    
    loadDemoData() {
        // Load sample data for demonstration
        this.data.rooms = [
            { id: '1', number: '101', type: 'Single Deluxe', status: 'available', price: 150 },
            { id: '2', number: '102', type: 'Double Superior', status: 'occupied', price: 220 },
            { id: '3', number: '201', type: 'Executive Suite', status: 'available', price: 450 },
            { id: '4', number: '301', type: 'Presidential Suite', status: 'maintenance', price: 850 }
        ];
        
        this.data.guests = [
            { id: '1', name: 'John Smith', email: 'john@example.com', phone: '+1-555-0123', nationality: 'US' },
            { id: '2', name: 'Emma Wilson', email: 'emma@example.com', phone: '+1-555-0456', nationality: 'UK' },
            { id: '3', name: 'Michael Chen', email: 'michael@example.com', phone: '+1-555-0789', nationality: 'CA' }
        ];
        
        this.data.bookings = [
            { id: '1', guestId: '1', roomId: '1', checkIn: '2024-01-15', checkOut: '2024-01-18', status: 'confirmed' },
            { id: '2', guestId: '2', roomId: '2', checkIn: '2024-01-16', checkOut: '2024-01-20', status: 'checked-in' },
            { id: '3', guestId: '3', roomId: '3', checkIn: '2024-01-17', checkOut: '2024-01-19', status: 'pending' }
        ];
        
        this.markDirty();
    }
    
    // Event system
    dispatchEvent(type, data = {}) {
        const event = new CustomEvent('dataManagerEvent', {
            detail: { type, data, timestamp: Date.now() }
        });
        document.dispatchEvent(event);
    }
    
    // Status getters
    isDataDirty() {
        return this.isDirty;
    }
    
    isDataLoading() {
        return this.isLoading;
    }
    
    isDataSaving() {
        return this.isSaving;
    }
    
    getLastModified() {
        return this.data.lastModified;
    }
}

// Export singleton instance
window.dataManager = new DataManager();