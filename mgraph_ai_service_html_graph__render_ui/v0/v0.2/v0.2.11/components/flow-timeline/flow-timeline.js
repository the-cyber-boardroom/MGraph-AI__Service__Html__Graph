/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Flow Timeline Component
   v0.2.11 - Jaeger-like visualization of FLeT execution flows
   
   Features:
   - List all FLeTs executed for an entity
   - Show task breakdown with timing bars
   - Display execution logs
   - Visual timeline representation
   ═══════════════════════════════════════════════════════════════════════════════ */

class FlowTimeline extends BaseComponent {
    constructor() {
        super();
        this.namespace = '';
        this.cacheId = '';
        this.flows = [];
        this.selectedFlow = null;
        this.flowData = null;
        this.isLoading = false;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Lifecycle
    // ═══════════════════════════════════════════════════════════════════════════

    bindElements() {
        this.flowListEl = this.$('#flow-list');
        this.flowDetailsEl = this.$('#flow-details');
    }

    setupEventListeners() {
        this.addTrackedListener(this.flowListEl, 'click', this.handleFlowClick);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Public API
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Load flows for a cache entity
     */
    async loadFlows(namespace, cacheId) {
        this.namespace = namespace;
        this.cacheId = cacheId;
        this.flows = [];
        this.selectedFlow = null;
        this.flowData = null;
        this.isLoading = true;
        
        this.showLoading();

        try {
            const response = await window.apiClient.listFlows(namespace, cacheId);

            if (response.success !== false) {
                this.flows = response.flets || response.flows || [];
                this.isLoading = false;
                this.renderFlowList();

                // Auto-select first flow
                if (this.flows.length > 0) {
                    this.selectFlow(this.flows[0]);
                }
            } else {
                this.isLoading = false;
                this.showError('Failed to load flows');
            }
        } catch (error) {
            console.error('[FlowTimeline] Load flows error:', error);
            this.isLoading = false;
            this.showError(error.message || 'Failed to load flows');
        }
    }

    /**
     * Clear all data
     */
    clear() {
        this.namespace = '';
        this.cacheId = '';
        this.flows = [];
        this.selectedFlow = null;
        this.flowData = null;
        this.isLoading = false;
        this.renderEmpty();
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Handlers
    // ═══════════════════════════════════════════════════════════════════════════

    handleFlowClick(e) {
        const flowItem = e.target.closest('.flow-item');
        if (flowItem) {
            this.selectFlow(flowItem.dataset.flet);
        }
    }

    /**
     * Select and load a specific flow
     */
    async selectFlow(fletName) {
        this.selectedFlow = fletName;
        this.flowData = null;

        // Update selection UI
        this.$$('.flow-item').forEach(el => {
            el.classList.toggle('selected', el.dataset.flet === fletName);
        });

        try {
            // Load durations, logs, and tasks in parallel
            const [durationsRes, logsRes, tasksRes] = await Promise.all([
                window.apiClient.getFlowDurations(this.namespace, this.cacheId, fletName).catch(() => null),
                window.apiClient.getFlowLogs(this.namespace, this.cacheId, fletName).catch(() => null),
                window.apiClient.getFlowTasks(this.namespace, this.cacheId, fletName).catch(() => null)
            ]);

            this.flowData = {
                name: fletName,
                durations: durationsRes?.durations || {},
                totalDuration: durationsRes?.total_duration || 0,
                logs: logsRes?.logs || [],
                tasks: tasksRes?.tasks || []
            };

            this.renderFlowDetails();

        } catch (error) {
            console.error('[FlowTimeline] Load flow details error:', error);
            this.showFlowError('Failed to load flow details');
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Rendering
    // ═══════════════════════════════════════════════════════════════════════════

    renderFlowList() {
        if (this.flows.length === 0) {
            this.flowListEl.innerHTML = `
                <div class="flow-timeline-empty">
                    No flows recorded for this entity
                </div>
            `;
            return;
        }

        this.flowListEl.innerHTML = this.flows.map(flet => `
            <div class="flow-item ${flet === this.selectedFlow ? 'selected' : ''}" 
                 data-flet="${this.escapeHtml(flet)}">
                <div class="flow-item-header">
                    <span class="flow-item-name">${this.formatFlowName(flet)}</span>
                    <span class="flow-item-duration" id="duration-${this.escapeHtml(flet)}">-</span>
                </div>
                <div class="flow-item-tasks" id="tasks-${this.escapeHtml(flet)}">
                    Click to load details
                </div>
            </div>
        `).join('');
    }

    renderFlowDetails() {
        if (!this.flowData) {
            this.flowDetailsEl.innerHTML = '';
            return;
        }

        const fd = this.flowData;

        // Update duration in flow list
        const durationEl = this.$(`#duration-${this.escapeHtml(fd.name)}`);
        if (durationEl && fd.totalDuration) {
            durationEl.textContent = `${(fd.totalDuration * 1000).toFixed(1)} ms`;
        }

        // Update tasks hint
        const tasksHint = this.$(`#tasks-${this.escapeHtml(fd.name)}`);
        if (tasksHint) {
            const taskCount = Object.keys(fd.durations).length;
            tasksHint.textContent = `${taskCount} task${taskCount !== 1 ? 's' : ''}`;
        }

        // Render timeline chart
        const timelineHtml = this.renderTimelineChart(fd.durations, fd.totalDuration);
        
        // Render logs
        const logsHtml = this.renderLogs(fd.logs);

        this.flowDetailsEl.innerHTML = `
            ${timelineHtml}
            ${logsHtml}
        `;
    }

    renderTimelineChart(durations, totalDuration) {
        if (!durations || Object.keys(durations).length === 0) {
            return '<div class="flow-timeline-empty">No timing data available</div>';
        }

        // Convert durations object to array
        const tasks = Object.entries(durations).map(([name, duration]) => ({
            name,
            duration: typeof duration === 'number' ? duration : 0
        }));

        // Sort by duration descending
        tasks.sort((a, b) => b.duration - a.duration);

        // Calculate bar widths relative to total
        const maxDuration = totalDuration || Math.max(...tasks.map(t => t.duration));

        const barsHtml = tasks.slice(0, 15).map(task => {
            const widthPercent = maxDuration > 0 ? (task.duration / maxDuration * 100) : 0;
            const durationMs = (task.duration * 1000).toFixed(1);
            
            return `
                <div class="timeline-task">
                    <span class="timeline-task-name" title="${this.escapeHtml(task.name)}">
                        ${this.escapeHtml(this.truncate(task.name, 20))}
                    </span>
                    <div class="timeline-task-bar-container">
                        <div class="timeline-task-bar" style="width: ${widthPercent}%"></div>
                    </div>
                    <span class="timeline-task-duration">${durationMs} ms</span>
                </div>
            `;
        }).join('');

        return `
            <div class="flow-timeline-chart">
                <div class="chart-header">
                    Task Breakdown (${Math.min(15, tasks.length)} of ${tasks.length})
                </div>
                ${barsHtml}
                <div class="chart-footer">
                    Total: ${(totalDuration * 1000).toFixed(1)} ms
                </div>
            </div>
        `;
    }

    renderLogs(logs) {
        if (!logs || logs.length === 0) {
            return '';
        }

        const logsHtml = logs.slice(0, 30).map(log => `
            <div class="flow-log-entry">
                <span class="flow-log-level ${(log.level || 'INFO').toLowerCase()}">${log.level || 'INFO'}</span>
                <span class="flow-log-message">${this.escapeHtml(log.message || '')}</span>
            </div>
        `).join('');

        return `
            <div class="flow-logs">
                <div class="flow-logs-title">Execution Logs (${Math.min(30, logs.length)} of ${logs.length})</div>
                ${logsHtml}
            </div>
        `;
    }

    renderEmpty() {
        this.flowListEl.innerHTML = `
            <div class="flow-timeline-empty">
                Select an entity to view its flow data
            </div>
        `;
        this.flowDetailsEl.innerHTML = '';
    }

    showLoading() {
        this.flowListEl.innerHTML = `
            <div class="flow-timeline-loading">
                <div class="spinner"></div>
                <span>Loading flows...</span>
            </div>
        `;
        this.flowDetailsEl.innerHTML = '';
    }

    showError(message) {
        this.flowListEl.innerHTML = `
            <div class="flow-timeline-empty error">${this.escapeHtml(message)}</div>
        `;
    }

    showFlowError(message) {
        this.flowDetailsEl.innerHTML = `
            <div class="flow-timeline-empty error">${this.escapeHtml(message)}</div>
        `;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Utilities
    // ═══════════════════════════════════════════════════════════════════════════

    formatFlowName(name) {
        return name
            .replace(/-/g, ' ')
            .replace(/_/g, ' ')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    truncate(str, maxLength) {
        if (!str) return '';
        if (str.length <= maxLength) return str;
        return str.substring(0, maxLength - 3) + '...';
    }
}

customElements.define('flow-timeline', FlowTimeline);
