/**
 * Business Map Viewer - Interactive map with layers for business locations
 * Built with Leaflet.js and OpenStreetMap
 */

class BusinessMapViewer {
    constructor(mapId, options = {}) {
        this.mapId = mapId;
        this.options = {
            apiEndpoint: '/api/map-data/',
            configEndpoint: '/api/map-config/',
            enableClustering: false,
            showControls: true,
            defaultZoom: 10,
            ...options
        };
        
        this.map = null;
        this.layerGroups = {};
        this.categories = [];
        this.allLocations = [];
        
        this.init();
    }
    
    async init() {
        try {
            console.log('Initializing Business Map...');
            
            // Load configuration first
            const config = await this.loadConfig();
            console.log('Map config loaded:', config);
            
            // Initialize the map
            this.initMap(config);
            
            // Load location data
            await this.loadData();
            
            // Setup layer controls - DISABLED (using 3-tier controls instead)
            // this.setupLayerControls();
            
            // Setup additional controls
            this.setupAdditionalControls();
            
            // Initialize 3-Tier Hierarchical Controls
            this.setup3TierControls();
            
            console.log('Map initialized successfully');
            
        } catch (error) {
            console.error('Error initializing map:', error);
            this.showError('Failed to load map. Please try again later.');
        }
    }
    
    async loadConfig() {
        try {
            const response = await fetch(this.options.configEndpoint);
            if (!response.ok) throw new Error('Config request failed');
            return await response.json();
        } catch (error) {
            console.warn('Using default config due to error:', error);
            return this.getDefaultConfig();
        }
    }
    
    getDefaultConfig() {
        return {
            center_latitude: 21.0285,
            center_longitude: 105.8542,
            zoom_level: 10,
            tile_layer: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attribution: '© OpenStreetMap contributors',
            max_zoom: 18,
            min_zoom: 1,
            show_zoom_control: true
        };
    }
    
    initMap(config) {
        // Initialize the map
        this.map = L.map(this.mapId, {
            zoomControl: config.show_zoom_control !== false
        }).setView(
            [config.center_latitude, config.center_longitude], 
            config.zoom_level || this.options.defaultZoom
        );
        
        // Add tile layer (OpenStreetMap)
        L.tileLayer(config.tile_layer, {
            attribution: config.attribution,
            maxZoom: config.max_zoom || 18,
            minZoom: config.min_zoom || 1
        }).addTo(this.map);
        
        // Add scale control if enabled
        if (config.show_scale !== false) {
            L.control.scale().addTo(this.map);
        }
    }
    
    async loadData() {
        try {
            const response = await fetch(this.options.apiEndpoint);
            if (!response.ok) throw new Error('Data request failed');
            
            const data = await response.json();
            console.log('Map data loaded:', data);
            
            this.categories = data.categories || [];
            this.allLocations = data.locations || [];
            
            // Create layer groups for each category
            this.categories.forEach(category => {
                this.layerGroups[category.id] = L.layerGroup();
            });
            
            // Add markers to their respective layers
            this.allLocations.forEach(location => {
                this.addMarker(location);
            });
            
            // Add all layers to map initially
            Object.values(this.layerGroups).forEach(group => {
                group.addTo(this.map);
            });
            
            // Fit map to show all markers
            this.fitMapToMarkers();
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load location data.');
        }
    }
    
    addMarker(location) {
        // Create marker based on category
        const marker = L.circleMarker([location.latitude, location.longitude], {
            color: location.category_color || '#ff6b6b',
            fillColor: location.category_color || '#ff6b6b',
            fillOpacity: 0.8,
            radius: location.featured ? 10 : 8,
            weight: location.featured ? 3 : 2,
            className: 'custom-marker'
        });
        
        // Create popup content
        const popupContent = this.createPopupContent(location);
        marker.bindPopup(popupContent, {
            maxWidth: 300,
            closeButton: true
        });
        
        // Add hover effects
        marker.on('mouseover', function() {
            this.setStyle({
                fillOpacity: 1,
                radius: this.options.radius + 2
            });
        });
        
        marker.on('mouseout', function() {
            this.setStyle({
                fillOpacity: 0.8,
                radius: this.options.radius - 2
            });
        });
        
        // Add to appropriate layer group
        if (this.layerGroups[location.category]) {
            marker.addTo(this.layerGroups[location.category]);
        }
    }
    
    createPopupContent(location) {
        let content = `
            <div class="popup-content">
                <div class="popup-title">${location.name}</div>
                <div class="popup-address">${location.address}</div>
        `;
        
        if (location.description) {
            content += `<div class="popup-description">${location.description}</div>`;
        }
        
        // Add contact information if available
        const contacts = [];
        if (location.phone) contacts.push(`📞 ${location.phone}`);
        if (location.email) contacts.push(`📧 <a href="mailto:${location.email}">${location.email}</a>`);
        if (location.website) contacts.push(`🌐 <a href="${location.website}" target="_blank">Website</a>`);
        
        if (contacts.length > 0) {
            content += `
                <div class="popup-contact">
                    ${contacts.join('<br>')}
                </div>
            `;
        }
        
        content += `</div>`;
        
        return content;
    }
    
    setupLayerControls() {
        const controlsContainer = document.getElementById('layer-controls');
        if (!controlsContainer) return;
        
        let html = '';
        
        this.categories.forEach(category => {
            const count = this.allLocations.filter(loc => loc.category === category.id).length;
            
            html += `
                <div class="layer-toggle" data-category="${category.id}">
                    <input type="checkbox" id="layer-${category.id}" checked>
                    <div class="layer-color" style="background-color: ${category.color}"></div>
                    <label for="layer-${category.id}" class="layer-label">${category.name}</label>
                    <span class="layer-count">${count}</span>
                </div>
            `;
        });
        
        controlsContainer.innerHTML = html;
        
        // Add event listeners for layer checkboxes
        this.categories.forEach(category => {
            const checkbox = document.getElementById(`layer-${category.id}`);
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    this.toggleLayer(category.id, e.target.checked);
                });
            }
        });
        
        // Add event listeners for select/deselect all buttons - ensure DOM is ready
        this.setupLayerControlButtons();
    }
    
    setupLayerControlButtons() {
        console.log('Setting up layer control buttons...');
        
        // Wait a bit to ensure DOM is fully loaded
        setTimeout(() => {
            const selectAllBtn = document.getElementById('select-all-layers');
            const deselectAllBtn = document.getElementById('deselect-all-layers');
            
            console.log('Select All button:', selectAllBtn);
            console.log('Deselect All button:', deselectAllBtn);
            
            if (selectAllBtn) {
                // Remove existing onclick to avoid conflicts
                selectAllBtn.removeAttribute('onclick');
                
                // Add new event listener
                selectAllBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    console.log('JavaScript: Select All clicked');
                    this.selectAllLayers(true);
                });
                console.log('✅ Select All button event listener added');
            } else {
                console.error('❌ Select All button not found!');
            }
            
            if (deselectAllBtn) {
                // Remove existing onclick to avoid conflicts
                deselectAllBtn.removeAttribute('onclick');
                
                // Add new event listener  
                deselectAllBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    console.log('JavaScript: Deselect All clicked');
                    this.selectAllLayers(false);
                });
                console.log('✅ Deselect All button event listener added');
            } else {
                console.error('❌ Deselect All button not found!');
            }
        }, 200);
    }
    
    selectAllLayers(select = true) {
        console.log(`selectAllLayers called with select=${select}`);
        console.log('Available categories:', this.categories);
        
        // Find all layer checkboxes directly
        const allCheckboxes = document.querySelectorAll('input[id^="layer-"');
        console.log('Found checkboxes:', allCheckboxes.length);
        
        allCheckboxes.forEach(checkbox => {
            console.log(`Setting checkbox ${checkbox.id} to ${select}`);
            checkbox.checked = select;
            
            // Extract category ID from checkbox ID (format: "layer-{categoryId}")
            const categoryId = parseInt(checkbox.id.replace('layer-', ''));
            if (!isNaN(categoryId)) {
                this.toggleLayer(categoryId, select);
            }
        });
        
        // Alternative: use this.categories if available
        if (this.categories && this.categories.length > 0) {
            this.categories.forEach(category => {
                const checkbox = document.getElementById(`layer-${category.id}`);
                if (checkbox) {
                    checkbox.checked = select;
                    this.toggleLayer(category.id, select);
                }
            });
        }
        
        // Optional: Show notification
        const action = select ? 'selected' : 'deselected';
        console.log(`All layers ${action}`);
    }
    
    // Global test functions for console debugging
    testSelectAll() {
        console.log('Testing Select All...');
        this.selectAllLayers(true);
    }
    
    testDeselectAll() {
        console.log('Testing Deselect All...');
        this.selectAllLayers(false);
    }
    
    setupAdditionalControls() {
        // Featured only toggle
        const featuredToggle = document.getElementById('featured-only');
        if (featuredToggle) {
            featuredToggle.addEventListener('change', (e) => {
                this.filterFeaturedOnly(e.target.checked);
            });
        }
        
        // Add custom controls to map
        const customControl = L.control({position: 'topleft'});
        customControl.onAdd = () => {
            const div = L.DomUtil.create('div', 'leaflet-control-custom');
            div.innerHTML = `
                <button onclick="businessMap.fitMapToMarkers()" title="Fit to all locations">
                    Fit All
                </button>
            `;
            div.style.backgroundColor = 'white';
            div.style.padding = '5px';
            div.style.borderRadius = '3px';
            div.style.boxShadow = '0 1px 5px rgba(0,0,0,0.2)';
            return div;
        };
        customControl.addTo(this.map);
    }
    
    toggleLayer(categoryId, show) {
        const layerGroup = this.layerGroups[categoryId];
        if (!layerGroup) return;
        
        if (show) {
            layerGroup.addTo(this.map);
        } else {
            this.map.removeLayer(layerGroup);
        }
    }
    
    filterFeaturedOnly(featuredOnly) {
        // Clear all layers
        Object.values(this.layerGroups).forEach(group => {
            group.clearLayers();
        });
        
        // Filter locations
        const locationsToShow = featuredOnly 
            ? this.allLocations.filter(loc => loc.featured)
            : this.allLocations;
        
        // Re-add filtered markers
        locationsToShow.forEach(location => {
            this.addMarker(location);
        });
        
        // Re-apply layer visibility based on checkboxes
        this.categories.forEach(category => {
            const checkbox = document.getElementById(`layer-${category.id}`);
            if (checkbox && checkbox.checked) {
                this.layerGroups[category.id].addTo(this.map);
            }
        });
        
        // Update counts
        this.updateLayerCounts(locationsToShow);
    }
    
    updateLayerCounts(locations) {
        this.categories.forEach(category => {
            const count = locations.filter(loc => loc.category === category.id).length;
            const countEl = document.querySelector(`[data-category="${category.id}"] .layer-count`);
            if (countEl) {
                countEl.textContent = count;
            }
        });
    }
    
    fitMapToMarkers() {
        const allMarkers = [];
        Object.values(this.layerGroups).forEach(group => {
            group.eachLayer(layer => {
                allMarkers.push(layer.getLatLng());
            });
        });
        
        if (allMarkers.length > 0) {
            const group = new L.featureGroup(
                allMarkers.map(latlng => L.marker(latlng))
            );
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }
    
    showError(message) {
        const mapContainer = document.getElementById(this.mapId);
        if (mapContainer) {
            mapContainer.innerHTML = `<div class="error">${message}</div>`;
        }
    }
    
    // Public methods for external control
    showCategory(categoryId) {
        const checkbox = document.getElementById(`layer-${categoryId}`);
        if (checkbox) {
            checkbox.checked = true;
            this.toggleLayer(categoryId, true);
        }
    }
    
    hideCategory(categoryId) {
        const checkbox = document.getElementById(`layer-${categoryId}`);
        if (checkbox) {
            checkbox.checked = false;
            this.toggleLayer(categoryId, false);
        }
    }
    
    showOnlyCategory(categoryId) {
        // Hide all categories first
        this.categories.forEach(category => {
            this.hideCategory(category.id);
        });
        // Then show the selected one
        this.showCategory(categoryId);
    }
    
    showAllCategories() {
        this.categories.forEach(category => {
            this.showCategory(category.id);
        });
    }
    
    setup3TierControls() {
        // Check if HierarchicalMapControls is available
        if (typeof HierarchicalMapControls !== 'undefined') {
            console.log('Initializing 3-Tier Hierarchical Controls...');
            
            // Clear old layer groups to prevent conflicts
            this.clearOldLayers();
            
            // Initialize the hierarchical controls
            this.hierarchicalControls = new HierarchicalMapControls(this.map, {
                position: 'topright',
                apiEndpoint: '/api/hierarchical/locations/',
                domainsEndpoint: '/api/hierarchical/domains/',
                autoLoad: true,
                collapsible: true,
                showStats: true
            });
            
            console.log('3-Tier Controls initialized successfully');
        } else {
            console.warn('HierarchicalMapControls not found. Make sure hierarchical-controls.js is loaded.');
        }
    }
    
    clearOldLayers() {
        // Remove all old layer groups from the map
        Object.values(this.layerGroups).forEach(group => {
            if (group && this.map.hasLayer(group)) {
                this.map.removeLayer(group);
            }
        });
        
        // Clear the layer groups object
        this.layerGroups = {};
        
        console.log('Old layer groups cleared for 3-tier controls');
    }
    
    // Public method to get hierarchical controls
    getHierarchicalControls() {
        return this.hierarchicalControls;
    }
    
    // Method to toggle between regular and hierarchical mode
    toggleHierarchicalMode(enable = true) {
        if (!this.hierarchicalControls) {
            console.warn('Hierarchical controls not available');
            return;
        }
        
        if (enable) {
            // Hide regular layer controls if they exist
            if (this.layerControl) {
                this.map.removeControl(this.layerControl);
            }
            
            console.log('Switched to Hierarchical mode');
        } else {
            // Destroy hierarchical controls
            if (this.hierarchicalControls) {
                this.hierarchicalControls.destroy();
                this.hierarchicalControls = null;
            }
            
            // Re-add regular layer controls - DISABLED (using 3-tier only)
            // this.setupLayerControls();
            
            console.log('Switched to Regular mode');
        }
    }
}

// Global functions for external access
window.BusinessMapViewer = BusinessMapViewer;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const mapViewer = new BusinessMapViewer();
    
    // Make it globally accessible for debugging
    window.mapViewer = mapViewer;
    
    // Also make the select/deselect functions globally accessible
    window.selectAllLayers = (select = true) => {
        console.log('Global function called:', select ? 'Select All' : 'Deselect All');
        if (mapViewer && typeof mapViewer.selectAllLayers === 'function') {
            mapViewer.selectAllLayers(select);
        }
    };
    
    window.testButtons = () => {
        console.log('Testing button functionality...');
        console.log('Map viewer:', window.mapViewer);
        console.log('Categories:', window.mapViewer?.categories);
        console.log('Layer groups:', window.mapViewer?.layerGroups);
    };
});