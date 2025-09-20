/**
 * Error Handling System
 * Centralized error handling, logging, and user feedback
 */

class ErrorHandler {
    constructor() {
        this.errors = [];
        this.maxErrors = 100;
        this.isInitialized = false;
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.setupGlobalErrorHandlers();
        this.setupUnhandledRejectionHandler();
        this.isInitialized = true;
    }
    
    setupGlobalErrorHandlers() {
        // JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleError({
                type: 'javascript',
                message: event.message,
                filename: event.filename,
                line: event.lineno,
                column: event.colno,
                error: event.error,
                stack: event.error?.stack
            });
        });
        
        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError({
                type: 'promise',
                message: event.reason?.message || 'Unhandled promise rejection',
                reason: event.reason,
                stack: event.reason?.stack
            });
        });
        
        // Network errors (for fetch requests)
        this.setupNetworkErrorHandling();
    }
    
    setupUnhandledRejectionHandler() {
        const originalFetch = window.fetch;
        
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch(...args);
                
                if (!response.ok) {
                    this.handleError({
                        type: 'network',
                        message: `HTTP ${response.status}: ${response.statusText}`,
                        url: args[0],
                        status: response.status,
                        statusText: response.statusText
                    });
                }
                
                return response;
            } catch (error) {
                this.handleError({
                    type: 'network',
                    message: `Network error: ${error.message}`,
                    url: args[0],
                    error
                });
                throw error;
            }
        };
    }
    
    setupNetworkErrorHandling() {
        // Monitor XMLHttpRequest errors
        const originalXHR = window.XMLHttpRequest;
        
        window.XMLHttpRequest = function() {
            const xhr = new originalXHR();
            const originalOpen = xhr.open;
            const originalSend = xhr.send;
            
            let requestInfo = {};
            
            xhr.open = function(method, url, ...args) {
                requestInfo = { method, url };
                return originalOpen.call(this, method, url, ...args);
            };
            
            xhr.send = function(...args) {
                xhr.addEventListener('error', () => {
                    window.errorHandler.handleError({
                        type: 'xhr',
                        message: 'XMLHttpRequest error',
                        ...requestInfo,
                        status: xhr.status,
                        statusText: xhr.statusText
                    });
                });
                
                return originalSend.call(this, ...args);
            };
            
            return xhr;
        };
    }
    
    handleError(errorInfo) {
        const errorData = {
            id: this.generateErrorId(),
            timestamp: Date.now(),
            userAgent: navigator.userAgent,
            url: window.location.href,
            ...errorInfo
        };
        
        // Add to error log
        this.addToErrorLog(errorData);
        
        // Log to console
        this.logToConsole(errorData);
        
        // Send to analytics (if available)
        this.sendToAnalytics(errorData);
        
        // Show user notification for critical errors
        if (this.isCriticalError(errorData)) {
            this.showUserNotification(errorData);
        }
        
        // Dispatch error event
        this.dispatchErrorEvent(errorData);
    }
    
    addToErrorLog(errorData) {
        this.errors.unshift(errorData);
        
        // Keep only the most recent errors
        if (this.errors.length > this.maxErrors) {
            this.errors = this.errors.slice(0, this.maxErrors);
        }
        
        // Save to localStorage for persistence
        try {
            localStorage.setItem('kabul-taj-errors', JSON.stringify(this.errors.slice(0, 10)));
        } catch (e) {
            console.warn('Could not save error log to localStorage');
        }
    }
    
    logToConsole(errorData) {
        const { type, message, stack } = errorData;
        
        console.group(`🚨 ${type.toUpperCase()} Error`);
        console.error(message);
        
        if (stack) {
            console.error(stack);
        }
        
        console.table(errorData);
        console.groupEnd();
    }
    
    sendToAnalytics(errorData) {
        // Placeholder for analytics integration
        // In a real application, you would send this to your analytics service
        console.debug('Error sent to analytics:', errorData);
    }
    
    isCriticalError(errorData) {
        const criticalTypes = ['network', 'security'];
        const criticalMessages = ['chunk', 'module', 'syntax'];
        
        return criticalTypes.includes(errorData.type) ||
               criticalMessages.some(keyword => 
                   errorData.message.toLowerCase().includes(keyword)
               );
    }
    
    showUserNotification(errorData) {
        const message = this.getUserFriendlyMessage(errorData);
        
        if (window.componentManager?.showNotification) {
            window.componentManager.showNotification(message, 'error');
        } else {
            // Fallback notification
            this.showFallbackNotification(message);
        }
    }
    
    getUserFriendlyMessage(errorData) {
        switch (errorData.type) {
            case 'network':
                return 'Network connection issue. Please check your internet connection.';
            case 'javascript':
                return 'An unexpected error occurred. The page may need to be refreshed.';
            case 'promise':
                return 'A background operation failed. Some features may not work correctly.';
            default:
                return 'An error occurred. Please try again or contact support if the problem persists.';
        }
    }
    
    showFallbackNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.innerHTML = `
            <div class="error-content">
                <span class="error-icon">⚠️</span>
                <span class="error-message">${message}</span>
                <button class="error-close">&times;</button>
            </div>
        `;
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--color-danger);
            color: var(--color-danger-foreground);
            padding: 16px;
            border-radius: 8px;
            box-shadow: var(--shadow-lg);
            z-index: 10000;
            max-width: 400px;
            animation: slideIn 0.3s ease;
        `;
        
        // Add close functionality
        const closeBtn = notification.querySelector('.error-close');
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    dispatchErrorEvent(errorData) {
        const event = new CustomEvent('appError', {
            detail: errorData
        });
        document.dispatchEvent(event);
    }
    
    generateErrorId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    // Public API methods
    getErrors(type = null) {
        if (!type) {
            return [...this.errors];
        }
        
        return this.errors.filter(error => error.type === type);
    }
    
    getErrorCount(type = null) {
        return this.getErrors(type).length;
    }
    
    clearErrors() {
        this.errors = [];
        try {
            localStorage.removeItem('kabul-taj-errors');
        } catch (e) {
            console.warn('Could not clear error log from localStorage');
        }
    }
    
    exportErrors() {
        return JSON.stringify(this.errors, null, 2);
    }
    
    // Manual error reporting
    reportError(message, type = 'manual', additionalData = {}) {
        this.handleError({
            type,
            message,
            ...additionalData
        });
    }
    
    // Performance monitoring
    measurePerformance(name, fn) {
        const start = performance.now();
        
        try {
            const result = fn();
            
            // Handle promises
            if (result && typeof result.then === 'function') {
                return result.catch(error => {
                    this.handleError({
                        type: 'performance',
                        message: `Performance measurement '${name}' failed`,
                        duration: performance.now() - start,
                        error
                    });
                    throw error;
                });
            }
            
            const duration = performance.now() - start;
            
            // Log slow operations
            if (duration > 100) {
                console.warn(`Slow operation detected: ${name} took ${duration.toFixed(2)}ms`);
            }
            
            return result;
        } catch (error) {
            this.handleError({
                type: 'performance',
                message: `Performance measurement '${name}' failed`,
                duration: performance.now() - start,
                error
            });
            throw error;
        }
    }
}

// Export singleton instance
window.errorHandler = new ErrorHandler();

// Add CSS for error notifications
const errorStyles = document.createElement('style');
errorStyles.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .error-notification {
        font-family: inherit;
    }
    
    .error-content {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .error-icon {
        font-size: 20px;
    }
    
    .error-message {
        flex: 1;
        font-size: 14px;
    }
    
    .error-close {
        background: none;
        border: none;
        color: inherit;
        font-size: 20px;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
    }
    
    .error-close:hover {
        background: rgba(255, 255, 255, 0.2);
    }
`;

document.head.appendChild(errorStyles);