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
            
            // Setup layer controls
            this.setupLayerControls();
            
            // Setup additional controls
            this.setupAdditionalControls();
            
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
        
        // Add event listeners
        this.categories.forEach(category => {
            const checkbox = document.getElementById(`layer-${category.id}`);
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    this.toggleLayer(category.id, e.target.checked);
                });
            }
        });
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
                    📍 Fit All
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
}

// Global functions for external access
window.BusinessMapViewer = BusinessMapViewer;