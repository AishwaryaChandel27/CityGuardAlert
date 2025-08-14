// Dashboard JavaScript for CityGuard AI
let allIncidents = [];
let filteredIncidents = [];

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    
    // Auto-refresh every 5 minutes
    setInterval(refreshDashboard, 5 * 60 * 1000);
    
    // Initialize feather icons
    feather.replace();
});

async function loadDashboard() {
    try {
        // Load stats and incidents in parallel
        await Promise.all([
            loadStats(),
            loadIncidents()
        ]);
        
        updateLastUpdateTime();
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showErrorState();
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            updateStatsCards(data.stats);
        } else {
            console.error('Failed to load stats:', data.error);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        // Set default values if stats fail to load
        updateStatsCards({
            total_incidents_24h: 0,
            critical_incidents_24h: 0,
            weather_incidents_24h: 0,
            active_subscribers: 0
        });
    }
}

async function loadIncidents() {
    try {
        showLoadingState();
        
        const timeFilter = document.getElementById('time-filter').value || '24';
        const response = await fetch(`/api/incidents?hours=${timeFilter}&min_relevance=0.3`);
        const data = await response.json();
        
        if (data.success) {
            allIncidents = data.incidents;
            filterIncidents();
            hideLoadingState();
        } else {
            throw new Error(data.error || 'Failed to load incidents');
        }
    } catch (error) {
        console.error('Error loading incidents:', error);
        hideLoadingState();
        showErrorState();
    }
}

function updateStatsCards(stats) {
    document.getElementById('total-incidents').textContent = stats.total_incidents_24h || 0;
    document.getElementById('critical-incidents').textContent = stats.critical_incidents_24h || 0;
    document.getElementById('weather-incidents').textContent = stats.weather_incidents_24h || 0;
    document.getElementById('active-subscribers').textContent = stats.active_subscribers || 0;
}

function filterIncidents() {
    const severityFilter = document.getElementById('severity-filter').value;
    const sourceFilter = document.getElementById('source-filter').value;
    
    filteredIncidents = allIncidents.filter(incident => {
        const matchesSeverity = !severityFilter || incident.severity === severityFilter;
        const matchesSource = !sourceFilter || incident.source === sourceFilter;
        return matchesSeverity && matchesSource;
    });
    
    displayIncidents(filteredIncidents);
    updateIncidentCount(filteredIncidents.length);
}

function displayIncidents(incidents) {
    const container = document.getElementById('incidents-container');
    
    if (incidents.length === 0) {
        showNoIncidentsState();
        return;
    }
    
    hideNoIncidentsState();
    
    // Sort incidents by relevance score and date
    incidents.sort((a, b) => {
        const scoreA = a.relevance_score || 0;
        const scoreB = b.relevance_score || 0;
        if (scoreA !== scoreB) return scoreB - scoreA;
        return new Date(b.created_at) - new Date(a.created_at);
    });
    
    container.innerHTML = incidents.map(incident => createIncidentCard(incident)).join('');
    
    // Re-initialize feather icons for new content
    feather.replace();
}

function createIncidentCard(incident) {
    const severityColors = {
        'low': 'success',
        'medium': 'warning',
        'high': 'warning',
        'critical': 'danger'
    };
    
    const severityColor = severityColors[incident.severity] || 'secondary';
    const timeAgo = getTimeAgo(incident.created_at);
    const relevanceScore = Math.round((incident.relevance_score || 0) * 100);
    
    const sourceIcon = incident.source === 'weather' ? 'cloud' : 'newspaper';
    
    return `
        <div class="card mb-3 incident-card" data-incident-id="${incident.id}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="d-flex align-items-center">
                        <i data-feather="${sourceIcon}" class="me-2 text-${severityColor}"></i>
                        <span class="badge bg-${severityColor} me-2">${incident.severity.toUpperCase()}</span>
                        <small class="text-muted">${incident.source.toUpperCase()}</small>
                    </div>
                    <small class="text-muted">${timeAgo}</small>
                </div>
                
                <h6 class="card-title">${escapeHtml(incident.title)}</h6>
                
                <p class="card-text text-muted mb-2">
                    ${escapeHtml(incident.ai_summary || incident.description).substring(0, 200)}${(incident.ai_summary || incident.description).length > 200 ? '...' : ''}
                </p>
                
                <div class="d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center">
                        <i data-feather="map-pin" class="me-1" style="width: 16px; height: 16px;"></i>
                        <small class="text-muted">${escapeHtml(incident.location)}</small>
                        <span class="mx-2">•</span>
                        <small class="text-muted">${incident.category.toUpperCase()}</small>
                    </div>
                    <div class="d-flex align-items-center">
                        <small class="text-muted me-2">Relevance: ${relevanceScore}%</small>
                        <button class="btn btn-sm btn-outline-primary" onclick="showIncidentDetails(${incident.id})">
                            <i data-feather="eye" class="me-1" style="width: 14px; height: 14px;"></i>
                            Details
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function showIncidentDetails(incidentId) {
    try {
        const response = await fetch(`/api/incidents/${incidentId}`);
        const data = await response.json();
        
        if (data.success) {
            const incident = data.incident;
            
            document.getElementById('modal-title').textContent = incident.title;
            
            const modalBody = document.getElementById('modal-body');
            modalBody.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Incident Information</h6>
                        <p><strong>Severity:</strong> <span class="badge bg-${getSeverityColor(incident.severity)}">${incident.severity.toUpperCase()}</span></p>
                        <p><strong>Category:</strong> ${incident.category.toUpperCase()}</p>
                        <p><strong>Source:</strong> ${incident.source.toUpperCase()}</p>
                        <p><strong>Location:</strong> ${escapeHtml(incident.location)}</p>
                        <p><strong>Relevance Score:</strong> ${Math.round((incident.relevance_score || 0) * 100)}%</p>
                        <p><strong>Verified:</strong> ${incident.is_verified ? '✅ Yes' : '❌ No'}</p>
                    </div>
                    <div class="col-md-6">
                        <h6>Timeline</h6>
                        <p><strong>Reported:</strong> ${formatDateTime(incident.created_at)}</p>
                        <p><strong>Last Updated:</strong> ${formatDateTime(incident.updated_at)}</p>
                        <p><strong>Time Ago:</strong> ${getTimeAgo(incident.created_at)}</p>
                    </div>
                </div>
                
                <hr>
                
                <h6>AI Summary</h6>
                <div class="alert alert-info">
                    <i data-feather="cpu" class="me-2"></i>
                    ${escapeHtml(incident.ai_summary || 'No AI summary available')}
                </div>
                
                <h6>Full Description</h6>
                <p>${escapeHtml(incident.description)}</p>
            `;
            
            // Handle source link
            const sourceLink = document.getElementById('modal-source-link');
            if (incident.url) {
                sourceLink.href = incident.url;
                sourceLink.style.display = 'inline-block';
            } else {
                sourceLink.style.display = 'none';
            }
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('incidentModal'));
            modal.show();
            
            // Re-initialize feather icons
            feather.replace();
            
        } else {
            alert('Failed to load incident details: ' + data.error);
        }
    } catch (error) {
        console.error('Error loading incident details:', error);
        alert('Error loading incident details. Please try again.');
    }
}

// Utility functions
function refreshDashboard() {
    loadDashboard();
}

function showLoadingState() {
    document.getElementById('loading-state').style.display = 'block';
    document.getElementById('no-incidents-state').style.display = 'none';
    document.getElementById('error-state').style.display = 'none';
    document.getElementById('incidents-container').innerHTML = '';
}

function hideLoadingState() {
    document.getElementById('loading-state').style.display = 'none';
}

function showNoIncidentsState() {
    document.getElementById('no-incidents-state').style.display = 'block';
    document.getElementById('incidents-container').innerHTML = '';
}

function hideNoIncidentsState() {
    document.getElementById('no-incidents-state').style.display = 'none';
}

function showErrorState() {
    document.getElementById('error-state').style.display = 'block';
    document.getElementById('loading-state').style.display = 'none';
    document.getElementById('incidents-container').innerHTML = '';
}

function updateIncidentCount(count) {
    const countElement = document.getElementById('incident-count');
    countElement.textContent = `${count} incident${count !== 1 ? 's' : ''}`;
}

function updateLastUpdateTime() {
    const now = new Date();
    document.getElementById('last-update-time').textContent = now.toLocaleTimeString();
}

function getTimeAgo(dateString) {
    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function getSeverityColor(severity) {
    const colors = {
        'low': 'success',
        'medium': 'warning',
        'high': 'warning',
        'critical': 'danger'
    };
    return colors[severity] || 'secondary';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
