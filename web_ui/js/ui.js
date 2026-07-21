// Foundry Web UI — UI Utilities & Theme Manager

import { t } from './i18n.js';
import { escapeHtml } from './markdown.js';

export const ICONS = {
    bot: '<svg viewBox="0 0 56 56" width="16" height="16" fill="currentColor"><rect x="0" y="0" width="39" height="14" rx="2"/><rect x="42" y="0" width="14" height="39" rx="2"/><rect x="17" y="42" width="39" height="14" rx="2"/><rect x="0" y="17" width="14" height="39" rx="2"/></svg>',
    user: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    file: '<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>',
    fileEmpty: '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h6"/></svg>',
    alertCircle: '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v5M12 16h.01"/></svg>',
    trash: '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>',
    copy: '<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
    redo: '<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>',
    close: '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    info: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
    success: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>',
    error: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>'
};

export function initTheme() {
    const saved = localStorage.getItem('foundry-theme');
    document.documentElement.setAttribute('data-theme', saved || 'dark');
}

export function toggleTheme() {
    const next = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('foundry-theme', next);
}

export function setSidebarOpen(open) {
    document.getElementById('appContainer').classList.toggle('sidebar-open', open);
}

export function toggleDesktopSidebar() {
    document.getElementById('appContainer').classList.toggle('sidebar-collapsed');
}

export function showToast(type, message, duration = 4200) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${ICONS[type] || ICONS.info}</span>
        <span class="toast-message"></span>
        <button class="toast-close" aria-label="Kapat">${ICONS.close}</button>
    `;
    toast.querySelector('.toast-message').textContent = message;

    const dismiss = () => {
        toast.classList.add('leaving');
        setTimeout(() => toast.remove(), 160);
    };

    toast.querySelector('.toast-close').addEventListener('click', dismiss);
    container.appendChild(toast);
    setTimeout(dismiss, duration);
}

export function showPopover(e, docName, scorePercent) {
    const popover = document.getElementById('hoverPopover');
    if (!popover) return;

    popover.innerHTML = `
        <div class="popover-card">
            <div class="popover-card-header">
                <span>📄 ${escapeHtml(docName)}</span>
                <span class="popover-score-badge">%${scorePercent} ${t('matchScore')}</span>
            </div>
            <div>${t('popoverTitle')}</div>
        </div>
    `;

    const rect = e.target.getBoundingClientRect();
    popover.style.top = (rect.bottom + window.scrollY + 6) + 'px';
    popover.style.left = Math.min(rect.left + window.scrollX, window.innerWidth - 360) + 'px';
    popover.classList.add('visible');
    popover.setAttribute('aria-hidden', 'false');
}

export function hidePopover() {
    const popover = document.getElementById('hoverPopover');
    if (popover) {
        popover.classList.remove('visible');
        popover.setAttribute('aria-hidden', 'true');
    }
}
