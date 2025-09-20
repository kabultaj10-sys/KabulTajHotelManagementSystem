/**
 * Main Application Controller
 * Initializes the hotel management system and coordinates all modules
 */

class HotelManagementApp {
    constructor() {
        this.version = '1.0.0';
        this.initialized = false;
        this.startTime = Date.now();
        
        this.init();
    }
    
    async init() {
        try {
            console.log('🏨 Initializing Kabul Taj Hotel Management System...');
            
            // Wait for DOM to be ready
            await this.waitForDOM();
            
            // Initialize core systems
            await this.initializeCoreModules();
            
            // Setup application features
            this.setupFeatures();
            
            // Initialize UI components
            this.initializeUI();
            
            // Setup periodic tasks
            this.setupPeriodicTasks();
            
            // Mark as initialized
            this.initialized = true;
            
            // Dispatch ready event
            this.dispatchReadyEvent();
            
            // Log initialization complete
            const initTime = Date.now() - this.startTime;
            console.log(`✅ Hotel Management System initialized in ${initTime}ms`);
            
        } catch (error) {
            console.error('❌ Failed to initialize application:', error);
            this.handleInitializationError(error);
        }
    }
    
    waitForDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }
    
    async initializeCoreModules() {
        // Configuration manager should already be loaded
        if (!window.configManager) {
            throw new Error('Configuration manager not available');
        }
        
        // Data manager should already be loaded
        if (!window.dataManager) {
            throw new Error('Data manager not available');
        }
        
        // Error handler should already be loaded
        if (!window.errorHandler) {
            throw new Error('Error handler not available');
        }
        
        // Theme manager should already be loaded
        if (!window.themeManager) {
            throw new Error('Theme manager not available');
        }
        
        // Navigation manager should already be loaded
        if (!window.navigationManager) {
            throw new Error('Navigation manager not available');
        }
        
        // Component manager should already be loaded
        if (!window.componentManager) {
            throw new Error('Component manager not available');
        }
        
        console.log('✅ All core modules loaded successfully');
    }
    
    setupFeatures() {
        this.setupKeyboardShortcuts();
        this.setupAccessibility();
        this.setupServiceWorker();
        this.setupAnalytics();
        this.setupNotifications();
    }
    
    setupKeyboardShortcuts() {
        if (!window.configManager.get('keyboardShortcuts')) return;
        
        const shortcuts = {
            // Theme toggle: Ctrl/Cmd + Shift + T
            'ctrl+shift+t': () => window.themeManager?.toggleTheme(),
            
            // Save: Ctrl/Cmd + S
            'ctrl+s': (e) => {
                e.preventDefault();
                window.dataManager?.saveData();
                this.showToast('Data saved successfully');
            },
            
            // Search: Ctrl/Cmd + K
            'ctrl+k': (e) => {
                e.preventDefault();
                const searchInput = document.querySelector('.search-input');
                searchInput?.focus();
            },
            
            // Help: F1 or ?
            'f1': () => this.showHelp(),
            '?': () => this.showHelp(),
            
            // Module navigation: Ctrl/Cmd + 1-5
            'ctrl+1': () => window.navigationManager?.goToModule('hotel'),
            'ctrl+2': () => window.navigationManager?.goToModule('restaurant'),
            'ctrl+3': () => window.navigationManager?.goToModule('inventory'),
            'ctrl+4': () => window.navigationManager?.goToModule('users'),
            'ctrl+5': () => window.navigationManager?.goToModule('billing'),
        };
        
        document.addEventListener('keydown', (e) => {
            const key = this.getShortcutKey(e);
            const handler = shortcuts[key];
            
            if (handler) {
                handler(e);
            }
        });
        
        console.log('⌨️ Keyboard shortcuts enabled');
    }
    
    getShortcutKey(e) {
        const parts = [];
        
        if (e.ctrlKey || e.metaKey) parts.push('ctrl');
        if (e.shiftKey) parts.push('shift');
        if (e.altKey) parts.push('alt');
        
        parts.push(e.key.toLowerCase());
        
        return parts.join('+');
    }
    
    setupAccessibility() {
        // Skip links for keyboard navigation
        this.addSkipLinks();
        
        // ARIA live regions for announcements
        this.addLiveRegions();
        
        // Focus management
        this.setupFocusManagement();
        
        // High contrast mode detection
        this.detectHighContrast();
        
        console.log('♿ Accessibility features enabled');
    }
    
    addSkipLinks() {
        const skipNav = document.createElement('a');
        skipNav.href = '#main-content';
        skipNav.className = 'skip-link';
        skipNav.textContent = 'Skip to main content';
        skipNav.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: var(--color-primary);
            color: var(--color-primary-foreground);
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 10000;
            transition: top 0.3s;
        `;
        
        skipNav.addEventListener('focus', () => {
            skipNav.style.top = '6px';
        });
        
        skipNav.addEventListener('blur', () => {
            skipNav.style.top = '-40px';
        });
        
        document.body.insertBefore(skipNav, document.body.firstChild);
        
        // Add ID to main content
        const mainContent = document.querySelector('.module-container');
        if (mainContent) {
            mainContent.id = 'main-content';
        }
    }
    
    addLiveRegions() {
        const liveRegion = document.createElement('div');
        liveRegion.id = 'live-region';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        
        document.body.appendChild(liveRegion);
        
        // Make it available globally
        window.announceToScreenReader = (message) => {
            liveRegion.textContent = message;
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        };
    }
    
    setupFocusManagement() {
        // Trap focus in modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                const modal = document.querySelector('.modal.open, .dialog[open]');
                if (modal) {
                    this.trapFocus(e, modal);
                }
            }
        });
    }
    
    trapFocus(e, container) {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
        }
    }
    
    detectHighContrast() {
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            document.documentElement.classList.add('high-contrast');
        }
    }
    
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then((registration) => {
                    console.log('📱 Service Worker registered:', registration);
                })
                .catch((error) => {
                    console.warn('Service Worker registration failed:', error);
                });
        }
    }
    
    setupAnalytics() {
        // Placeholder for analytics initialization
        // In a real application, you would initialize your analytics service here
        console.log('📊 Analytics placeholder initialized');
    }
    
    setupNotifications() {
        if (!window.configManager.get('notifications')) return;
        
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                Notification.requestPermission().then((permission) => {
                    console.log(`🔔 Notification permission: ${permission}`);
                });
            }
        }
    }
    
    initializeUI() {
        // Add loading state management
        this.setupLoadingStates();
        
        // Initialize tooltips
        this.initializeTooltips();
        
        // Setup contextual help
        this.setupContextualHelp();
        
        console.log('🎨 UI components initialized');
    }
    
    setupLoadingStates() {
        // Global loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.id = 'global-loading';
        loadingIndicator.className = 'loading-indicator hidden';
        loadingIndicator.innerHTML = `
            <div class="loading-spinner"></div>
            <span class="loading-text">Loading...</span>
        `;
        
        document.body.appendChild(loadingIndicator);
        
        // Make it available globally
        window.showGlobalLoading = (text = 'Loading...') => {
            loadingIndicator.querySelector('.loading-text').textContent = text;
            loadingIndicator.classList.remove('hidden');
        };
        
        window.hideGlobalLoading = () => {
            loadingIndicator.classList.add('hidden');
        };
    }
    
    initializeTooltips() {
        if (!window.configManager.get('showTooltips')) return;
        
        // Enhanced tooltip system is handled by component manager
        console.log('💬 Tooltips enabled');
    }
    
    setupContextualHelp() {
        // Add help button to each module
        const modules = document.querySelectorAll('.module');
        
        modules.forEach((module) => {
            const header = module.querySelector('.module-header');
            if (header) {
                const helpBtn = document.createElement('button');
                helpBtn.className = 'btn-ghost help-btn';
                helpBtn.innerHTML = '?';
                helpBtn.title = 'Get help for this section';
                helpBtn.addEventListener('click', () => {
                    this.showModuleHelp(module.id);
                });
                
                header.appendChild(helpBtn);
            }
        });
    }
    
    setupPeriodicTasks() {
        // Data backup every 5 minutes
        setInterval(() => {
            if (window.dataManager?.isDataDirty()) {
                window.dataManager.saveData();
            }
        }, 5 * 60 * 1000);
        
        // Performance monitoring
        setInterval(() => {
            this.checkPerformance();
        }, 30 * 1000);
        
        console.log('⏰ Periodic tasks scheduled');
    }
    
    checkPerformance() {
        const memory = performance.memory;
        if (memory && memory.usedJSHeapSize > 50 * 1024 * 1024) { // 50MB
            console.warn('High memory usage detected:', memory.usedJSHeapSize);
        }
    }
    
    dispatchReadyEvent() {
        const event = new CustomEvent('appReady', {
            detail: {
                version: this.version,
                initTime: Date.now() - this.startTime,
                features: this.getEnabledFeatures()
            }
        });
        
        document.dispatchEvent(event);
    }
    
    getEnabledFeatures() {
        return {
            autoSave: window.configManager.get('autoSave'),
            animations: window.configManager.get('animations'),
            notifications: window.configManager.get('notifications'),
            keyboardShortcuts: window.configManager.get('keyboardShortcuts'),
            tooltips: window.configManager.get('showTooltips')
        };
    }
    
    handleInitializationError(error) {
        console.error('Initialization failed:', error);
        
        // Show fallback UI
        document.body.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh; text-align: center; font-family: sans-serif;">
                <div>
                    <h1>🚨 Application Error</h1>
                    <p>The hotel management system failed to initialize.</p>
                    <p>Please refresh the page or contact support.</p>
                    <button onclick="location.reload()" style="margin-top: 20px; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Refresh Page
                    </button>
                </div>
            </div>
        `;
    }
    
    // Utility methods
    showToast(message, type = 'info') {
        if (window.componentManager?.showNotification) {
            window.componentManager.showNotification(message, type);
        } else {
            console.log(`Toast: ${message}`);
        }
    }
    
    showHelp() {
        const currentModule = window.navigationManager?.getCurrentModule() || 'general';
        this.showModuleHelp(currentModule);
    }
    
    showModuleHelp(moduleId) {
        const helpContent = this.getHelpContent(moduleId);
        
        // Create help modal
        const modal = document.createElement('div');
        modal.className = 'help-modal';
        modal.innerHTML = `
            <div class="help-content">
                <h2>Help: ${helpContent.title}</h2>
                <div class="help-body">${helpContent.content}</div>
                <button class="btn btn-primary close-help">Close</button>
            </div>
        `;
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('close-help')) {
                modal.remove();
            }
        });
        
        document.body.appendChild(modal);
    }
    
    getHelpContent(moduleId) {
        const helpData = {
            hotel: {
                title: 'Hotel & Reservations',
                content: `
                    <p>This module helps you manage room bookings and guest information.</p>
                    <ul>
                        <li><strong>Room Availability:</strong> View and manage room status</li>
                        <li><strong>Bookings:</strong> Create and manage reservations</li>
                        <li><strong>Guest Management:</strong> Store guest information and preferences</li>
                        <li><strong>Pricing:</strong> Set seasonal rates and promotions</li>
                    </ul>
                `
            },
            restaurant: {
                title: 'Restaurant & Food Services',
                content: `
                    <p>Manage dining operations and food orders.</p>
                    <ul>
                        <li><strong>Table Reservations:</strong> Book tables for guests</li>
                        <li><strong>Orders:</strong> Manage food orders and kitchen operations</li>
                        <li><strong>Menu Management:</strong> Update menu items and pricing</li>
                        <li><strong>Room Service:</strong> Handle in-room dining requests</li>
                    </ul>
                `
            },
            inventory: {
                title: 'Inventory & Freezer Management',
                content: `
                    <p>Monitor stock levels and freezer operations.</p>
                    <ul>
                        <li><strong>Stock Tracking:</strong> Monitor inventory levels</li>
                        <li><strong>Freezer Status:</strong> Check temperature and capacity</li>
                        <li><strong>Purchasing:</strong> Manage vendor orders</li>
                        <li><strong>Alerts:</strong> Receive low stock notifications</li>
                    </ul>
                `
            },
            users: {
                title: 'Staff & User Management',
                content: `
                    <p>Manage staff accounts and permissions.</p>
                    <ul>
                        <li><strong>Staff Directory:</strong> Manage employee information</li>
                        <li><strong>Roles:</strong> Set user permissions and access levels</li>
                        <li><strong>Activity Log:</strong> Track staff actions</li>
                        <li><strong>Task Assignment:</strong> Assign and track tasks</li>
                    </ul>
                `
            },
            billing: {
                title: 'Orders & Billing',
                content: `
                    <p>Handle payments and financial transactions.</p>
                    <ul>
                        <li><strong>Invoicing:</strong> Generate bills and invoices</li>
                        <li><strong>Payment Methods:</strong> Process different payment types</li>
                        <li><strong>Revenue Tracking:</strong> Monitor financial performance</li>
                        <li><strong>Tax Configuration:</strong> Set up taxes and discounts</li>
                    </ul>
                `
            },
            general: {
                title: 'General Help',
                content: `
                    <h3>Keyboard Shortcuts:</h3>
                    <ul>
                        <li><kbd>Ctrl+S</kbd> - Save data</li>
                        <li><kbd>Ctrl+K</kbd> - Focus search</li>
                        <li><kbd>Ctrl+1-5</kbd> - Switch modules</li>
                        <li><kbd>Ctrl+Shift+T</kbd> - Toggle theme</li>
                        <li><kbd>F1</kbd> or <kbd>?</kbd> - Show help</li>
                    </ul>
                    
                    <h3>Navigation:</h3>
                    <p>Use the sidebar to navigate between different modules. On mobile, tap the menu button to open the sidebar.</p>
                `
            }
        };
        
        return helpData[moduleId] || helpData.general;
    }
    
    // Public API
    getVersion() {
        return this.version;
    }
    
    isInitialized() {
        return this.initialized;
    }
    
    getInitTime() {
        return Date.now() - this.startTime;
    }
    
    restart() {
        location.reload();
    }
}

// Main Application
class HotelManagementSystem {
    constructor() {
        this.initializeComponents();
        this.setupEventListeners();
    }

    initializeComponents() {
        // Initialize all components
        this.navigation = new Navigation();
        this.theme = new Theme();
        this.components = new Components();
        
        // Initialize data manager
        this.dataManager = new DataManager();
        
        // Initialize error handler
        this.errorHandler = new ErrorHandler();
    }

    setupEventListeners() {
        // Booking modal functionality
        const newBookingBtn = document.getElementById('newBookingBtn');
        const bookingModal = document.getElementById('bookingModal');
        const closeBookingModal = document.getElementById('closeBookingModal');
        const cancelBooking = document.getElementById('cancelBooking');
        const confirmBooking = document.getElementById('confirmBooking');

        if (newBookingBtn) {
            newBookingBtn.addEventListener('click', () => {
                bookingModal.classList.add('show');
            });
        }

        if (closeBookingModal) {
            closeBookingModal.addEventListener('click', () => {
                bookingModal.classList.remove('show');
            });
        }

        if (cancelBooking) {
            cancelBooking.addEventListener('click', () => {
                bookingModal.classList.remove('show');
            });
        }

        if (confirmBooking) {
            confirmBooking.addEventListener('click', () => {
                // Handle booking confirmation
                bookingModal.classList.remove('show');
                this.showNotification('Booking confirmed successfully!', 'success');
            });
        }

        // Conference room booking modal functionality
        const newConferenceBookingBtn = document.getElementById('newConferenceBookingBtn');
        const conferenceBookingModal = document.getElementById('conferenceBookingModal');
        const closeConferenceModal = document.getElementById('closeConferenceModal');
        const cancelConferenceBooking = document.getElementById('cancelConferenceBooking');
        const confirmConferenceBooking = document.getElementById('confirmConferenceBooking');

        if (newConferenceBookingBtn) {
            newConferenceBookingBtn.addEventListener('click', () => {
                conferenceBookingModal.classList.add('show');
            });
        }

        if (closeConferenceModal) {
            closeConferenceModal.addEventListener('click', () => {
                conferenceBookingModal.classList.remove('show');
            });
        }

        if (cancelConferenceBooking) {
            cancelConferenceBooking.addEventListener('click', () => {
                conferenceBookingModal.classList.remove('show');
            });
        }

        if (confirmConferenceBooking) {
            confirmConferenceBooking.addEventListener('click', () => {
                // Handle conference booking confirmation
                conferenceBookingModal.classList.remove('show');
                this.showNotification('Conference room booking confirmed!', 'success');
            });
        }

        // Conference room booking buttons
        const bookNowButtons = document.querySelectorAll('.conference-room .btn-primary');
        bookNowButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                conferenceBookingModal.classList.add('show');
            });
        });

        // Conference room filters
        const roomFilter = document.getElementById('roomFilter');
        const dateFilter = document.getElementById('dateFilter');
        const statusFilter = document.getElementById('statusFilter');

        if (roomFilter) {
            roomFilter.addEventListener('change', () => {
                this.filterConferenceRooms();
            });
        }

        if (dateFilter) {
            dateFilter.addEventListener('change', () => {
                this.filterConferenceRooms();
            });
        }

        if (statusFilter) {
            statusFilter.addEventListener('change', () => {
                this.filterConferenceRooms();
            });
        }

        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.remove('show');
            }
        });

        // Equipment checkboxes functionality
        const equipmentCheckboxes = document.querySelectorAll('.equipment-checkboxes input[type="checkbox"]');
        equipmentCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateEquipmentSelection();
            });
        });
    }

    filterConferenceRooms() {
        const roomFilter = document.getElementById('roomFilter');
        const dateFilter = document.getElementById('dateFilter');
        const statusFilter = document.getElementById('statusFilter');
        const conferenceRooms = document.querySelectorAll('.conference-room');

        const selectedRoom = roomFilter ? roomFilter.value : 'All Rooms';
        const selectedDate = dateFilter ? dateFilter.value : '';
        const selectedStatus = statusFilter ? statusFilter.value : 'All Status';

        conferenceRooms.forEach(room => {
            let show = true;

            // Filter by room name
            if (selectedRoom !== 'All Rooms') {
                const roomName = room.querySelector('h5').textContent;
                if (roomName !== selectedRoom) {
                    show = false;
                }
            }

            // Filter by status
            if (selectedStatus !== 'All Status') {
                const roomStatus = room.querySelector('.room-status').textContent.toLowerCase();
                const filterStatus = selectedStatus.toLowerCase();
                if (roomStatus !== filterStatus && roomStatus !== filterStatus.replace('-', '')) {
                    show = false;
                }
            }

            // Show/hide room based on filters
            room.style.display = show ? 'block' : 'none';
        });
    }

    updateEquipmentSelection() {
        const selectedEquipment = [];
        const equipmentCheckboxes = document.querySelectorAll('.equipment-checkboxes input[type="checkbox"]:checked');
        
        equipmentCheckboxes.forEach(checkbox => {
            selectedEquipment.push(checkbox.id);
        });

        // You can add logic here to update pricing or availability based on equipment selection
        console.log('Selected equipment:', selectedEquipment);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span>${message}</span>
                <button class="notification-close">×</button>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 5000);

        // Close button functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HotelManagementSystem();
});

// Add help modal styles
const helpStyles = document.createElement('style');
helpStyles.textContent = `
    .help-modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        padding: 20px;
    }
    
    .help-content {
        background: var(--color-card);
        border-radius: var(--radius-lg);
        padding: 32px;
        max-width: 600px;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: var(--shadow-xl);
    }
    
    .help-content h2 {
        color: var(--color-gold-primary);
        margin-bottom: 16px;
    }
    
    .help-content h3 {
        color: var(--color-foreground);
        margin-top: 24px;
        margin-bottom: 12px;
    }
    
    .help-content ul {
        margin-left: 20px;
        margin-bottom: 16px;
    }
    
    .help-content li {
        margin-bottom: 8px;
        color: var(--color-foreground);
    }
    
    .help-content kbd {
        background: var(--color-muted);
        padding: 2px 6px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9em;
    }
    
    .close-help {
        margin-top: 24px;
    }
    
    .loading-indicator {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--color-card);
        padding: 32px;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        z-index: 10000;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
    }
    
    .loading-spinner {
        width: 32px;
        height: 32px;
        border: 3px solid var(--color-muted);
        border-top: 3px solid var(--color-gold-primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .help-btn {
        position: absolute;
        top: 16px;
        right: 16px;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 16px;
    }
`;

document.head.appendChild(helpStyles);

console.info('🚀 Main application controller loaded');