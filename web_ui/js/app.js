// Foundry Web UI — Main Orchestrator

import { getLanguage, toggleLanguage, initLanguage, t } from './i18n.js';
import { apiFetch, isAdmin } from './auth.js';
import { initSessionGate } from './session-gate.js';
import { renderUsersPanel } from './users-panel.js';
import { renderMarkdown, escapeHtml } from './markdown.js';
import { ICONS, initTheme, toggleTheme, setSidebarOpen, toggleDesktopSidebar, showToast, showPopover, hidePopover } from './ui.js';
import { bindModalEvents, closeUploadModal } from './modal.js';
import { loadChatSessions, createNewChatSession, filterChatHistory, recordMessageToCurrentSession, getCurrentSessionId, configureSessionRenderers } from './sessions.js';

import { API_BASE } from './config.js';

let isProcessing = false;
let activePanel = null; // 'documents' | 'settings' | null

// ============== Init ==============

let appStarted = false;

// Oturum dogrulandiktan SONRA calisir. Giris yapmamis bir kullanici icin
// hicbir veri cagrisi yapilmaz (aksi halde her acilista 401 yagardi).
function startApp() {
    if (appStarted) return;
    appStarted = true;
    // Gecmis sohbetlerin ekrana cizilebilmesi icin gerekli
    configureSessionRenderers({ renderMeta, addAssistantHolder, addUserMessage, clearChatUI });
    loadChatSessions();
    bindModalEvents(refreshDocBadge);
    checkHealth();
    refreshDocBadge();
    setInterval(checkHealth, 30000);
}

async function initApp() {
    // Tema/dil ve olay baglama oturumdan bagimsiz: giris ekrani da
    // dogru temada gorunmeli.
    initTheme();
    initLanguage();
    bindEvents();

    const authenticated = await initSessionGate({ onAuthenticated: startApp });
    if (authenticated) startApp();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

function bindEvents() {
    const input = document.getElementById('chatInput');
    input.addEventListener('keydown', handleKeydown);
    input.addEventListener('input', function () {
        autoResize(this);
        document.getElementById('sendBtn').disabled = !this.value.trim() || isProcessing;
    });
    document.getElementById('sendBtn').addEventListener('click', sendMessage);

    bindSuggestions(document);

    document.getElementById('btnNewChat').addEventListener('click', () => createNewChatSession(true, clearChatUI));
    document.getElementById('navDocuments').addEventListener('click', () => openPanel('documents'));
    document.getElementById('navSettings').addEventListener('click', () => openPanel('settings'));
    const navUsers = document.getElementById('navUsers');
    if (navUsers) navUsers.addEventListener('click', () => openPanel('users'));
    document.getElementById('btnToggleDocs').addEventListener('click', () => togglePanel('documents'));
    document.getElementById('panelCloseBtn').addEventListener('click', closePanel);

    document.getElementById('sidebarOpenBtn').addEventListener('click', () => setSidebarOpen(true));
    document.getElementById('sidebarCloseBtn').addEventListener('click', () => setSidebarOpen(false));
    document.getElementById('sidebarBackdrop').addEventListener('click', () => setSidebarOpen(false));

    const desktopToggle = document.getElementById('btnToggleSidebar');
    if (desktopToggle) desktopToggle.addEventListener('click', toggleDesktopSidebar);

    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    const langBtn = document.getElementById('langToggle');
    if (langBtn) {
        langBtn.addEventListener('click', () => {
            toggleLanguage();
            showToast('info', t('toastLangChanged'));
            checkHealth();
            const welcome = document.getElementById('welcomeScreen');
            if (welcome) clearChatUI();

            // updateDOMTranslations yalnizca data-i18n tasiyan STATIK ogeleri
            // ceviriyor. Panel icerikleri ve sohbet listesi JS ile uretiliyor;
            // t() cagrisi cizim aninda calistigi icin acik bir panel eski
            // dilde kalirdi. Bu yuzden acik olan ne varsa yeniden cizilir.
            if (activePanel) openPanel(activePanel);
            loadChatSessions();
        });
    }

    document.getElementById('historySearch').addEventListener('input', filterChatHistory);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (activePanel) closePanel();
            closeUploadModal();
            setSidebarOpen(false);
        }
    });
}

function bindSuggestions(root) {
    root.querySelectorAll('.suggestion').forEach(btn => {
        btn.addEventListener('click', () => sendQuick(btn.dataset.quick));
    });
}

// ============== Health & Badges ==============

async function checkHealth() {
    const dot = document.getElementById('statusDot');
    const label = document.getElementById('statusLabel');
    try {
        const response = await apiFetch(`/health`);
        if (!response.ok) throw new Error('unhealthy');
        const data = await response.json();
        dot.className = 'status-dot online';
        label.textContent = data.models_loaded ? t('statusOnline') : t('statusLoadingModel');
        // /health artik istatistik dondurmuyor (giris yapmamis birine sizmasin)
    } catch (e) {
        dot.className = 'status-dot offline';
        label.textContent = t('statusOffline');
    }
}

function setDocBadge(count) {
    const badge = document.getElementById('docCountBadge');
    if (!badge) return;
    badge.textContent = count;
    badge.hidden = !count;
}

export async function refreshDocBadge() {
    // /stats admin'e kapali; belge sayisini herkesin erisebildigi
    // /documents uzerinden turet.
    try {
        const r = await apiFetch(`/documents`);
        if (!r.ok) return;
        const data = await r.json();
        setDocBadge((data.documents || []).length);
    } catch (e) {}
}

function clearChatUI() {
    const container = document.getElementById('chatMessages');
    container.innerHTML = `
        <div class="hero" id="welcomeScreen">
            <div class="hero-orb" aria-hidden="true">
                <svg viewBox="0 0 56 56" width="30" height="30" fill="currentColor"><rect x="0" y="0" width="39" height="14" rx="2"/><rect x="42" y="0" width="14" height="39" rx="2"/><rect x="17" y="42" width="39" height="14" rx="2"/><rect x="0" y="17" width="14" height="39" rx="2"/></svg>
            </div>
            <h1 class="hero-title"><span class="grad-text">Foundry</span> ${t('pageTitle')}</h1>
            <p class="hero-sub">${t('welcomeSub')}</p>
            <div class="suggestions" id="suggestions">
                <button type="button" class="suggestion" data-quick="${t('suggestion1Query')}">
                    <span class="suggestion-icon"><svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.75"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg></span>
                    <span class="suggestion-body"><span class="suggestion-title">${t('suggestion1Title')}</span><span class="suggestion-desc">${t('suggestion1Desc')}</span></span>
                </button>
                <button type="button" class="suggestion" data-quick="${t('suggestion2Query')}">
                    <span class="suggestion-icon"><svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.75"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></span>
                    <span class="suggestion-body"><span class="suggestion-title">${t('suggestion2Title')}</span><span class="suggestion-desc">${t('suggestion2Desc')}</span></span>
                </button>
            </div>
        </div>
    `;
    bindSuggestions(container);
}

// ============== Chat Handling ==============

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 168) + 'px';
}

function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function sendQuick(text) {
    const input = document.getElementById('chatInput');
    input.value = text;
    sendMessage();
}

function scrollToBottom() {
    const scroller = document.getElementById('chatScroll');
    scroller.scrollTop = scroller.scrollHeight;
}

function autoScroll() {
    const s = document.getElementById('chatScroll');
    if (s.scrollHeight - s.scrollTop - s.clientHeight < 160) {
        s.scrollTop = s.scrollHeight;
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const query = input.value.trim();
    if (!query || isProcessing) return;

    const welcome = document.getElementById('welcomeScreen');
    if (welcome) welcome.remove();

    addUserMessage(query);
    recordMessageToCurrentSession('user', query);

    input.value = '';
    input.style.height = 'auto';
    document.getElementById('sendBtn').disabled = true;
    setProcessing(true);

    const holder = addAssistantHolder();

    try {
        await streamAnswer(query, holder);
    } catch (error) {
        try {
            await fallbackAnswer(query, holder);
        } catch (err2) {
            holder.content.innerHTML = `<p>${t('errorApiDown', { error: escapeHtml(err2.message) })}</p>`;
            holder.root.classList.add('error');
            showToast('error', t('queryFailed', { error: err2.message }));
        }
    } finally {
        holder.content.classList.remove('streaming');
        setProcessing(false);
        scrollToBottom();
    }
}

async function streamAnswer(query, holder) {
    const response = await apiFetch(`/query/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, stream: true })
    });
    if (!response.ok || !response.body) {
        const errBody = await response.json().catch(() => ({}));
        throw new Error(errBody.detail || `HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let meta = null;
    let answer = '';
    let started = false;

    let rafPending = false;
    const flush = () => {
        rafPending = false;
        holder.content.innerHTML = renderMarkdown(answer);
        autoScroll();
    };
    const scheduleFlush = () => {
        if (rafPending) return;
        rafPending = true;
        requestAnimationFrame(flush);
    };

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const frames = buffer.split('\n\n');
        buffer = frames.pop();

        for (const frame of frames) {
            const line = frame.trim();
            if (!line.startsWith('data:')) continue;
            const payload = line.slice(5).trim();
            if (!payload || payload === '[DONE]') continue;

            let event;
            try { event = JSON.parse(payload); } catch { continue; }

            if (event.type === 'error') {
                throw new Error(event.message || t('serverError'));
            } else if (event.type === 'metadata') {
                meta = event;
            } else if (event.type === 'delta' && event.content) {
                if (!started) {
                    started = true;
                    holder.content.textContent = '';
                    holder.content.classList.add('streaming');
                }
                answer += event.content;
                scheduleFlush();
            }
        }
    }

    holder.content.classList.remove('streaming');
    if (!started) {
        holder.content.innerHTML = `<p>${t('noResponse')}</p>`;
    } else {
        holder.content.innerHTML = renderMarkdown(answer);
        addMessageActions(holder, query, answer);
        bindInlineSourcePopovers(holder.content);
    }
    if (meta) {
        renderMeta(holder, meta);
        recordMessageToCurrentSession('assistant', answer, meta);
    } else {
        recordMessageToCurrentSession('assistant', answer);
    }
    autoScroll();
}

async function fallbackAnswer(query, holder) {
    const response = await apiFetch(`/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, stream: false })
    });
    if (!response.ok) {
        const errBody = await response.json().catch(() => ({}));
        throw new Error(errBody.detail || `HTTP ${response.status}`);
    }
    const data = await response.json();
    holder.content.innerHTML = renderMarkdown(data.answer);
    addMessageActions(holder, query, data.answer);
    bindInlineSourcePopovers(holder.content);
    renderMeta(holder, data);
    recordMessageToCurrentSession('assistant', data.answer, data);
}

function addUserMessage(text) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'message user';
    div.innerHTML = `
        <div class="message-avatar">${ICONS.user}</div>
        <div class="message-body">
            <div class="message-content"></div>
        </div>
    `;
    div.querySelector('.message-content').textContent = text;
    container.appendChild(div);
    scrollToBottom();
}

function addAssistantHolder() {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.innerHTML = `
        <div class="message-avatar">${ICONS.bot}</div>
        <div class="message-body">
            <div class="message-content">
                <span class="thinking">
                    ${t('statusThinking')}
                    <span class="thinking-dots"><span></span><span></span><span></span></span>
                </span>
            </div>
        </div>
    `;
    container.appendChild(div);
    scrollToBottom();
    return {
        root: div,
        body: div.querySelector('.message-body'),
        content: div.querySelector('.message-content')
    };
}

function addMessageActions(holder, query, answerText) {
    const actions = document.createElement('div');
    actions.className = 'msg-actions';
    actions.innerHTML = `
        <button class="msg-action-btn copy-btn" type="button">${ICONS.copy} ${t('btnCopy')}</button>
        <button class="msg-action-btn redo-btn" type="button">${ICONS.redo} ${t('btnRedo')}</button>
    `;

    actions.querySelector('.copy-btn').addEventListener('click', () => {
        navigator.clipboard.writeText(answerText);
        showToast('info', t('toastCopied'));
    });

    actions.querySelector('.redo-btn').addEventListener('click', () => {
        const input = document.getElementById('chatInput');
        input.value = query;
        sendMessage();
    });

    holder.body.appendChild(actions);
}

// ============== Collapsible Sources Accordion & Popovers ==============

function renderMeta(holder, meta) {
    const sources = meta.sources || [];
    const confidence = meta.confidence ?? 0;
    if (!sources.length) return;

    const confPercent = (confidence * 100).toFixed(0);

    const accordion = document.createElement('div');
    accordion.className = 'sources-accordion';
    accordion.innerHTML = `
        <button class="sources-trigger" type="button">
            <span>▼ ${t('sourcesHeader')} (${sources.length})</span>
            <span class="chevron">▼</span>
        </button>
        <div class="sources-content">
            ${sources.map(s => `
                <div class="source-accordion-item" data-source="${escapeHtml(s)}">
                    <span class="source-accordion-title">📄 ${escapeHtml(s)}</span>
                    <span class="source-accordion-score">%${confPercent} ${t('matchScore')}</span>
                </div>
            `).join('')}
        </div>
    `;

    const trigger = accordion.querySelector('.sources-trigger');
    trigger.addEventListener('click', () => {
        accordion.classList.toggle('open');
    });

    // Hover popovers on accordion items
    accordion.querySelectorAll('.source-accordion-item').forEach(item => {
        const sourceName = item.dataset.source;
        item.addEventListener('mouseenter', (e) => showPopover(e, sourceName, confPercent));
        item.addEventListener('mouseleave', hidePopover);
    });

    holder.body.appendChild(accordion);
}

function bindInlineSourcePopovers(rootEl) {
    rootEl.querySelectorAll('.source-inline-badge').forEach(badge => {
        const docName = badge.dataset.doc;
        badge.addEventListener('mouseenter', (e) => showPopover(e, docName, '85'));
        badge.addEventListener('mouseleave', hidePopover);
    });
}

function setProcessing(processing) {
    isProcessing = processing;
    const input = document.getElementById('chatInput');
    document.getElementById('sendBtn').disabled = processing || !input.value.trim();
    document.getElementById('statusText').textContent = processing ? t('statusGenerating') : t('statusReady');
}

// ============== Side Panel (Bilgi Tabanı & Ayarlar) ==============

function openPanel(kind) {
    activePanel = kind;
    const panel = document.getElementById('sidePanel');
    panel.classList.add('open');
    panel.setAttribute('aria-hidden', 'false');

    document.getElementById('navDocuments').classList.toggle('active', kind === 'documents');
    document.getElementById('navSettings').classList.toggle('active', kind === 'settings');
    const navUsers = document.getElementById('navUsers');
    if (navUsers) navUsers.classList.toggle('active', kind === 'users');
    setSidebarOpen(false);

    if (kind === 'documents') {
        document.getElementById('panelTitle').textContent = t('navDocs');
        loadDocuments();
    } else if (kind === 'users') {
        document.getElementById('panelTitle').textContent = t('navUsers');
        renderUsersPanel();
    } else {
        document.getElementById('panelTitle').textContent = t('navSettings');
        renderSettingsPanel();
    }
}

function togglePanel(kind) {
    activePanel === kind ? closePanel() : openPanel(kind);
}

function closePanel() {
    activePanel = null;
    const panel = document.getElementById('sidePanel');
    panel.classList.remove('open');
    panel.setAttribute('aria-hidden', 'true');
    document.getElementById('navDocuments').classList.remove('active');
    document.getElementById('navSettings').classList.remove('active');
    const nu = document.getElementById('navUsers');
    if (nu) nu.classList.remove('active');
}

async function loadDocuments() {
    const list = document.getElementById('panelBody');
    list.innerHTML = `<div class="empty-state">${t('statusThinking')}</div>`;

    try {
        const response = await apiFetch(`/documents`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        if (!data.documents || data.documents.length === 0) {
            list.innerHTML = `<div class="empty-state">${ICONS.fileEmpty}<span>${t('noDocsYet')}</span></div>`;
            setDocBadge(0);
            return;
        }

        setDocBadge(data.documents.length);

        const wrap = document.createElement('div');
        wrap.className = 'document-list';
        wrap.innerHTML = data.documents.map(doc => `
            <div class="document-item" data-doc-id="${doc.id}">
                <span class="doc-icon">${ICONS.file}</span>
                <div class="doc-info">
                    <div class="doc-name" title="${escapeHtml(doc.source)}">${escapeHtml(doc.source)}</div>
                    <div class="doc-meta">${doc.chunk_count || 0} ${t('unitChunks')}</div>
                </div>
                ${isAdmin() ? `<button class="doc-delete-btn" type="button" aria-label="Belgeyi sil" title="Belgeyi sil">${ICONS.trash}</button>` : ''}
            </div>
        `).join('');

        list.innerHTML = '';
        list.appendChild(wrap);

        wrap.querySelectorAll('.doc-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = e.currentTarget.closest('.document-item');
                deleteDocument(item.dataset.docId, item);
            });
        });
    } catch (e) {
        list.innerHTML = `<div class="empty-state is-error">${ICONS.alertCircle}<span>${t('docsLoadFailed')}</span></div>`;
    }
}

async function deleteDocument(docId, itemEl) {
    if (!confirm(t('confirmDeleteDoc'))) return;

    try {
        const response = await apiFetch(`/documents/${docId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        itemEl.remove();
        showToast('success', t('toastDocDeleted'));
        refreshDocBadge();
        if (!document.querySelector('.document-item')) loadDocuments();
    } catch (e) {
        showToast('error', 'Belge silinemedi: ' + e.message);
    }
}

async function renderSettingsPanel() {
    const body = document.getElementById('panelBody');
    body.innerHTML = `
        <div class="settings-section">
            <div class="settings-section-title">${t('sectionConnection')}</div>
            <div class="settings-card">
                <div class="settings-row"><span class="label">API adresi</span><span class="value">${escapeHtml(API_BASE)}</span></div>
                <div class="settings-row"><span class="label">Durum</span><span class="value" id="stHealth">Kontrol ediliyor…</span></div>
                <div class="settings-row"><span class="label">Modeller</span><span class="value" id="stModel">—</span></div>
            </div>
        </div>
        <div class="settings-section">
            <div class="settings-section-title">${t('navDocs')}</div>
            <div class="settings-card">
                <div class="settings-row"><span class="label">Belgeler</span><span class="value" id="stDocs">—</span></div>
                <div class="settings-row"><span class="label">${t('labelChunks')}</span><span class="value" id="stChunks">—</span></div>
                <div class="settings-row"><span class="label">Embedding'li</span><span class="value" id="stEmbedded">—</span></div>
            </div>
        </div>
    `;
    loadSettingsData();
}

async function loadSettingsData() {
    try {
        const response = await apiFetch(`/health`);
        const data = await response.json();
        const healthEl = document.getElementById('stHealth');
        const modelEl = document.getElementById('stModel');
        if (healthEl) {
            healthEl.textContent = data.status === 'healthy' ? t('statusHealthy') : t('statusUnhealthy');
            healthEl.className = 'value ' + (data.status === 'healthy' ? 'ok' : 'bad');
        }
        if (modelEl) {
            modelEl.textContent = data.models_loaded ? t('modelLoaded') : t('modelNotLoaded');
            modelEl.className = 'value ' + (data.models_loaded ? 'ok' : 'bad');
        }
        if (data.stats) {
            ['stDocs', 'stChunks', 'stEmbedded'].forEach((id, i) => {
                const el = document.getElementById(id);
                const keys = ['documents', 'chunks', 'embedded_chunks'];
                if (el && data.stats[keys[i]] !== undefined) el.textContent = data.stats[keys[i]];
            });
        }
    } catch (e) {}
}
