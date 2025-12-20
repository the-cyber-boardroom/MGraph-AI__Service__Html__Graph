/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - QA Control Panel Component
   v0.2.0 - Visual controls for QA test execution
   
   Provides UI for:
   - Mode selection (Automated/Interactive/Teleport)
   - Scenario selection and execution
   - Step-by-step controls (Next/Pause/Resume/Stop)
   - Real-time status display
   ═══════════════════════════════════════════════════════════════════════════════ */

class QAControlPanel extends HTMLElement {
    constructor() {
        super();
        this.engine = null;
        this.selectedScenario = null;
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }

    setEngine(engine) {
        this.engine = engine;
        
        // Subscribe to engine state changes
        this.engine.onStateChange = (state) => this.updateState(state);
        this.engine.onStepComplete = (result, index, total) => this.onStepComplete(result, index, total);
        this.engine.onScenarioComplete = (summary) => this.onScenarioComplete(summary);
        this.engine.onError = (error, step) => this.onError(error, step);
        
        this.updateScenarioList();
    }

    render() {
        this.innerHTML = `
            <style>
                .qa-control-panel {
                    font-family: system-ui, -apple-system, sans-serif;
                    background: #1a1a2e;
                    color: #eee;
                    border-radius: 8px;
                    padding: 16px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                }
                
                .qa-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 16px;
                    padding-bottom: 12px;
                    border-bottom: 1px solid #333;
                }
                
                .qa-title {
                    font-size: 1.1em;
                    font-weight: 600;
                    color: #6366f1;
                }
                
                .qa-section {
                    margin-bottom: 16px;
                }
                
                .qa-section-title {
                    font-size: 0.85em;
                    color: #888;
                    margin-bottom: 8px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .qa-mode-buttons {
                    display: flex;
                    gap: 8px;
                }
                
                .qa-mode-btn {
                    flex: 1;
                    padding: 8px 12px;
                    border: 1px solid #444;
                    background: #252542;
                    color: #aaa;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 0.85em;
                    transition: all 0.2s;
                }
                
                .qa-mode-btn:hover {
                    background: #2a2a4a;
                    border-color: #555;
                }
                
                .qa-mode-btn.active {
                    background: #6366f1;
                    border-color: #6366f1;
                    color: white;
                }
                
                .qa-select {
                    width: 100%;
                    padding: 10px 12px;
                    background: #252542;
                    border: 1px solid #444;
                    border-radius: 6px;
                    color: #eee;
                    font-size: 0.9em;
                    cursor: pointer;
                }
                
                .qa-select:focus {
                    outline: none;
                    border-color: #6366f1;
                }
                
                .qa-controls {
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                }
                
                .qa-btn {
                    padding: 10px 16px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 0.9em;
                    font-weight: 500;
                    transition: all 0.2s;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }
                
                .qa-btn:disabled {
                    opacity: 0.4;
                    cursor: not-allowed;
                }
                
                .qa-btn-primary {
                    background: #10b981;
                    color: white;
                    flex: 1;
                }
                
                .qa-btn-primary:hover:not(:disabled) {
                    background: #059669;
                }
                
                .qa-btn-secondary {
                    background: #374151;
                    color: white;
                }
                
                .qa-btn-secondary:hover:not(:disabled) {
                    background: #4b5563;
                }
                
                .qa-btn-warning {
                    background: #f59e0b;
                    color: white;
                }
                
                .qa-btn-warning:hover:not(:disabled) {
                    background: #d97706;
                }
                
                .qa-btn-danger {
                    background: #ef4444;
                    color: white;
                }
                
                .qa-btn-danger:hover:not(:disabled) {
                    background: #dc2626;
                }
                
                .qa-btn-teleport {
                    background: #8b5cf6;
                    color: white;
                }
                
                .qa-btn-teleport:hover:not(:disabled) {
                    background: #7c3aed;
                }
                
                .qa-status {
                    padding: 12px;
                    background: #252542;
                    border-radius: 6px;
                    margin-top: 12px;
                }
                
                .qa-status-row {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 6px;
                    font-size: 0.85em;
                }
                
                .qa-status-label {
                    color: #888;
                }
                
                .qa-status-value {
                    color: #eee;
                    font-weight: 500;
                }
                
                .qa-status-value.running {
                    color: #10b981;
                }
                
                .qa-status-value.paused {
                    color: #f59e0b;
                }
                
                .qa-status-value.stopped {
                    color: #888;
                }
                
                .qa-progress {
                    margin-top: 12px;
                }
                
                .qa-progress-bar {
                    height: 6px;
                    background: #333;
                    border-radius: 3px;
                    overflow: hidden;
                }
                
                .qa-progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #6366f1, #8b5cf6);
                    transition: width 0.3s ease;
                    width: 0%;
                }
                
                .qa-progress-text {
                    display: flex;
                    justify-content: space-between;
                    margin-top: 6px;
                    font-size: 0.8em;
                    color: #888;
                }
                
                .qa-current-step {
                    margin-top: 12px;
                    padding: 12px;
                    background: #1e1e38;
                    border-radius: 6px;
                    border-left: 3px solid #6366f1;
                }
                
                .qa-step-name {
                    font-weight: 500;
                    color: #eee;
                    margin-bottom: 4px;
                }
                
                .qa-step-description {
                    font-size: 0.85em;
                    color: #888;
                }
                
                .qa-results {
                    margin-top: 12px;
                    max-height: 200px;
                    overflow-y: auto;
                }
                
                .qa-result-item {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 6px 0;
                    font-size: 0.85em;
                    border-bottom: 1px solid #333;
                }
                
                .qa-result-item:last-child {
                    border-bottom: none;
                }
                
                .qa-result-icon {
                    font-size: 1em;
                }
                
                .qa-result-icon.pass {
                    color: #10b981;
                }
                
                .qa-result-icon.fail {
                    color: #ef4444;
                }
                
                .qa-result-name {
                    flex: 1;
                    color: #ccc;
                }
                
                .qa-result-duration {
                    color: #666;
                    font-size: 0.8em;
                }
                
                .qa-teleport-section {
                    margin-top: 12px;
                    padding-top: 12px;
                    border-top: 1px solid #333;
                }
                
                .qa-teleport-row {
                    display: flex;
                    gap: 8px;
                    align-items: center;
                }
                
                .qa-teleport-input {
                    width: 60px;
                    padding: 8px;
                    background: #252542;
                    border: 1px solid #444;
                    border-radius: 6px;
                    color: #eee;
                    text-align: center;
                }
                
                .qa-summary {
                    margin-top: 12px;
                    padding: 12px;
                    border-radius: 6px;
                    text-align: center;
                }
                
                .qa-summary.success {
                    background: rgba(16, 185, 129, 0.2);
                    border: 1px solid #10b981;
                }
                
                .qa-summary.failure {
                    background: rgba(239, 68, 68, 0.2);
                    border: 1px solid #ef4444;
                }
                
                .qa-summary-title {
                    font-weight: 600;
                    font-size: 1.1em;
                    margin-bottom: 4px;
                }
                
                .qa-summary-stats {
                    font-size: 0.9em;
                    color: #ccc;
                }
            </style>
            
            <div class="qa-control-panel">
                <div class="qa-header">
                    <span class="qa-title">🧪 QA Test Runner</span>
                    <span id="qa-version">v0.2.0</span>
                </div>
                
                <div class="qa-section">
                    <div class="qa-section-title">Execution Mode</div>
                    <div class="qa-mode-buttons">
                        <button class="qa-mode-btn active" data-mode="automated" title="Run all steps rapidly">
                            ⚡ Fast
                        </button>
                        <button class="qa-mode-btn" data-mode="interactive" title="Step through with delays">
                            👁️ Slow-Mo
                        </button>
                        <button class="qa-mode-btn" data-mode="teleport" title="Jump to specific state">
                            🚀 Teleport
                        </button>
                    </div>
                </div>
                
                <div class="qa-section">
                    <div class="qa-section-title">Scenario</div>
                    <select id="qa-scenario-select" class="qa-select">
                        <option value="">-- Select a scenario --</option>
                    </select>
                </div>
                
                <div class="qa-section">
                    <div class="qa-section-title">Controls</div>
                    <div class="qa-controls">
                        <button id="qa-run-btn" class="qa-btn qa-btn-primary" disabled>
                            ▶️ Run
                        </button>
                        <button id="qa-next-btn" class="qa-btn qa-btn-secondary" disabled>
                            ⏭️ Next
                        </button>
                        <button id="qa-pause-btn" class="qa-btn qa-btn-warning" disabled>
                            ⏸️ Pause
                        </button>
                        <button id="qa-stop-btn" class="qa-btn qa-btn-danger" disabled>
                            ⏹️ Stop
                        </button>
                    </div>
                </div>
                
                <div id="qa-teleport-section" class="qa-teleport-section" style="display: none;">
                    <div class="qa-section-title">Teleport to Step</div>
                    <div class="qa-teleport-row">
                        <input type="number" id="qa-teleport-step" class="qa-teleport-input" min="1" value="1">
                        <button id="qa-teleport-btn" class="qa-btn qa-btn-teleport" disabled>
                            🚀 Teleport
                        </button>
                    </div>
                </div>
                
                <div class="qa-status">
                    <div class="qa-status-row">
                        <span class="qa-status-label">Status:</span>
                        <span id="qa-status-value" class="qa-status-value stopped">Idle</span>
                    </div>
                    <div class="qa-status-row">
                        <span class="qa-status-label">Mode:</span>
                        <span id="qa-mode-value" class="qa-status-value">Automated</span>
                    </div>
                    
                    <div class="qa-progress">
                        <div class="qa-progress-bar">
                            <div id="qa-progress-fill" class="qa-progress-fill"></div>
                        </div>
                        <div class="qa-progress-text">
                            <span id="qa-progress-current">Step 0</span>
                            <span id="qa-progress-total">of 0</span>
                        </div>
                    </div>
                </div>
                
                <div id="qa-current-step" class="qa-current-step" style="display: none;">
                    <div id="qa-step-name" class="qa-step-name"></div>
                    <div id="qa-step-description" class="qa-step-description"></div>
                </div>
                
                <div id="qa-results" class="qa-results"></div>
                
                <div id="qa-summary" class="qa-summary" style="display: none;"></div>
            </div>
        `;
    }

    setupEventListeners() {
        // Mode buttons
        this.querySelectorAll('.qa-mode-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.querySelectorAll('.qa-mode-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const mode = btn.dataset.mode;
                if (this.engine) {
                    this.engine.setMode(mode);
                }
                this.querySelector('#qa-mode-value').textContent = this.getModeLabel(mode);
                this.querySelector('#qa-teleport-section').style.display = 
                    mode === 'teleport' ? 'block' : 'none';
            });
        });

        // Scenario select
        this.querySelector('#qa-scenario-select').addEventListener('change', (e) => {
            this.selectedScenario = e.target.value;
            this.updateControlStates();
        });

        // Run button
        this.querySelector('#qa-run-btn').addEventListener('click', () => {
            if (this.selectedScenario && this.engine) {
                this.clearResults();
                this.engine.runScenario(this.selectedScenario);
            }
        });

        // Next button
        this.querySelector('#qa-next-btn').addEventListener('click', () => {
            if (this.engine) {
                this.engine.nextStep();
            }
        });

        // Pause button
        this.querySelector('#qa-pause-btn').addEventListener('click', () => {
            if (this.engine) {
                if (this.engine.isPaused) {
                    this.engine.resume();
                } else {
                    this.engine.pause();
                }
            }
        });

        // Stop button
        this.querySelector('#qa-stop-btn').addEventListener('click', () => {
            if (this.engine) {
                this.engine.stop();
            }
        });

        // Teleport button
        this.querySelector('#qa-teleport-btn').addEventListener('click', () => {
            const stepInput = this.querySelector('#qa-teleport-step');
            const targetStep = parseInt(stepInput.value, 10) - 1; // Convert to 0-indexed
            if (this.selectedScenario && this.engine && targetStep >= 0) {
                this.clearResults();
                this.engine.teleportToStep(this.selectedScenario, targetStep);
            }
        });
    }

    updateScenarioList() {
        const select = this.querySelector('#qa-scenario-select');
        const scenarios = this.engine.getScenarios();
        
        select.innerHTML = '<option value="">-- Select a scenario --</option>';
        scenarios.forEach(s => {
            const option = document.createElement('option');
            option.value = s.id;
            option.textContent = `${s.name} (${s.stepCount} steps)`;
            option.title = s.description;
            select.appendChild(option);
        });
    }

    updateState(state) {
        const statusEl = this.querySelector('#qa-status-value');
        const pauseBtn = this.querySelector('#qa-pause-btn');
        
        // Update status text
        if (state.isRunning) {
            if (state.isPaused) {
                statusEl.textContent = 'Paused';
                statusEl.className = 'qa-status-value paused';
                pauseBtn.innerHTML = '▶️ Resume';
            } else {
                statusEl.textContent = 'Running';
                statusEl.className = 'qa-status-value running';
                pauseBtn.innerHTML = '⏸️ Pause';
            }
        } else {
            statusEl.textContent = 'Idle';
            statusEl.className = 'qa-status-value stopped';
        }

        // Update progress
        this.querySelector('#qa-progress-current').textContent = `Step ${state.currentStep + 1}`;
        this.querySelector('#qa-progress-total').textContent = `of ${state.totalSteps}`;
        
        const progress = state.totalSteps > 0 
            ? ((state.currentStep) / state.totalSteps) * 100 
            : 0;
        this.querySelector('#qa-progress-fill').style.width = `${progress}%`;

        // Update current step display
        const currentStep = this.engine?.getCurrentStep();
        const stepDisplay = this.querySelector('#qa-current-step');
        if (currentStep && state.isRunning) {
            stepDisplay.style.display = 'block';
            this.querySelector('#qa-step-name').textContent = currentStep.name;
            this.querySelector('#qa-step-description').textContent = currentStep.description;
        } else {
            stepDisplay.style.display = 'none';
        }

        this.updateControlStates(state);
    }

    updateControlStates(state = null) {
        const hasScenario = !!this.selectedScenario;
        const engineState = state || this.engine?.getState() || {};
        const isRunning = engineState.isRunning;
        const isPaused = engineState.isPaused;
        const mode = engineState.mode || this.engine?.mode || 'automated';

        this.querySelector('#qa-run-btn').disabled = !hasScenario || isRunning;
        this.querySelector('#qa-next-btn').disabled = !isRunning || mode === 'automated';
        this.querySelector('#qa-pause-btn').disabled = !isRunning;
        this.querySelector('#qa-stop-btn').disabled = !isRunning;
        this.querySelector('#qa-teleport-btn').disabled = !hasScenario || isRunning;
    }

    onStepComplete(result, index, total) {
        const resultsEl = this.querySelector('#qa-results');
        const item = document.createElement('div');
        item.className = 'qa-result-item';
        item.innerHTML = `
            <span class="qa-result-icon ${result.passed ? 'pass' : 'fail'}">
                ${result.passed ? '✓' : '✗'}
            </span>
            <span class="qa-result-name">${result.name}</span>
            <span class="qa-result-duration">${result.duration.toFixed(0)}ms</span>
        `;
        resultsEl.appendChild(item);
        resultsEl.scrollTop = resultsEl.scrollHeight;
    }

    onScenarioComplete(summary) {
        const summaryEl = this.querySelector('#qa-summary');
        summaryEl.style.display = 'block';
        summaryEl.className = `qa-summary ${summary.allPassed ? 'success' : 'failure'}`;
        summaryEl.innerHTML = `
            <div class="qa-summary-title">
                ${summary.allPassed ? '✅ All Tests Passed!' : '❌ Some Tests Failed'}
            </div>
            <div class="qa-summary-stats">
                ${summary.passed}/${summary.total} passed
            </div>
        `;
    }

    onError(error, step) {
        console.error('[QA Control Panel] Error at step', step, ':', error);
    }

    clearResults() {
        this.querySelector('#qa-results').innerHTML = '';
        this.querySelector('#qa-summary').style.display = 'none';
    }

    getModeLabel(mode) {
        const labels = {
            automated: 'Automated (Fast)',
            interactive: 'Interactive (Slow-Mo)',
            teleport: 'Teleport'
        };
        return labels[mode] || mode;
    }
}

customElements.define('qa-control-panel', QAControlPanel);
