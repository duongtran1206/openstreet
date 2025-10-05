/**
 * 3-Tier Hierarchical Map Controls
 * Widget để chọn lựa và quản lý dữ liệu 3 tầng trên bản đồ
 */

class HierarchicalMapControls {
    constructor(map, options = {}) {
        this.map = map;
        this.options = {
            position: 'topright',
            apiEndpoint: '/api/hierarchical/locations/',
            domainsEndpoint: '/api/hierarchical/domains/',
            autoLoad: true,
            collapsible: true,
            showStats: true,
            ...options
        };
        
        // Data storage
        this.domains = new Map();
        this.categories = new Map();
        this.locations = new Map();
        this.layerGroups = new Map();
        
        // State management
        this.selectedDomain = null;
        this.selectedCategories = new Set();
        this.visibleLocations = new Set();
        
        // UI elements
        this.controlContainer = null;
        this.isCollapsed = false;
        
        this.init();
    }
    
    init() {
        this.createControlUI();
        this.addToMap();
        
        if (this.options.autoLoad) {
            this.loadDomains();
        }
    }
    
    createControlUI() {
        // Create main container
        this.controlContainer = L.DomUtil.create('div', 'hierarchical-controls');
        
        // Prevent map interactions when using controls
        L.DomEvent.disableClickPropagation(this.controlContainer);
        L.DomEvent.disableScrollPropagation(this.controlContainer);
        
        this.controlContainer.innerHTML = `
            <div class="hierarchical-header">
                <h4>
                    Layer Control
                    <button class="collapse-btn" title="Collapse/Expand">
                        <span class="collapse-icon">−</span>
                    </button>
                </h4>
                ${this.options.showStats ? '<div class="stats-summary"></div>' : ''}
            </div>
            
            <div class="hierarchical-content">
                <!-- TIER 1: Domain Selection -->
                <div class="tier-section domain-section">
                    <div class="tier-header">
                        <span class="tier-title">Tier 1: Domain</span>
                    </div>
                    <select class="domain-select">
                        <option value="">-- Select Domain --</option>
                    </select>
                    <div class="domain-info"></div>
                </div>
                
                <!-- TIER 2: Category Selection -->
                <div class="tier-section category-section">
                    <div class="tier-header">
                        <span class="tier-title">Tier 2: Categories</span>
                        <div class="category-controls">
                            <button class="btn-mini select-all" title="Select All">All</button>
                            <button class="btn-mini deselect-all" title="Deselect All">None</button>
                        </div>
                    </div>
                    <div class="category-list">
                        <div class="loading-message">Select domain to view categories...</div>
                    </div>
                </div>
                
                <!-- TIER 3: Location List -->
                <div class="tier-section location-section">
                    <div class="tier-header">
                        <span class="tier-title">Tier 3: Locations</span>
                        <div class="location-controls">
                            <button class="btn-mini toggle-list" title="Show/Hide List">List</button>
                        </div>
                    </div>
                    <div class="location-summary">
                        <span class="visible-count">0</span> / 
                        <span class="total-count">0</span> locations
                    </div>
                    <div class="location-list" style="display: block;">
                        <div class="loading-message">Select categories to view locations...</div>
                    </div>
                </div>
            </div>
        `;
        
        this.bindEvents();
    }
    
    bindEvents() {
        const container = this.controlContainer;
        
        // Collapse/Expand functionality
        const collapseBtn = container.querySelector('.collapse-btn');
        collapseBtn.addEventListener('click', () => this.toggleCollapse());
        
        // Domain selection
        const domainSelect = container.querySelector('.domain-select');
        domainSelect.addEventListener('change', (e) => this.selectDomain(e.target.value));
        
        // Category controls
        const selectAllBtn = container.querySelector('.select-all');
        const deselectAllBtn = container.querySelector('.deselect-all');
        
        selectAllBtn.addEventListener('click', () => this.selectAllCategories());
        deselectAllBtn.addEventListener('click', () => this.deselectAllCategories());
        
        // Category list delegation (for dynamic content)
        const categoryList = container.querySelector('.category-list');
        categoryList.addEventListener('change', (e) => {
            if (e.target.classList.contains('category-checkbox')) {
                this.toggleCategory(e.target.value, e.target.checked);
            }
        });
        
        // Location list toggle
        const toggleListBtn = container.querySelector('.toggle-list');
        if (toggleListBtn) {
            toggleListBtn.addEventListener('click', () => this.toggleLocationList());
        }
    }
    
    addToMap() {
        // Create Leaflet control
        const CustomControl = L.Control.extend({
            options: {
                position: this.options.position
            },
            
            onAdd: () => {
                return this.controlContainer;
            }
        });
        
        this.leafletControl = new CustomControl();
        this.leafletControl.addTo(this.map);
    }
    
    async loadDomains() {
        try {
            const response = await fetch(this.options.domainsEndpoint);
            const data = await response.json();
            
            if (data.domains) {
                this.processDomains(data.domains);
                this.updateDomainSelect();
                this.updateStats();
            }
        } catch (error) {
            console.error('Error loading domains:', error);
            this.showError('Unable to load domain data');
        }
    }
    
    processDomains(domains) {
        this.domains.clear();
        
        domains.forEach(domain => {
            this.domains.set(domain.domain_id, {
                id: domain.domain_id,
                name: domain.name,
                country: domain.country,
                language: domain.language,
                icon: domain.icon || '🌍',
                categoryCount: domain.category_count || 0,
                locationCount: domain.location_count || 0
            });
        });
    }
    
    updateDomainSelect() {
        const select = this.controlContainer.querySelector('.domain-select');
        
        // Clear existing options (except default)
        select.innerHTML = '<option value="">-- Select Domain --</option>';
        
        let firstDomainId = null;
        
        // Add domain options
        this.domains.forEach(domain => {
            const option = document.createElement('option');
            option.value = domain.id;
            option.textContent = `${domain.icon} ${domain.name}`;
            select.appendChild(option);
            
            // Store first domain ID for auto-selection
            if (!firstDomainId) {
                firstDomainId = domain.id;
            }
        });
        
        // Auto-select first domain if available
        if (firstDomainId) {
            select.value = firstDomainId;
            // Trigger selection programmatically
            setTimeout(() => {
                this.selectDomain(firstDomainId);
            }, 100);
        }
    }
    
    async selectDomain(domainId) {
        if (!domainId) {
            this.selectedDomain = null;
            this.clearCategories();
            this.clearLocations();
            this.clearMapLayers();
            this.updateLocationSummary();
            return;
        }
        
        this.selectedDomain = domainId;
        
        // Update domain info
        this.updateDomainInfo();
        
        // Load categories for this domain
        await this.loadCategories(domainId);
        
        console.log(`Domain selected: ${domainId}, Categories loaded: ${this.categories.size}, Selected categories: ${this.selectedCategories.size}`);
    }
    
    updateDomainInfo() {
        const infoDiv = this.controlContainer.querySelector('.domain-info');
        
        if (!this.selectedDomain) {
            infoDiv.innerHTML = '';
            return;
        }
        
        const domain = this.domains.get(this.selectedDomain);
        infoDiv.innerHTML = `
            <div class="domain-details">
                <small>Location: ${domain.country} | Language: ${domain.language}</small><br>
                <small>Stats: ${domain.categoryCount} categories | ${domain.locationCount} locations</small>
            </div>
        `;
    }
    
    async loadCategories(domainId) {
        try {
            const response = await fetch(`/api/hierarchical/categories/?domain=${domainId}`);
            const data = await response.json();
            
            if (data.categories) {
                this.processCategories(data.categories);
                this.updateCategoryList();
            }
        } catch (error) {
            console.error('Error loading categories:', error);
            this.showError('Unable to load categories');
        }
    }
    
    processCategories(categories) {
        this.categories.clear();
        
        categories.forEach(category => {
            this.categories.set(category.category_id, {
                id: category.category_id,
                name: category.name,
                color: category.color || '#3388ff',
                icon: category.icon || '📂',
                locationCount: category.location_count || 0
            });
        });
    }
    
    updateCategoryList() {
        const listDiv = this.controlContainer.querySelector('.category-list');
        
        if (this.categories.size === 0) {
            listDiv.innerHTML = '<div class="empty-message">No categories available</div>';
            return;
        }
        
        let html = '';
        this.categories.forEach(category => {
            html += `
                <div class="category-item">
                    <label class="category-label">
                        <input type="checkbox" 
                               class="category-checkbox" 
                               value="${category.id}"
                               checked>
                        <span class="category-color" style="background: ${category.color}"></span>
                        <span class="category-text">
                            ${category.name}
                            <small>(${category.locationCount})</small>
                        </span>
                    </label>
                </div>
            `;
        });
        
        listDiv.innerHTML = html;
        
        // Initialize all categories as selected
        this.selectedCategories.clear();
        this.categories.forEach(category => {
            this.selectedCategories.add(category.id);
        });
        
        // Load locations immediately
        setTimeout(() => {
            this.loadLocations();
        }, 100);
    }
    
    async loadLocations() {
        if (!this.selectedDomain) return;
        
        try {
            const categoryIds = Array.from(this.selectedCategories);
            const params = new URLSearchParams({
                domain: this.selectedDomain,
                ...categoryIds.reduce((acc, id, index) => {
                    acc[`categories[${index}]`] = id;
                    return acc;
                }, {})
            });
            
            const response = await fetch(`${this.options.apiEndpoint}?${params}`);
            const data = await response.json();
            
            if (data.features) {
                this.processLocations(data.features);
                this.updateMapLayers();
                this.updateLocationSummary();
                console.log(`Locations loaded: ${data.features.length}, Visible locations: ${this.visibleLocations.size}`);
            }
        } catch (error) {
            console.error('Error loading locations:', error);
            this.showError('Unable to load location data');
        }
    }
    
    processLocations(features) {
        // Clear existing locations and layers
        this.clearMapLayers();
        this.locations.clear();
        this.visibleLocations.clear();
        
        features.forEach(feature => {
            const props = feature.properties;
            const coords = feature.geometry.coordinates;
            
            // Store location data
            this.locations.set(props.id, {
                id: props.id,
                name: props.name,
                address: props.address,
                phone: props.phone,
                email: props.email,
                website: props.website,
                coordinates: [coords[1], coords[0]], // [lat, lng]
                categories: props.categories || [],
                feature: feature
            });
            
            // Check if location should be visible
            const hasVisibleCategory = props.categories.some(cat => 
                this.selectedCategories.has(cat.id)
            );
            
            if (hasVisibleCategory) {
                this.visibleLocations.add(props.id);
            }
        });
    }
    
    updateMapLayers() {
        // Clear existing layers
        this.clearMapLayers();
        
        console.log(`updateMapLayers: ${this.selectedCategories.size} selected categories, ${this.visibleLocations.size} visible locations`);
        
        // Create layer groups for each category
        this.selectedCategories.forEach(categoryId => {
            const category = this.categories.get(categoryId);
            if (category) {
                this.layerGroups.set(categoryId, L.layerGroup().addTo(this.map));
            }
        });
        
        // Add markers to appropriate layer groups
        let markersAdded = 0;
        this.visibleLocations.forEach(locationId => {
            const location = this.locations.get(locationId);
            if (!location) return;
            
            // Create marker
            const marker = L.circleMarker(location.coordinates, {
                radius: 8,
                fillColor: location.categories[0]?.color || '#3388ff',
                color: '#fff',
                weight: 2,
                opacity: 0.8,
                fillOpacity: 0.7
            });
            
            // Add popup
            const popupContent = this.createPopupContent(location);
            marker.bindPopup(popupContent);
            
            // Add to appropriate layer groups
            location.categories.forEach(category => {
                const layerGroup = this.layerGroups.get(category.id);
                if (layerGroup && this.selectedCategories.has(category.id)) {
                    layerGroup.addLayer(marker);
                    markersAdded++;
                }
            });
        });
        
        console.log(`Markers added to map: ${markersAdded}`);
    }
    
    createPopupContent(location) {
        return `
            <div class="location-popup">
                <h4>${location.name}</h4>
                <p><strong>Address:</strong><br>${location.address}</p>
                ${location.phone ? `<p><strong>Phone:</strong> ${location.phone}</p>` : ''}
                ${location.email ? `<p><strong>Email:</strong> ${location.email}</p>` : ''}
                ${location.website ? `<p><strong>Website:</strong> <a href="${location.website}" target="_blank">Visit</a></p>` : ''}
                <div class="categories">
                    ${location.categories.map(cat => 
                        `<span class="category-tag" style="background: ${cat.color}">${cat.name}</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }
    
    toggleCategory(categoryId, isSelected) {
        if (isSelected) {
            this.selectedCategories.add(categoryId);
        } else {
            this.selectedCategories.delete(categoryId);
        }
        
        // Update visible locations and map
        this.updateVisibleLocations();
        this.updateMapLayers();
        this.updateLocationSummary();
    }
    
    updateVisibleLocations() {
        this.visibleLocations.clear();
        
        this.locations.forEach((location, locationId) => {
            const hasVisibleCategory = location.categories.some(cat => 
                this.selectedCategories.has(cat.id)
            );
            
            if (hasVisibleCategory) {
                this.visibleLocations.add(locationId);
            }
        });
    }
    
    selectAllCategories() {
        this.categories.forEach((category, categoryId) => {
            this.selectedCategories.add(categoryId);
        });
        
        // Update checkboxes
        this.controlContainer.querySelectorAll('.category-checkbox').forEach(checkbox => {
            checkbox.checked = true;
        });
        
        console.log(`Select All: ${this.selectedCategories.size} categories selected`);
        this.updateVisibleLocations();
        console.log(`After updateVisibleLocations: ${this.visibleLocations.size} locations visible`);
        this.updateMapLayers();
        this.updateLocationSummary();
    }
    
    deselectAllCategories() {
        this.selectedCategories.clear();
        
        // Update checkboxes
        this.controlContainer.querySelectorAll('.category-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        console.log(`Deselect All: ${this.selectedCategories.size} categories selected`);
        this.updateVisibleLocations();
        console.log(`After updateVisibleLocations: ${this.visibleLocations.size} locations visible`);
        this.updateMapLayers();
        this.updateLocationSummary();
    }
    
    updateLocationSummary() {
        const visibleSpan = this.controlContainer.querySelector('.visible-count');
        const totalSpan = this.controlContainer.querySelector('.total-count');
        
        visibleSpan.textContent = this.visibleLocations.size;
        totalSpan.textContent = this.locations.size;
        
        // Update location list
        this.updateLocationList();
        
        // Update stats if enabled
        if (this.options.showStats) {
            this.updateStats();
        }
    }
    
    updateLocationList() {
        const locationList = this.controlContainer.querySelector('.location-list');
        if (!locationList) {
            console.warn('Location list element not found');
            return;
        }
        
        console.log(`updateLocationList: ${this.visibleLocations.size} visible locations, ${this.locations.size} total locations`);
        
        if (this.visibleLocations.size === 0) {
            locationList.innerHTML = '<div class="loading-message">No locations available for selected categories</div>';
            return;
        }
        
        // Build location list HTML
        let listHTML = '<div class="location-items">';
        
        this.visibleLocations.forEach(locationId => {
            const location = this.locations.get(locationId);
            if (!location) return;
            
            const categoryNames = location.categories.map(cat => cat.name).join(', ');
            
            listHTML += `
                <div class="location-item" data-location-id="${location.id}" title="Click to zoom to location">
                    <div class="location-name">
                        <strong>${location.name}</strong>
                    </div>
                    <div class="location-details">
                        <div class="location-address">${location.address || 'No address available'}</div>
                        <div class="location-categories">${categoryNames}</div>
                        ${location.phone ? `<div class="location-contact">Tel: ${location.phone}</div>` : ''}
                        ${location.email ? `<div class="location-contact">Email: ${location.email}</div>` : ''}
                    </div>
                </div>
            `;
        });
        
        listHTML += '</div>';
        locationList.innerHTML = listHTML;
        
        // Add click events to location items
        locationList.querySelectorAll('.location-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const locationId = item.dataset.locationId;
                this.zoomToLocation(locationId);
            });
        });
    }
    
    zoomToLocation(locationId) {
        const location = this.locations.get(locationId);
        if (!location) return;
        
        const [lat, lng] = location.coordinates;
        this.map.setView([lat, lng], 15);
        
        // Highlight the location temporarily
        this.highlightLocation(locationId);
    }
    
    highlightLocation(locationId) {
        // Find and highlight the marker
        this.layerGroups.forEach(layerGroup => {
            layerGroup.eachLayer(marker => {
                if (marker.options && marker.options.locationId === locationId) {
                    // Temporarily change marker style or open popup
                    if (marker.openPopup) {
                        marker.openPopup();
                    }
                }
            });
        });
    }
    
    toggleLocationList() {
        const locationList = this.controlContainer.querySelector('.location-list');
        const toggleBtn = this.controlContainer.querySelector('.toggle-list');
        
        if (!locationList || !toggleBtn) return;
        
        if (locationList.style.display === 'none') {
            locationList.style.display = 'block';
            toggleBtn.textContent = 'Hide';
            toggleBtn.title = 'Hide location list';
        } else {
            locationList.style.display = 'none';
            toggleBtn.textContent = 'List';
            toggleBtn.title = 'Show location list';
        }
    }
    
    updateStats() {
        const statsDiv = this.controlContainer.querySelector('.stats-summary');
        if (!statsDiv) return;
        
        const domainCount = this.domains.size;
        const categoryCount = this.categories.size;
        const selectedCategoryCount = this.selectedCategories.size;
        const visibleLocationCount = this.visibleLocations.size;
        
        statsDiv.innerHTML = `
            <small>
                ${domainCount} domains | 
                ${selectedCategoryCount}/${categoryCount} categories | 
                ${visibleLocationCount} locations
            </small>
        `;
    }
    
    zoomToVisibleLocations() {
        if (this.visibleLocations.size === 0) {
            this.showMessage('No locations to display');
            return;
        }
        
        const bounds = L.latLngBounds();
        this.visibleLocations.forEach(locationId => {
            const location = this.locations.get(locationId);
            if (location) {
                bounds.extend(location.coordinates);
            }
        });
        
        this.map.fitBounds(bounds, { padding: [10, 10] });
    }
    
    exportVisibleData() {
        const data = {
            domain: this.selectedDomain,
            categories: Array.from(this.selectedCategories),
            locations: Array.from(this.visibleLocations).map(id => this.locations.get(id)),
            exported_at: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `hierarchical_data_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    clearCategories() {
        this.categories.clear();
        this.selectedCategories.clear();
        
        const listDiv = this.controlContainer.querySelector('.category-list');
        listDiv.innerHTML = '<div class="loading-message">Select domain to view categories...</div>';
    }
    
    clearLocations() {
        this.locations.clear();
        this.visibleLocations.clear();
        this.clearMapLayers();
        this.updateLocationSummary();
    }
    
    clearMapLayers() {
        this.layerGroups.forEach(layerGroup => {
            this.map.removeLayer(layerGroup);
        });
        this.layerGroups.clear();
    }
    
    toggleCollapse() {
        const content = this.controlContainer.querySelector('.hierarchical-content');
        const icon = this.controlContainer.querySelector('.collapse-icon');
        
        this.isCollapsed = !this.isCollapsed;
        
        if (this.isCollapsed) {
            content.style.display = 'none';
            icon.textContent = '+';
            this.controlContainer.classList.add('collapsed');
        } else {
            content.style.display = 'block';
            icon.textContent = '−';
            this.controlContainer.classList.remove('collapsed');
        }
    }
    
    showError(message) {
        console.error(message);
        // Could implement toast notification here
    }
    
    showMessage(message) {
        console.log(message);
        // Could implement toast notification here
    }
    
    // Public API methods
    getDomains() {
        return Array.from(this.domains.values());
    }
    
    getSelectedDomain() {
        return this.selectedDomain;
    }
    
    getCategories() {
        return Array.from(this.categories.values());
    }
    
    getSelectedCategories() {
        return Array.from(this.selectedCategories);
    }
    
    getVisibleLocations() {
        return Array.from(this.visibleLocations).map(id => this.locations.get(id));
    }
    
    destroy() {
        if (this.leafletControl) {
            this.map.removeControl(this.leafletControl);
        }
        this.clearMapLayers();
    }
}