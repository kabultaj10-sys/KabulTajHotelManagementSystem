/**
 * Navigation Management System
 * Handles module switching, sidebar functionality, and responsive navigation
 */

class NavigationManager {
    constructor() {
        this.currentModule = 'hotel';
        this.sidebar = null;
        this.sidebarOverlay = null;
        this.menuToggle = null;
        this.sidebarClose = null;
        this.navItems = [];
        this.modules = [];
        this.isSidebarOpen = false;
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupNavigation());
        } else {
            this.setupNavigation();
        }
    }
    
    setupNavigation() {
        this.cacheElements();
        this.setupEventListeners();
        this.setupResponsiveNavigation();
        this.showModule(this.currentModule);
    }
    
    cacheElements() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarOverlay = document.getElementById('sidebarOverlay');
        this.menuToggle = document.getElementById('menuToggle');
        this.sidebarClose = document.getElementById('sidebarClose');
        this.navItems = Array.from(document.querySelectorAll('.nav-item[data-module]'));
        this.modules = Array.from(document.querySelectorAll('.module[id$="-module"]'));
    }
    
    setupEventListeners() {
        // Navigation item clicks - now using href links
        this.navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                // Let the default link behavior work for navigation
                // Close sidebar on mobile after navigation
                if (window.innerWidth <= 1024) {
                    this.closeSidebar();
                }
            });
        });
        
        // Mobile menu toggle
        if (this.menuToggle) {
            this.menuToggle.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }
        
        // Sidebar close button
        if (this.sidebarClose) {
            this.sidebarClose.addEventListener('click', () => {
                this.closeSidebar();
            });
        }
        
        // Overlay click to close sidebar
        if (this.sidebarOverlay) {
            this.sidebarOverlay.addEventListener('click', () => {
                this.closeSidebar();
            });
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });
        
        // Window resize handling
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        // Handle browser back/forward buttons
        window.addEventListener('popstate', (e) => {
            const module = e.state?.module || this.getModuleFromURL();
            if (module && module !== this.currentModule) {
                this.showModule(module, false);
            }
        });
    }
    
    setupResponsiveNavigation() {
        // Set initial sidebar state based on screen size
        this.handleResize();
        
        // Add swipe gestures for mobile
        this.setupSwipeGestures();
    }
    
    switchToModule(module) {
        if (module === this.currentModule) return;
        
        // Update URL without triggering page reload
        this.updateURL(module);
        
        // Show the module
        this.showModule(module, true);
    }
    
    showModule(module, pushState = true) {
        // Show selected module first
        const targetModule = document.getElementById(`${module}-module`);
        if (targetModule) {
            // Show the module first
            targetModule.classList.remove('hidden');
            
            // Then hide all other modules
            this.modules.forEach(moduleEl => {
                if (moduleEl !== targetModule) {
                    moduleEl.classList.add('hidden');
                }
            });
            
            // Update navigation state
            this.updateNavigationState(module);
            
            // Update current module
            this.currentModule = module;
            
            // Push state to history
            if (pushState) {
                history.pushState({ module }, '', `#${module}`);
            }
            
            // Dispatch module change event
            this.dispatchModuleChangeEvent(module);
        }
    }
    
    updateNavigationState(module) {
        // Update active navigation item
        this.navItems.forEach(item => {
            const itemModule = item.getAttribute('data-module');
            if (itemModule === module) {
                item.classList.add('active');
                item.setAttribute('aria-current', 'page');
            } else {
                item.classList.remove('active');
                item.removeAttribute('aria-current');
            }
        });
    }
    
    updateURL(module) {
        // Update URL hash without scrolling
        history.replaceState({ module }, '', `#${module}`);
    }
    
    getModuleFromURL() {
        const hash = window.location.hash.slice(1);
        const validModules = ['hotel', 'restaurant', 'inventory', 'users', 'billing'];
        return validModules.includes(hash) ? hash : 'hotel';
    }
    
    toggleSidebar() {
        if (this.isSidebarOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }
    
    openSidebar() {
        if (!this.sidebar || !this.sidebarOverlay) return;
        
        this.sidebar.classList.add('open');
        this.sidebarOverlay.classList.add('active');
        this.isSidebarOpen = true;
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Focus first navigation item for accessibility
        const firstNavItem = this.navItems[0];
        if (firstNavItem) {
            setTimeout(() => firstNavItem.focus(), 150);
        }
        
        // Add escape key listener
        document.addEventListener('keydown', this.handleEscapeKey);
    }
    
    closeSidebar() {
        if (!this.sidebar || !this.sidebarOverlay) return;
        
        this.sidebar.classList.remove('open');
        this.sidebarOverlay.classList.remove('active');
        this.isSidebarOpen = false;
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Return focus to menu toggle
        if (this.menuToggle) {
            this.menuToggle.focus();
        }
        
        // Remove escape key listener
        document.removeEventListener('keydown', this.handleEscapeKey);
    }
    
    handleEscapeKey = (e) => {
        if (e.key === 'Escape') {
            this.closeSidebar();
        }
    }
    
    handleResize() {
        const isDesktop = window.innerWidth > 1024;
        
        if (isDesktop) {
            // Desktop: always show sidebar, remove mobile states
            this.closeSidebar();
            document.body.style.overflow = '';
        } else {
            // Mobile: ensure sidebar is properly positioned
            if (this.isSidebarOpen) {
                document.body.style.overflow = 'hidden';
            }
        }
    }
    
    handleKeyboardNavigation(e) {
        // Module switching with number keys (1-5)
        if (e.ctrlKey || e.metaKey) {
            const moduleKeys = {
                '1': 'hotel',
                '2': 'restaurant',
                '3': 'inventory',
                '4': 'users',
                '5': 'billing'
            };
            
            if (moduleKeys[e.key]) {
                e.preventDefault();
                this.switchToModule(moduleKeys[e.key]);
            }
        }
        
        // Sidebar toggle with M key
        if ((e.ctrlKey || e.metaKey) && e.key === 'm') {
            e.preventDefault();
            this.toggleSidebar();
        }
        
        // Arrow key navigation within sidebar
        if (this.isSidebarOpen && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
            e.preventDefault();
            this.navigateWithArrows(e.key);
        }
    }
    
    navigateWithArrows(direction) {
        const focusedElement = document.activeElement;
        const currentIndex = this.navItems.indexOf(focusedElement);
        
        if (currentIndex === -1) return;
        
        let nextIndex;
        if (direction === 'ArrowDown') {
            nextIndex = (currentIndex + 1) % this.navItems.length;
        } else {
            nextIndex = currentIndex === 0 ? this.navItems.length - 1 : currentIndex - 1;
        }
        
        this.navItems[nextIndex].focus();
    }
    
    setupSwipeGestures() {
        let startX = 0;
        let startY = 0;
        let endX = 0;
        let endY = 0;
        
        const minSwipeDistance = 50;
        const maxVerticalDistance = 100;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            if (!e.changedTouches[0]) return;
            
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = Math.abs(endY - startY);
            
            // Only handle horizontal swipes
            if (deltaY > maxVerticalDistance) return;
            
            // Swipe right to open sidebar
            if (deltaX > minSwipeDistance && startX < 50 && !this.isSidebarOpen) {
                this.openSidebar();
            }
            
            // Swipe left to close sidebar
            if (deltaX < -minSwipeDistance && this.isSidebarOpen) {
                this.closeSidebar();
            }
        }, { passive: true });
    }
    

    
    dispatchModuleChangeEvent(module) {
        const event = new CustomEvent('modulechange', {
            detail: { 
                module, 
                previousModule: this.currentModule,
                timestamp: Date.now()
            }
        });
        document.dispatchEvent(event);
    }
    
    // Public API methods
    getCurrentModule() {
        return this.currentModule;
    }
    
    goToModule(module) {
        this.switchToModule(module);
    }
    
    isMobileView() {
        return window.innerWidth <= 1024;
    }
    
    getSidebarState() {
        return this.isSidebarOpen;
    }
}

// Initialize navigation manager
window.navigationManager = new NavigationManager();

// Module change event listener
document.addEventListener('modulechange', (e) => {
    console.log(`Module changed to: ${e.detail.module}`);
    
    // Add custom logic here for module-specific initialization
    // For example, loading module-specific data, updating analytics, etc.
});

// Export for global access
window.NavigationManager = NavigationManager;

// Console utilities
if (typeof window !== 'undefined' && window.console) {
    window.console.info('🧭 Navigation Manager loaded. Available commands:');
    window.console.info('- navigationManager.goToModule("hotel")');
    window.console.info('- navigationManager.toggleSidebar()');
    window.console.info('- navigationManager.getCurrentModule()');
}