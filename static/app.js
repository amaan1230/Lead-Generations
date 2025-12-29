// ===== Global State =====
let allLeads = [];
let currentLeadId = null;
let bulkPreviews = {};

// ===== API Base URL =====
const API_BASE = 'http://localhost:5000/api';

// ===== Theme Toggle =====
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
if (savedTheme === 'dark') {
    body.classList.add('dark-mode');
}

themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    const theme = body.classList.contains('dark-mode') ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
});

// ===== Navigation =====
const navItems = document.querySelectorAll('.nav-item');
const pages = document.querySelectorAll('.page');

navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const pageName = item.dataset.page;

        // Update active nav item
        navItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');

        // Show corresponding page
        pages.forEach(page => page.classList.remove('active'));
        document.getElementById(`${pageName}-page`).classList.add('active');

        // Load page-specific data
        if (pageName === 'dashboard') {
            loadDashboard();
        } else if (pageName === 'campaign') {
            loadCampaign();
        } else if (pageName === 'scraper') {
            // No specific load function needed yet
        } else if (pageName === 'analytics') {
            loadAnalytics();
        }
    });
});

// ===== Campaign Tabs =====
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;

        // Update active tab
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Show corresponding content
        tabContents.forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// ===== Toast Notification =====
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ===== Modal Management =====
const emailModal = document.getElementById('emailModal');
const progressModal = document.getElementById('progressModal');
const closeModalBtn = document.getElementById('closeModal');

closeModalBtn.addEventListener('click', () => {
    emailModal.classList.remove('active');
});

emailModal.querySelector('.modal-overlay').addEventListener('click', () => {
    emailModal.classList.remove('active');
});

// ===== API Functions =====
async function fetchLeads() {
    try {
        const response = await fetch(`${API_BASE}/leads`);
        if (!response.ok) throw new Error('Failed to fetch leads');
        const data = await response.json();
        allLeads = data.leads || [];
        return allLeads;
    } catch (error) {
        console.error('Error fetching leads:', error);
        showToast('Failed to load leads', 'error');
        return [];
    }
}

async function previewEmail(leadId) {
    try {
        const response = await fetch(`${API_BASE}/preview-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lead_id: leadId })
        });
        if (!response.ok) throw new Error('Failed to generate preview');
        return await response.json();
    } catch (error) {
        console.error('Error generating preview:', error);
        showToast('Failed to generate email preview', 'error');
        return null;
    }
}

async function sendEmail(leadId, subject, body) {
    try {
        const response = await fetch(`${API_BASE}/send-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lead_id: leadId, subject, body })
        });
        if (!response.ok) throw new Error('Failed to send email');
        return await response.json();
    } catch (error) {
        console.error('Error sending email:', error);
        showToast('Failed to send email', 'error');
        return { success: false };
    }
}

async function bulkPreview() {
    try {
        const response = await fetch(`${API_BASE}/bulk-preview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error('Failed to generate bulk preview');
        return await response.json();
    } catch (error) {
        console.error('Error generating bulk preview:', error);
        showToast('Failed to generate bulk preview', 'error');
        return null;
    }
}

async function bulkSend(selectedLeads) {
    try {
        const response = await fetch(`${API_BASE}/bulk-send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lead_ids: selectedLeads })
        });
        if (!response.ok) throw new Error('Failed to send bulk emails');
        return await response.json();
    } catch (error) {
        console.error('Error sending bulk emails:', error);
        showToast('Failed to send bulk emails', 'error');
        return { success: false };
    }
}

async function runScheduler() {
    try {
        const response = await fetch(`${API_BASE}/run-scheduler`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error('Failed to run scheduler');
        return await response.json();
    } catch (error) {
        console.error('Error running scheduler:', error);
        showToast('Failed to run scheduler', 'error');
        return { success: false };
    }
}

async function runScraper(query) {
    try {
        const response = await fetch(`${API_BASE}/run-scraper`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        if (!response.ok) throw new Error('Failed to start scraper');
        return await response.json();
    } catch (error) {
        console.error('Error starting scraper:', error);
        showToast('Failed to start scraper', 'error');
        return { success: false };
    }
}

async function fetchAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/analytics`);
        if (!response.ok) throw new Error('Failed to fetch analytics');
        return await response.json();
    } catch (error) {
        console.error('Error fetching analytics:', error);
        showToast('Failed to fetch analytics', 'error');
        return null;
    }
}

// ===== Dashboard Functions =====
async function loadDashboard() {
    const leads = await fetchLeads();

    // Update stats
    document.getElementById('totalLeads').textContent = leads.length;

    const contacted = leads.filter(l =>
        ['CONTACTED', 'FOLLOWUP_1', 'FOLLOWUP_2', 'FOLLOWUP_3'].includes(l.status)
    ).length;
    document.getElementById('contacted').textContent = contacted;
    document.getElementById('emailsSent').textContent = contacted;

    const followups = leads.filter(l =>
        ['FOLLOWUP_1', 'FOLLOWUP_2', 'FOLLOWUP_3'].includes(l.status)
    ).length;
    document.getElementById('followups').textContent = followups;

    // Render leads table
    renderLeadsTable(leads);
}

function renderLeadsTable(leads) {
    const tbody = document.getElementById('leadsTableBody');

    if (leads.length === 0) {
        tbody.innerHTML = `
            <tr class="loading-row">
                <td colspan="7">
                    <div class="empty-state">
                        <p>No leads found</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = leads.map(lead => `
        <tr>
            <td><strong>${lead.clinic_name || 'N/A'}</strong></td>
            <td>${lead.email || 'N/A'}</td>
            <td><a href="${lead.website}" target="_blank" style="color: var(--primary);">${truncate(lead.website, 30)}</a></td>
            <td><span class="status-badge ${getStatusClass(lead.status)}">${lead.status}</span></td>
            <td>${lead.follow_up_count || 0}</td>
            <td>${formatDate(lead.last_contacted)}</td>
            <td>
                ${lead.status === 'ENRICHED' ?
            `<button class="btn btn-primary" onclick="openEmailPreview(${lead.id})" style="padding: 0.375rem 0.75rem; font-size: 0.75rem;">Preview</button>` :
            '-'
        }
            </td>
        </tr>
    `).join('');
}

// ===== Campaign Functions =====
async function loadCampaign() {
    const leads = await fetchLeads();
    const enrichedLeads = leads.filter(l => l.status === 'ENRICHED');

    // Individual tab
    renderIndividualLeads(enrichedLeads);

    // Bulk tab
    document.getElementById('bulkLeadCount').textContent = `${enrichedLeads.length} leads`;

    // Follow-ups tab
    const followupLeads = leads.filter(l =>
        ['CONTACTED', 'FOLLOWUP_1', 'FOLLOWUP_2', 'FOLLOWUP_3'].includes(l.status)
    );
    renderFollowupLeads(followupLeads);
}

function renderIndividualLeads(leads) {
    const container = document.getElementById('individualLeadsList');

    if (leads.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                    <circle cx="32" cy="32" r="30" stroke="currentColor" stroke-width="2" opacity="0.2"/>
                    <path d="M32 20V32L40 36" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <p>No enriched leads available</p>
            </div>
        `;
        return;
    }

    container.innerHTML = leads.map(lead => `
        <div class="card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h4 style="margin-bottom: 0.5rem;">📋 ${lead.clinic_name} - ${lead.email}</h4>
                    <p class="text-muted" style="margin: 0.25rem 0;"><strong>Website:</strong> ${lead.website}</p>
                    <p class="text-muted" style="margin: 0.25rem 0;"><strong>Contact:</strong> ${lead.name || 'N/A'}</p>
                </div>
                <button class="btn btn-primary" onclick="openEmailPreview(${lead.id})">
                    🔍 Preview Email
                </button>
            </div>
        </div>
    `).join('');
}

function renderFollowupLeads(leads) {
    const container = document.getElementById('followupLeadsList');

    if (leads.length === 0) {
        container.innerHTML = '<p class="text-muted">No leads in follow-up stages</p>';
        return;
    }

    container.innerHTML = `
        <table class="leads-table">
            <thead>
                <tr>
                    <th>Clinic</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Follow-ups</th>
                    <th>Last Contacted</th>
                </tr>
            </thead>
            <tbody>
                ${leads.map(lead => `
                    <tr>
                        <td><strong>${lead.clinic_name}</strong></td>
                        <td>${lead.email}</td>
                        <td><span class="status-badge ${getStatusClass(lead.status)}">${lead.status}</span></td>
                        <td>${lead.follow_up_count || 0}</td>
                        <td>${formatDate(lead.last_contacted)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ===== Email Preview Modal =====
async function openEmailPreview(leadId) {
    currentLeadId = leadId;
    emailModal.classList.add('active');

    // Show loading state
    document.getElementById('emailSubject').value = 'Generating...';
    document.getElementById('emailBody').value = 'Generating personalized email...';

    // Fetch preview
    const preview = await previewEmail(leadId);

    if (preview) {
        document.getElementById('emailSubject').value = preview.subject;
        document.getElementById('emailBody').value = preview.body;
    }
}

document.getElementById('sendEmailBtn').addEventListener('click', async () => {
    const subject = document.getElementById('emailSubject').value;
    const body = document.getElementById('emailBody').value;

    if (!currentLeadId) return;

    emailModal.classList.remove('active');
    progressModal.classList.add('active');
    document.getElementById('progressTitle').textContent = 'Sending email...';
    document.getElementById('progressText').textContent = 'Please wait';

    const result = await sendEmail(currentLeadId, subject, body);

    progressModal.classList.remove('active');

    if (result.success) {
        showToast('Email sent successfully!', 'success');
        loadDashboard();
        loadCampaign();
    } else {
        showToast('Failed to send email', 'error');
    }
});

document.getElementById('discardEmailBtn').addEventListener('click', () => {
    emailModal.classList.remove('active');
});

// ===== Bulk Send =====
document.getElementById('previewAllBtn').addEventListener('click', async () => {
    const btn = document.getElementById('previewAllBtn');
    btn.disabled = true;
    btn.innerHTML = '<div class="loading-spinner"></div> Generating...';

    const previews = await bulkPreview();

    btn.disabled = false;
    btn.innerHTML = '🔍 Preview All Emails';

    if (previews && previews.previews) {
        bulkPreviews = previews.previews;
        renderBulkPreviews(previews.previews);
        document.getElementById('bulkPreviewContainer').style.display = 'block';
    }
});

function renderBulkPreviews(previews) {
    const container = document.getElementById('bulkLeadsList');
    const previewArray = Object.entries(previews);

    container.innerHTML = previewArray.map(([leadId, data]) => `
        <div class="card" style="margin-bottom: 1rem;">
            <label style="display: flex; align-items: start; gap: 1rem; cursor: pointer;">
                <input type="checkbox" class="bulk-checkbox" data-lead-id="${leadId}" checked style="margin-top: 0.25rem;">
                <div style="flex: 1;">
                    <h4 style="margin-bottom: 0.5rem;">✅ ${data.lead.clinic_name} (${data.lead.email})</h4>
                    <details style="margin-top: 0.5rem;">
                        <summary style="cursor: pointer; color: var(--primary); font-weight: 600;">Preview Email</summary>
                        <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-tertiary); border-radius: var(--radius-md);">
                            <p style="margin-bottom: 0.5rem;"><strong>Subject:</strong> ${data.subject}</p>
                            <p style="margin-bottom: 0.5rem;"><strong>Body:</strong></p>
                            <pre style="white-space: pre-wrap; font-family: inherit; font-size: 0.875rem;">${data.body}</pre>
                        </div>
                    </details>
                </div>
            </label>
        </div>
    `).join('');

    updateSelectedCount();

    // Add event listeners to checkboxes
    document.querySelectorAll('.bulk-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedCount);
    });
}

function updateSelectedCount() {
    const checkboxes = document.querySelectorAll('.bulk-checkbox');
    const checked = document.querySelectorAll('.bulk-checkbox:checked').length;
    const total = checkboxes.length;
    document.getElementById('selectedCount').textContent = `${checked} of ${total} emails`;
}

document.getElementById('sendAllBtn').addEventListener('click', async () => {
    const selectedCheckboxes = document.querySelectorAll('.bulk-checkbox:checked');
    const selectedLeadIds = Array.from(selectedCheckboxes).map(cb => parseInt(cb.dataset.leadId));

    if (selectedLeadIds.length === 0) {
        showToast('No leads selected', 'error');
        return;
    }

    // Show progress modal
    progressModal.classList.add('active');
    document.getElementById('progressTitle').textContent = 'Sending bulk emails...';

    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressText = document.getElementById('progressText');

    // Simulate progress (in real implementation, this would be updated via API)
    let progress = 0;
    const interval = setInterval(() => {
        progress += 10;
        if (progress <= 90) {
            progressFill.style.width = `${progress}%`;
            progressPercent.textContent = `${progress}%`;
        }
    }, 300);

    const result = await bulkSend(selectedLeadIds);

    clearInterval(interval);
    progressFill.style.width = '100%';
    progressPercent.textContent = '100%';

    setTimeout(() => {
        progressModal.classList.remove('active');

        if (result.success) {
            showToast(`Bulk send complete! Sent: ${result.sent}, Failed: ${result.failed}`, 'success');
            document.getElementById('bulkPreviewContainer').style.display = 'none';
            loadDashboard();
            loadCampaign();
        } else {
            showToast('Bulk send failed', 'error');
        }
    }, 500);
});

document.getElementById('discardAllBtn').addEventListener('click', () => {
    document.getElementById('bulkPreviewContainer').style.display = 'none';
    bulkPreviews = {};
});

// ===== Follow-up Scheduler =====
document.getElementById('runSchedulerBtn').addEventListener('click', async () => {
    const btn = document.getElementById('runSchedulerBtn');
    btn.disabled = true;
    btn.innerHTML = '<div class="loading-spinner"></div> Running...';

    const result = await runScheduler();

    btn.disabled = false;
    btn.innerHTML = '🔄 Run Follow-up Scheduler';

    if (result.success) {
        showToast('Follow-up scheduler completed!', 'success');
        loadDashboard();
        loadCampaign();
    }
});

// ===== Refresh Button =====
document.getElementById('refreshBtn').addEventListener('click', () => {
    loadDashboard();
    showToast('Dashboard refreshed', 'success');
});

// ===== Scraper Functions =====
document.getElementById('runScraperBtn').addEventListener('click', async () => {
    const query = document.getElementById('searchQuery').value;
    if (!query) {
        showToast('Please enter a search query', 'error');
        return;
    }

    const btn = document.getElementById('runScraperBtn');
    const progress = document.getElementById('scraperProgress');
    const consoleOut = document.getElementById('scraperConsole');

    btn.disabled = true;
    progress.style.display = 'block';
    consoleOut.innerHTML = `<div class="log-line">Starting scraper for: "${query}"...</div>`;

    // Simulate real-time logs (since we don't have websocket set up yet)
    let logs = [
        "Initializing Google Search scraper...",
        "Searching for leads...",
        "Found potential leads...",
        "Extracting contact information...",
        "Verifying email addresses...",
        "Saving leads to database..."
    ];

    let i = 0;
    const logInterval = setInterval(() => {
        if (i < logs.length) {
            consoleOut.innerHTML += `<div class="log-line">${logs[i]}</div>`;
            consoleOut.scrollTop = consoleOut.scrollHeight;
            i++;
        }
    }, 1500);

    const result = await runScraper(query);

    clearInterval(logInterval);
    btn.disabled = false;

    if (result.success) {
        consoleOut.innerHTML += `<div class="log-line success">✅ Scraping complete! Found ${result.count} new leads.</div>`;
        showToast(`Scraping complete! Added ${result.count} leads`, 'success');
    } else {
        consoleOut.innerHTML += `<div class="log-line error">❌ Error: ${result.error}</div>`;
        showToast('Scraping failed', 'error');
    }
});

// ===== Analytics Functions =====
async function loadAnalytics() {
    const data = await fetchAnalytics();

    if (!data) return;

    // Update stats
    document.getElementById('analyticsResponseRate').textContent = '12.5%'; // active placeholder
    document.getElementById('analyticsConversionRate').textContent = '3.2%'; // active placeholder

    // Render Charts
    renderStatusChart(data.status_counts);
    renderPerformanceChart(data.daily_stats);
}

function renderStatusChart(statusCounts) {
    const values = Object.values(statusCounts);
    const labels = Object.keys(statusCounts);

    const data = [{
        values: values,
        labels: labels,
        type: 'pie',
        hole: 0.4,
        marker: {
            colors: ['#667eea', '#764ba2', '#48bb78', '#ed8936', '#f56565'] // Custom colors
        }
    }];

    const layout = {
        height: 300,
        margin: { t: 0, b: 0, l: 0, r: 0 },
        showlegend: true,
        bg_color: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)' // Transparent background
    };

    Plotly.newPlot('statusChart', data, layout, { displayModeBar: false });
}

function renderPerformanceChart(dailyStats) {
    // Placeholder data if no real history exists
    const dates = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const sent = [5, 12, 8, 15, 10, 4, 2];
    const opened = [2, 6, 4, 8, 5, 2, 1];

    const trace1 = {
        x: dates,
        y: sent,
        type: 'bar',
        name: 'Emails Sent',
        marker: { color: '#667eea' }
    };

    const trace2 = {
        x: dates,
        y: opened,
        type: 'bar',
        name: 'Opened',
        marker: { color: '#48bb78' }
    };

    const data = [trace1, trace2];

    const layout = {
        height: 300,
        margin: { t: 20, b: 30, l: 40, r: 20 },
        barmode: 'group',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot('performanceChart', data, layout, { displayModeBar: false });
}

// ===== Status Filter =====
document.getElementById('statusFilter').addEventListener('change', (e) => {
    const status = e.target.value;
    const filtered = status ? allLeads.filter(l => l.status === status) : allLeads;
    renderLeadsTable(filtered);
});

// ===== Utility Functions =====
function truncate(str, length) {
    if (!str) return 'N/A';
    return str.length > length ? str.substring(0, length) + '...' : str;
}

function formatDate(dateStr) {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function getStatusClass(status) {
    if (status === 'ENRICHED') return 'enriched';
    if (status === 'CONTACTED') return 'contacted';
    if (['FOLLOWUP_1', 'FOLLOWUP_2', 'FOLLOWUP_3'].includes(status)) return 'followup';
    if (status === 'CLOSED') return 'closed';
    return '';
}

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});
