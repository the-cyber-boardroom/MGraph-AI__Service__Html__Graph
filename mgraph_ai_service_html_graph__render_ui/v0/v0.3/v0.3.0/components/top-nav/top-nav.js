/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Top Navigation Component
   v0.3.0 - From v0.2.0 (unchanged)
   ═══════════════════════════════════════════════════════════════════════════════ */

class TopNav extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <nav class="top-nav">
                <div class="nav-brand">
                    <span class="nav-logo">🔗</span>
                    <span class="nav-title">HTML Graph Playground</span>
                    <span class="nav-version">v0.3.0</span>
                </div>
                <div class="nav-links">
                    <a href="./index.html" class="nav-link">Dashboard</a>
                    <a href="/docs" class="nav-link" target="_blank">API Docs</a>
                </div>
            </nav>
        `;
    }
}

customElements.define('top-nav', TopNav);
