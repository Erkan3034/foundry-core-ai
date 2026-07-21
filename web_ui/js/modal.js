// Foundry Web UI — Modal & File Upload Controller

import { API_BASE } from './config.js';
import { apiFetch } from './auth.js';
import { showToast } from './ui.js';
import { t } from './i18n.js';
import { escapeHtml } from './markdown.js';

export function bindModalEvents(refreshDocBadge) {
    const modal = document.getElementById('uploadModal');
    const openBtn1 = document.getElementById('btnOpenUploadModal');
    const openBtn2 = document.getElementById('btnUploadModalTop');
    const closeBtn = document.getElementById('modalCloseBtn');
    const dropzone = document.getElementById('modalDropzone');
    const fileInput = document.getElementById('modalFileInput');

    if (openBtn1) openBtn1.addEventListener('click', openUploadModal);
    if (openBtn2) openBtn2.addEventListener('click', openUploadModal);
    if (closeBtn) closeBtn.addEventListener('click', closeUploadModal);

    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeUploadModal();
        });
    }

    if (dropzone && fileInput) {
        dropzone.addEventListener('click', () => fileInput.click());

        ['dragenter', 'dragover'].forEach(name => {
            dropzone.addEventListener(name, (e) => {
                e.preventDefault();
                dropzone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(name => {
            dropzone.addEventListener(name, (e) => {
                e.preventDefault();
                dropzone.classList.remove('drag-over');
            });
        });

        dropzone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) uploadModalFile(files[0], refreshDocBadge);
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) uploadModalFile(fileInput.files[0], refreshDocBadge);
        });
    }

    const toggleIndexed = document.getElementById('toggleIndexedList');
    if (toggleIndexed) {
        toggleIndexed.addEventListener('click', () => {
            const list = document.getElementById('modalIndexedList');
            if (list) list.style.display = list.style.display === 'none' ? 'flex' : 'none';
        });
    }
}

export function openUploadModal() {
    const modal = document.getElementById('uploadModal');
    if (!modal) return;
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    loadModalIndexedDocuments();
}

export function closeUploadModal() {
    const modal = document.getElementById('uploadModal');
    if (!modal) return;
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
}

export async function loadModalIndexedDocuments() {
    const list = document.getElementById('modalIndexedList');
    if (!list) return;
    list.innerHTML = `<div class="empty-state">${t('statusThinking')}</div>`;

    try {
        const response = await apiFetch(`/documents`);
        const data = await response.json();

        if (!data.documents || data.documents.length === 0) {
            list.innerHTML = '<div class="empty-state">Henüz indekslenmiş belge yok.</div>';
            return;
        }

        list.innerHTML = data.documents.map(doc => `
            <div class="indexed-doc-item">
                <span class="indexed-doc-name">📄 ${escapeHtml(doc.source)}</span>
                <span class="chunk-badge-green">${doc.chunk_count || 0} chunks</span>
            </div>
        `).join('');
    } catch (e) {
        list.innerHTML = '<div class="empty-state">Belgeler yüklenemedi.</div>';
    }
}

export async function uploadModalFile(file, refreshDocBadge) {
    if (!file) return;

    const contentEl = document.getElementById('dropzoneContent');
    const loaderEl = document.getElementById('dropzoneLoader');
    const statusTextEl = document.getElementById('loaderStatusText');

    if (contentEl) contentEl.style.display = 'none';
    if (loaderEl) loaderEl.style.display = 'flex';
    if (statusTextEl) statusTextEl.textContent = `${file.name} ${t('dropzoneUploading')}`;

    const formData = new FormData();
    formData.append('file', file);

    showToast('info', `${file.name} ${t('dropzoneUploading')}`);
    try {
        const response = await apiFetch(`/ingest/file`, { method: 'POST', body: formData });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`);

        const chunkCount = data.chunks ? data.chunks.length : 0;
        showToast('success', `${file.name} ${t('toastDocUploaded')} (${chunkCount} parça)!`);
        if (refreshDocBadge) refreshDocBadge();
        loadModalIndexedDocuments();
    } catch (e) {
        showToast('error', `${t('toastUploadError')}: ${e.message}`);
    } finally {
        if (contentEl) contentEl.style.display = 'block';
        if (loaderEl) loaderEl.style.display = 'none';
    }
}
