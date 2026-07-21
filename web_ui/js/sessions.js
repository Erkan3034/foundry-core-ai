// Foundry Web UI — Chat Sessions Manager

import { ICONS, showToast, setSidebarOpen } from './ui.js';
import { escapeHtml, renderMarkdown } from './markdown.js';
import { t } from './i18n.js';

let chatSessions = [];
let currentSessionId = null;

// Sohbet icerigini ekrana cizen fonksiyonlar app.js'te yasiyor.
// Bunlar bir kez kaydedilir; renderHistoryList icindeki tiklama isleyicisi
// switchChatSession'i parametresiz cagirdigi icin onceden ANLIK olarak
// undefined geciliyordu ve gecmis sohbetler hic cizilmiyordu.
let renderers = {};

export function configureSessionRenderers(fns) {
    renderers = fns || {};
}

export function getCurrentSessionId() {
    return currentSessionId;
}

export function loadChatSessions() {
    try {
        const saved = localStorage.getItem('foundry-chat-sessions');
        chatSessions = saved ? JSON.parse(saved) : [];
    } catch (e) {
        chatSessions = [];
    }
    if (chatSessions.length === 0) {
        createNewChatSession(false);
    } else {
        currentSessionId = chatSessions[0].id;
        renderHistoryList();
    }
}

export function saveChatSessions() {
    try {
        localStorage.setItem('foundry-chat-sessions', JSON.stringify(chatSessions));
    } catch (e) {}
}

export function createNewChatSession(render = true, onClearUI = null) {
    const newSession = {
        id: 'session_' + Date.now(),
        title: t('newChat'),
        createdAt: new Date().toISOString(),
        messages: []
    };
    chatSessions.unshift(newSession);
    currentSessionId = newSession.id;
    saveChatSessions();

    if (render) {
        renderHistoryList();
        if (onClearUI) onClearUI();
        showToast('info', t('toastNewChat'));
    }
}

export function renderHistoryList() {
    const list = document.getElementById('chatHistoryList');
    if (!list) return;

    if (chatSessions.length === 0) {
        list.innerHTML = `<div class="empty-state" style="padding:12px;">${t('noChatsYet')}</div>`;
        return;
    }

    list.innerHTML = chatSessions.map(session => `
        <div class="history-item ${session.id === currentSessionId ? 'active' : ''}" data-id="${session.id}">
            <span class="history-title">${escapeHtml(session.title)}</span>
            <button class="history-del-btn" type="button" title="Sohbeti sil" data-del="${session.id}">${ICONS.trash}</button>
        </div>
    `).join('');

    list.querySelectorAll('.history-item').forEach(el => {
        el.addEventListener('click', (e) => {
            if (e.target.closest('.history-del-btn')) return;
            switchChatSession(el.dataset.id);
        });
    });

    list.querySelectorAll('.history-del-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteChatSession(btn.dataset.del);
        });
    });
}

export function filterChatHistory(e) {
    const query = e.target.value.toLowerCase().trim();
    const items = document.querySelectorAll('#chatHistoryList .history-item');
    items.forEach(item => {
        const title = item.querySelector('.history-title').textContent.toLowerCase();
        item.style.display = title.includes(query) ? 'flex' : 'none';
    });
}

export function switchChatSession(id) {
    const { renderMeta, addAssistantHolder, addUserMessage, clearChatUI } = renderers;

    currentSessionId = id;
    saveChatSessions();
    renderHistoryList();
    if (clearChatUI) clearChatUI();

    const session = chatSessions.find(s => s.id === id);
    if (!session || session.messages.length === 0) return;

    const welcome = document.getElementById('welcomeScreen');
    if (welcome) welcome.remove();

    session.messages.forEach(msg => {
        if (msg.role === 'user') {
            if (addUserMessage) addUserMessage(msg.text);
        } else {
            if (addAssistantHolder) {
                const holder = addAssistantHolder();
                holder.content.innerHTML = renderMarkdown(msg.text);
                if (msg.meta && renderMeta) renderMeta(holder, msg.meta);
            }
        }
    });

    setSidebarOpen(false);
}

export function deleteChatSession(id) {
    chatSessions = chatSessions.filter(s => s.id !== id);
    saveChatSessions();

    if (currentSessionId === id) {
        if (chatSessions.length > 0) {
            currentSessionId = chatSessions[0].id;
            renderHistoryList();
        } else {
            createNewChatSession();
        }
    } else {
        renderHistoryList();
    }
}

export function recordMessageToCurrentSession(role, text, meta = null) {
    let session = chatSessions.find(s => s.id === currentSessionId);
    if (!session) {
        createNewChatSession(false);
        session = chatSessions.find(s => s.id === currentSessionId);
    }
    if (session) {
        if (session.messages.length === 0 && role === 'user') {
            session.title = text.length > 28 ? text.substring(0, 28) + '…' : text;
        }
        session.messages.push({ role, text, meta });
        saveChatSessions();
        renderHistoryList();
    }
}
