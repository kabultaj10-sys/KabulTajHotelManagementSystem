/**
 * Restaurant Billing Dashboard JavaScript
 * Enhances the billing dashboard with interactive features
 */

class RestaurantBillingDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.setupSearch();
        this.setupFilters();
        this.setupStatCards();
        this.setupSmoothScrolling();
        this.setupResponsiveTable();
        this.setupAnimations();
    }

    /**
     * Setup search functionality for invoices
     */
    setupSearch() {
        const searchInput = document.querySelector('.search-input');
        const tableRows = document.querySelectorAll('.table-body .table-row');
        
        if (searchInput && tableRows.length > 0) {
            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                
                tableRows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                        row.classList.add('search-highlight');
                    } else {
                        row.style.display = 'none';
                        row.classList.remove('search-highlight');
                    }
                });
                
                this.updateSearchResults(searchTerm, tableRows);
            });
        }
    }

    /**
     * Setup filter functionality for invoice status
     */
    setupFilters() {
        const filterSelect = document.querySelector('.filter-select');
        const tableRows = document.querySelectorAll('.table-body .table-row');
        
        if (filterSelect && tableRows.length > 0) {
            filterSelect.addEventListener('change', (e) => {
                const filterValue = e.target.value.toLowerCase();
                
                tableRows.forEach(row => {
                    const statusCell = row.querySelector('.status-badge');
                    if (statusCell) {
                        const status = statusCell.textContent.toLowerCase();
                        if (filterValue === '' || status.includes(filterValue)) {
                            row.style.display = '';
                        } else {
                            row.style.display = 'none';
                        }
                    }
                });
                
                this.updateFilterResults(filterValue, tableRows);
            });
        }
    }

    /**
     * Setup interactive stat cards
     */
    setupStatCards() {
        const statCards = document.querySelectorAll('.stat-card');
        
        statCards.forEach((card, index) => {
            // Add click functionality
            card.addEventListener('click', () => {
                this.handleStatCardClick(card, index);
            });
            
            // Add hover effects
            card.addEventListener('mouseenter', () => {
                this.animateStatCard(card, 'enter');
            });
            
            card.addEventListener('mouseleave', () => {
                this.animateStatCard(card, 'leave');
            });
        });
    }

    /**
     * Setup smooth scrolling for anchor links
     */
    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    /**
     * Setup responsive table behavior
     */
    setupResponsiveTable() {
        const table = document.querySelector('.invoice-table');
        if (table) {
            this.handleTableResponsiveness();
            window.addEventListener('resize', () => {
                this.handleTableResponsiveness();
            });
        }
    }

    /**
     * Setup animations and transitions
     */
    setupAnimations() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.stat-card, .summary-card, .content-card').forEach(el => {
            observer.observe(el);
        });
    }

    /**
     * Handle stat card clicks
     */
    handleStatCardClick(card, index) {
        const label = card.querySelector('.stat-label').textContent;
        const value = card.querySelector('.stat-number').textContent;
        
        console.log(`Stat card clicked: ${label} - ${value}`);
        
        // Add visual feedback
        card.style.transform = 'scale(0.95)';
        setTimeout(() => {
            card.style.transform = '';
        }, 150);
        
        // You can add navigation or modal functionality here
        this.showStatDetails(label, value);
    }

    /**
     * Animate stat cards on hover
     */
    animateStatCard(card, action) {
        if (action === 'enter') {
            card.style.transform = 'translateY(-8px) scale(1.02)';
            card.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
        } else {
            card.style.transform = 'translateY(0) scale(1)';
            card.style.boxShadow = '';
        }
    }

    /**
     * Update search results count
     */
    updateSearchResults(searchTerm, tableRows) {
        const visibleRows = Array.from(tableRows).filter(row => 
            row.style.display !== 'none'
        );
        
        // You can add a results counter here
        if (searchTerm && visibleRows.length > 0) {
            this.showSearchFeedback(`Found ${visibleRows.length} matching invoices`);
        }
    }

    /**
     * Update filter results
     */
    updateFilterResults(filterValue, tableRows) {
        const visibleRows = Array.from(tableRows).filter(row => 
            row.style.display !== 'none'
        );
        
        if (filterValue) {
            this.showFilterFeedback(`Showing ${visibleRows.length} ${filterValue} invoices`);
        }
    }

    /**
     * Handle table responsiveness
     */
    handleTableResponsiveness() {
        const table = document.querySelector('.invoice-table');
        const isMobile = window.innerWidth <= 768;
        
        if (table && isMobile) {
            // Add mobile-specific classes
            table.classList.add('mobile-table');
        } else if (table) {
            table.classList.remove('mobile-table');
        }
    }

    /**
     * Show stat details (placeholder for future functionality)
     */
    showStatDetails(label, value) {
        // This could open a modal or navigate to a detailed view
        console.log(`Showing details for: ${label} - ${value}`);
        
        // Example: Show a toast notification
        this.showToast(`Viewing details for ${label}`);
    }

    /**
     * Show search feedback
     */
    showSearchFeedback(message) {
        this.showToast(message, 'info');
    }

    /**
     * Show filter feedback
     */
    showFilterFeedback(message) {
        this.showToast(message, 'success');
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close">&times;</button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
        
        // Close button functionality
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        });
    }

    /**
     * Export dashboard data
     */
    exportDashboardData() {
        const data = {
            totalInvoices: document.querySelector('.stat-card:nth-child(1) .stat-number')?.textContent,
            totalRevenue: document.querySelector('.stat-card:nth-child(2) .stat-number')?.textContent,
            pendingInvoices: document.querySelector('.stat-card:nth-child(3) .stat-number')?.textContent,
            overdueInvoices: document.querySelector('.stat-card:nth-child(4) .stat-number')?.textContent,
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'billing-dashboard-data.json';
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Refresh dashboard data
     */
    refreshDashboard() {
        // Add loading state
        document.body.classList.add('loading');
        
        // Simulate refresh (replace with actual API call)
        setTimeout(() => {
            document.body.classList.remove('loading');
            this.showToast('Dashboard refreshed successfully', 'success');
        }, 1000);
    }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RestaurantBillingDashboard();
});

// Export for global access if needed
window.RestaurantBillingDashboard = RestaurantBillingDashboard;
