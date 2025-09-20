/**
 * UI Components Management System
 * Handles interactive components like tabs, tables, forms, and other UI elements
 */

class ComponentManager {
    constructor() {
        this.activeComponents = new Map();
        this.init();
    }
    
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
        } else {
            this.initializeComponents();
        }
    }
    
    initializeComponents() {
        this.initializeTabs();
        this.initializeTables();
        this.initializeForms();
        this.initializeProgressBars();
        this.initializeTooltips();
        this.initializeModals();
        this.setupGlobalEventListeners();
    }
    
    // Tab System
    initializeTabs() {
        const tabContainers = document.querySelectorAll('.tabs');
        
        tabContainers.forEach(container => {
            const triggers = container.querySelectorAll('.tab-trigger');
            const contents = container.querySelectorAll('.tab-content');
            
            triggers.forEach(trigger => {
                trigger.addEventListener('click', () => {
                    const tabId = trigger.getAttribute('data-tab');
                    this.switchTab(container, tabId);
                });
                
                // Keyboard navigation for tabs
                trigger.addEventListener('keydown', (e) => {
                    this.handleTabKeyboard(e, triggers);
                });
            });
            
            // Store tab state
            this.activeComponents.set(container, {
                type: 'tabs',
                activeTab: container.querySelector('.tab-trigger.active')?.getAttribute('data-tab') || 'availability'
            });
        });
    }
    
    switchTab(container, tabId) {
        const triggers = container.querySelectorAll('.tab-trigger');
        const contents = container.querySelectorAll('.tab-content');
        
        // Update triggers
        triggers.forEach(trigger => {
            if (trigger.getAttribute('data-tab') === tabId) {
                trigger.classList.add('active');
                trigger.setAttribute('aria-selected', 'true');
                trigger.setAttribute('tabindex', '0');
            } else {
                trigger.classList.remove('active');
                trigger.setAttribute('aria-selected', 'false');
                trigger.setAttribute('tabindex', '-1');
            }
        });
        
        // Update content
        contents.forEach(content => {
            if (content.id === `${tabId}-tab`) {
                content.classList.add('active');
                content.setAttribute('aria-hidden', 'false');
            } else {
                content.classList.remove('active');
                content.setAttribute('aria-hidden', 'true');
            }
        });
        
        // Update component state
        const componentState = this.activeComponents.get(container);
        if (componentState) {
            componentState.activeTab = tabId;
        }
        
        // Dispatch tab change event
        this.dispatchTabChangeEvent(container, tabId);
    }
    
    handleTabKeyboard(e, triggers) {
        const currentIndex = Array.from(triggers).indexOf(e.target);
        let nextIndex;
        
        switch (e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                nextIndex = currentIndex === 0 ? triggers.length - 1 : currentIndex - 1;
                triggers[nextIndex].focus();
                triggers[nextIndex].click();
                break;
            case 'ArrowRight':
                e.preventDefault();
                nextIndex = (currentIndex + 1) % triggers.length;
                triggers[nextIndex].focus();
                triggers[nextIndex].click();
                break;
            case 'Home':
                e.preventDefault();
                triggers[0].focus();
                triggers[0].click();
                break;
            case 'End':
                e.preventDefault();
                triggers[triggers.length - 1].focus();
                triggers[triggers.length - 1].click();
                break;
        }
    }
    

    
    // Table System
    initializeTables() {
        const tables = document.querySelectorAll('.table');
        
        tables.forEach(table => {
            this.makeTableResponsive(table);
            this.addTableSorting(table);
            this.addTableFiltering(table);
            
            // Add hover effects
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.addEventListener('mouseenter', () => {
                    this.highlightTableRow(row, true);
                });
                row.addEventListener('mouseleave', () => {
                    this.highlightTableRow(row, false);
                });
            });
        });
    }
    
    makeTableResponsive(table) {
        const container = table.closest('.table-container');
        if (!container) return;
        
        // Add scroll shadows
        const updateScrollShadows = () => {
            const scrollLeft = container.scrollLeft;
            const scrollWidth = container.scrollWidth;
            const clientWidth = container.clientWidth;
            
            container.classList.toggle('scroll-left', scrollLeft > 0);
            container.classList.toggle('scroll-right', scrollLeft < scrollWidth - clientWidth);
        };
        
        container.addEventListener('scroll', updateScrollShadows);
        window.addEventListener('resize', updateScrollShadows);
        updateScrollShadows();
    }
    
    addTableSorting(table) {
        const headers = table.querySelectorAll('th[data-sortable]');
        
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.setAttribute('role', 'button');
            header.setAttribute('tabindex', '0');
            
            // Add sort icon
            const sortIcon = document.createElement('span');
            sortIcon.className = 'sort-icon';
            sortIcon.innerHTML = '↕️';
            header.appendChild(sortIcon);
            
            header.addEventListener('click', () => {
                this.sortTable(table, header);
            });
            
            header.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.sortTable(table, header);
                }
            });
        });
    }
    
    sortTable(table, header) {
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const isAscending = !header.classList.contains('sort-asc');
        
        // Clear other sort states
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        
        // Set current sort state
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        
        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.children[columnIndex].textContent.trim();
            const bValue = b.children[columnIndex].textContent.trim();
            
            // Try to compare as numbers first
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? aNum - bNum : bNum - aNum;
            }
            
            // Compare as strings
            return isAscending 
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        });
        
        // Reorder DOM
        rows.forEach(row => tbody.appendChild(row));
        
        // Add animation
        this.animateTableSort(tbody);
    }
    
    animateTableSort(tbody) {
        tbody.style.opacity = '0.7';
        
        setTimeout(() => {
            tbody.style.transition = 'opacity 0.2s ease';
            tbody.style.opacity = '1';
            
            setTimeout(() => {
                tbody.style.transition = '';
            }, 200);
        }, 50);
    }
    
    addTableFiltering(table) {
        const container = table.closest('.card');
        const searchInput = container?.querySelector('input[type="text"]');
        
        if (!searchInput) return;
        
        let filterTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(filterTimeout);
            filterTimeout = setTimeout(() => {
                this.filterTable(table, e.target.value);
            }, 300);
        });
    }
    
    filterTable(table, searchTerm) {
        const rows = table.querySelectorAll('tbody tr');
        const term = searchTerm.toLowerCase();
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(term);
            
            row.style.display = matches ? '' : 'none';
            
            if (matches) {
                row.style.animation = 'fadeIn 0.3s ease';
            }
        });
    }
    
    highlightTableRow(row, highlight) {
        if (highlight) {
            row.style.backgroundColor = 'var(--color-background-secondary)';
            row.style.boxShadow = 'var(--shadow-sm)';
        } else {
            row.style.backgroundColor = '';
            row.style.boxShadow = '';
        }
    }
    
    // Form System
    initializeForms() {
        const forms = document.querySelectorAll('form, .form-container');
        
        forms.forEach(form => {
            this.initializeFormValidation(form);
            this.initializeFormAnimations(form);
        });
        
        // Initialize file uploads
        this.initializeFileUploads();
        
        // Initialize custom selects
        this.initializeCustomSelects();
    }
    
    initializeFormValidation(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
            
            input.addEventListener('input', () => {
                this.clearFieldError(input);
            });
        });
    }
    
    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        
        let isValid = true;
        let errorMessage = '';
        
        // Required field validation
        if (required && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }
        
        // Email validation
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        }
        
        // Phone validation
        if (type === 'tel' && value) {
            const phoneRegex = /^[\+]?[\d\s\-\(\)]+$/;
            if (!phoneRegex.test(value) || value.length < 10) {
                isValid = false;
                errorMessage = 'Please enter a valid phone number';
            }
        }
        
        this.setFieldValidation(field, isValid, errorMessage);
        return isValid;
    }
    
    setFieldValidation(field, isValid, errorMessage) {
        const container = field.closest('.form-group') || field.parentElement;
        
        // Remove existing error
        const existingError = container.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        if (isValid) {
            field.classList.remove('error');
            field.classList.add('valid');
        } else {
            field.classList.remove('valid');
            field.classList.add('error');
            
            // Add error message
            const errorEl = document.createElement('span');
            errorEl.className = 'field-error';
            errorEl.textContent = errorMessage;
            container.appendChild(errorEl);
        }
    }
    
    clearFieldError(field) {
        field.classList.remove('error', 'valid');
        const container = field.closest('.form-group') || field.parentElement;
        const errorEl = container.querySelector('.field-error');
        if (errorEl) {
            errorEl.remove();
        }
    }
    
    initializeFormAnimations(form) {
        const inputs = form.querySelectorAll('input, textarea');
        
        inputs.forEach(input => {
            // Floating label effect
            const handleInputState = () => {
                const hasValue = input.value.trim() !== '';
                input.classList.toggle('has-value', hasValue);
            };
            
            input.addEventListener('input', handleInputState);
            input.addEventListener('blur', handleInputState);
            input.addEventListener('focus', handleInputState);
            
            // Initial state
            handleInputState();
        });
    }
    
    initializeFileUploads() {
        const uploadAreas = document.querySelectorAll('.upload-area');
        
        uploadAreas.forEach(area => {
            // Drag and drop functionality
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('drag-over');
            });
            
            area.addEventListener('dragleave', () => {
                area.classList.remove('drag-over');
            });
            
            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('drag-over');
                
                const files = e.dataTransfer.files;
                this.handleFileUpload(area, files);
            });
            
            // Click to upload
            area.addEventListener('click', () => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = 'image/*,.pdf';
                input.onchange = (e) => {
                    this.handleFileUpload(area, e.target.files);
                };
                input.click();
            });
        });
    }
    
    initializeCustomSelects() {
        const customSelects = document.querySelectorAll('.custom-select, select[data-custom="true"]');
        
        customSelects.forEach(select => {
            // Skip if already initialized
            if (select.classList.contains('custom-select-initialized')) {
                return;
            }
            
            // Create custom select wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'custom-select-wrapper';
            
            // Create custom select button
            const button = document.createElement('button');
            button.className = 'custom-select-button';
            button.type = 'button';
            button.setAttribute('aria-haspopup', 'listbox');
            button.setAttribute('aria-expanded', 'false');
            
            // Create custom select dropdown
            const dropdown = document.createElement('ul');
            dropdown.className = 'custom-select-dropdown';
            dropdown.setAttribute('role', 'listbox');
            
            // Get options from original select
            const options = Array.from(select.options);
            let selectedOption = options.find(option => option.selected) || options[0];
            
            // Create custom options
            options.forEach((option, index) => {
                const li = document.createElement('li');
                li.className = 'custom-select-option';
                li.setAttribute('role', 'option');
                li.setAttribute('data-value', option.value);
                li.textContent = option.textContent;
                
                if (option.selected) {
                    li.classList.add('selected');
                    button.textContent = option.textContent;
                }
                
                li.addEventListener('click', () => {
                    // Update original select
                    select.value = option.value;
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    // Update custom select
                    dropdown.querySelectorAll('.custom-select-option').forEach(opt => {
                        opt.classList.remove('selected');
                    });
                    li.classList.add('selected');
                    button.textContent = option.textContent;
                    
                    // Close dropdown
                    this.closeCustomSelect(wrapper);
                });
                
                dropdown.appendChild(li);
            });
            
            // Add click handler to button
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const isOpen = wrapper.classList.contains('open');
                
                // Close all other custom selects
                document.querySelectorAll('.custom-select-wrapper.open').forEach(w => {
                    if (w !== wrapper) {
                        this.closeCustomSelect(w);
                    }
                });
                
                if (isOpen) {
                    this.closeCustomSelect(wrapper);
                } else {
                    this.openCustomSelect(wrapper);
                }
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!wrapper.contains(e.target)) {
                    this.closeCustomSelect(wrapper);
                }
            });
            
            // Keyboard navigation
            button.addEventListener('keydown', (e) => {
                this.handleCustomSelectKeyboard(e, wrapper);
            });
            
            // Assemble custom select
            wrapper.appendChild(button);
            wrapper.appendChild(dropdown);
            
            // Replace original select
            select.style.display = 'none';
            select.parentNode.insertBefore(wrapper, select);
            wrapper.appendChild(select);
            
            // Mark as initialized
            select.classList.add('custom-select-initialized');
        });
    }
    
    openCustomSelect(wrapper) {
        wrapper.classList.add('open');
        const button = wrapper.querySelector('.custom-select-button');
        const dropdown = wrapper.querySelector('.custom-select-dropdown');
        
        button.setAttribute('aria-expanded', 'true');
        dropdown.style.display = 'block';
        
        // Focus first option
        const firstOption = dropdown.querySelector('.custom-select-option');
        if (firstOption) {
            firstOption.focus();
        }
    }
    
    closeCustomSelect(wrapper) {
        wrapper.classList.remove('open');
        const button = wrapper.querySelector('.custom-select-button');
        const dropdown = wrapper.querySelector('.custom-select-dropdown');
        
        button.setAttribute('aria-expanded', 'false');
        dropdown.style.display = 'none';
        
        // Return focus to button
        button.focus();
    }
    
    handleCustomSelectKeyboard(e, wrapper) {
        const dropdown = wrapper.querySelector('.custom-select-dropdown');
        const options = Array.from(dropdown.querySelectorAll('.custom-select-option'));
        const currentOption = dropdown.querySelector('.custom-select-option:focus');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (currentOption) {
                    const nextIndex = (options.indexOf(currentOption) + 1) % options.length;
                    options[nextIndex].focus();
                } else {
                    options[0]?.focus();
                }
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                if (currentOption) {
                    const prevIndex = (options.indexOf(currentOption) - 1 + options.length) % options.length;
                    options[prevIndex].focus();
                } else {
                    options[options.length - 1]?.focus();
                }
                break;
                
            case 'Enter':
            case ' ':
                e.preventDefault();
                if (currentOption) {
                    currentOption.click();
                }
                break;
                
            case 'Escape':
                e.preventDefault();
                this.closeCustomSelect(wrapper);
                break;
        }
    }
    
    handleFileUpload(area, files) {
        if (files.length === 0) return;
        
        const file = files[0];
        const maxSize = 5 * 1024 * 1024; // 5MB
        
        if (file.size > maxSize) {
            this.showNotification('File size must be less than 5MB', 'error');
            return;
        }
        
        // Show upload progress
        this.showUploadProgress(area, file);
    }
    
    showUploadProgress(area, file) {
        area.innerHTML = `
            <div class="upload-progress">
                <div class="upload-file-info">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${this.formatFileSize(file.size)}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
                <span class="upload-status">Uploading...</span>
            </div>
        `;
        
        // Simulate upload progress
        const progressFill = area.querySelector('.progress-fill');
        const statusEl = area.querySelector('.upload-status');
        let progress = 0;
        
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                statusEl.textContent = 'Upload complete';
                statusEl.style.color = 'var(--color-success)';
            }
            progressFill.style.width = `${progress}%`;
        }, 200);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Progress Bars
    initializeProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        
        // Intersection Observer for animation on scroll
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressFill = entry.target.querySelector('.progress-fill');
                    if (progressFill) {
                        this.animateProgressBar(progressFill);
                    }
                }
            });
        }, { threshold: 0.5 });
        
        progressBars.forEach(bar => observer.observe(bar));
    }
    
    animateProgressBar(progressFill) {
        const targetWidth = progressFill.style.width || '0%';
        progressFill.style.width = '0%';
        
        setTimeout(() => {
            progressFill.style.transition = 'width 1s ease-out';
            progressFill.style.width = targetWidth;
        }, 100);
    }
    
    // Tooltips
    initializeTooltips() {
        const elementsWithTooltips = document.querySelectorAll('[title], [data-tooltip]');
        
        elementsWithTooltips.forEach(element => {
            const tooltip = this.createTooltip(element);
            
            element.addEventListener('mouseenter', () => {
                this.showTooltip(tooltip, element);
            });
            
            element.addEventListener('mouseleave', () => {
                this.hideTooltip(tooltip);
            });
        });
    }
    
    createTooltip(element) {
        const tooltipText = element.getAttribute('data-tooltip') || element.getAttribute('title');
        element.removeAttribute('title'); // Prevent default tooltip
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = tooltipText;
        document.body.appendChild(tooltip);
        
        return tooltip;
    }
    
    showTooltip(tooltip, element) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        tooltip.style.top = `${rect.top - tooltipRect.height - 8}px`;
        tooltip.style.left = `${rect.left + (rect.width - tooltipRect.width) / 2}px`;
        tooltip.classList.add('visible');
    }
    
    hideTooltip(tooltip) {
        tooltip.classList.remove('visible');
    }
    
    // Modal System
    initializeModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');
        
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal');
                this.openModal(modalId);
            });
        });
    }
    
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
        
        // Focus first focusable element
        const focusable = modal.querySelector('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusable) {
            focusable.focus();
        }
        
        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal(modalId);
            }
        });
        
        // Close on escape
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                this.closeModal(modalId);
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }
    
    // Global Event Listeners
    setupGlobalEventListeners() {
        // Button click effects
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn, button')) {
                this.addButtonRipple(e.target, e);
            }
        });
        
        // Auto-resize textareas
        document.addEventListener('input', (e) => {
            if (e.target.matches('textarea[data-auto-resize]')) {
                this.autoResizeTextarea(e.target);
            }
        });
    }
    
    addButtonRipple(button, event) {
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
    
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }
    
    // Utility Methods
    dispatchTabChangeEvent(container, tabId) {
        const event = new CustomEvent('tabchange', {
            detail: { container, tabId }
        });
        document.dispatchEvent(event);
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    // Public API
    getComponentState(element) {
        return this.activeComponents.get(element);
    }
    
    switchToTab(container, tabId) {
        this.switchTab(container, tabId);
    }
    
    validateForm(form) {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
}

// Initialize component manager
window.componentManager = new ComponentManager();

// Export for global access
window.ComponentManager = ComponentManager;

console.info('🎛️ Component Manager loaded. Features: tabs, tables, forms, tooltips, modals');