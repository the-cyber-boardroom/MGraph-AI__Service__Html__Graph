/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Top Navigation Component
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

class TopNav extends HTMLElement {
    constructor() {
        super();
        this.render();
    }

    render() {
        this.innerHTML = `
            <style>
                .top-nav {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: var(--spacing-sm) var(--spacing-md);
                    background: var(--gradient-bg);
                    color: white;
                    box-shadow: var(--shadow-md);
                }
                .top-nav-brand {
                    display: flex;
                    align-items: center;
                    gap: var(--spacing-sm);
                    font-size: 1.2em;
                    font-weight: 600;
                    text-decoration: none;
                    color: white;
                }
                .top-nav-brand:hover {
                    opacity: 0.9;
                }
                .top-nav-brand-icon {
                    font-size: 1.3em;
                }
                .top-nav-links {
                    display: flex;
                    align-items: center;
                    gap: var(--spacing-md);
                }
                .top-nav-link {
                    color: rgba(255,255,255,0.8);
                    text-decoration: none;
                    font-size: 0.95em;
                    padding: var(--spacing-xs) var(--spacing-sm);
                    border-radius: var(--radius-sm);
                    transition: all 0.2s ease;
                }
                .top-nav-link:hover {
                    color: white;
                    background: rgba(255,255,255,0.1);
                }
                .top-nav-link.active {
                    color: white;
                    background: rgba(255,255,255,0.2);
                }
            </style>
            <nav class="top-nav">
                <a href="./index.html" class="top-nav-brand">
                    <span class="top-nav-brand-icon">🔗</span>
                    <span>HTML Graph</span>
                </a>
                <div class="top-nav-links">
                    <a href="./index.html" class="top-nav-link">Dashboard</a>
                    <a href="./playground.html" class="top-nav-link active">Playground</a>
                    <a href="/docs" class="top-nav-link" target="_blank">API Docs</a>
                </div>
            </nav>
        `;
    }
}

customElements.define('top-nav', TopNav);
