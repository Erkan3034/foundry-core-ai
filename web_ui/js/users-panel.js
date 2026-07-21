// Foundry Web UI — Kullanici Yonetimi Paneli (yalnizca admin)
//
// Sunucu tarafi zaten require_admin ile korunuyor; buradaki gizleme sadece
// arayuz kolayligidir. Panel gorunmese de endpoint korumali kalir.

import { listUsers, createUser, resetUserPassword, deactivateUser, getUser } from './auth.js';
import { escapeHtml } from './markdown.js';
import { showToast } from './ui.js';
import { t } from './i18n.js';

/** Yonetici tarafindan verilecek gecici parola onerisi. */
function suggestPassword() {
    const bytes = new Uint8Array(9);
    crypto.getRandomValues(bytes);
    return btoa(String.fromCharCode(...bytes)).replace(/[+/=]/g, '').slice(0, 12);
}

function userRow(user, currentUserId) {
    const kendisi = user.id === currentUserId;
    const sonGiris = user.last_login_at
        ? new Date(user.last_login_at).toLocaleString(t('dateLocale'), { dateStyle: 'short', timeStyle: 'short' })
        : t('userNeverLoggedIn');

    return `
        <div class="user-row ${user.is_active ? '' : 'inactive'}" data-user-id="${user.id}">
            <div class="user-row-main">
                <div class="user-row-name">
                    ${escapeHtml(user.username)}
                    <span class="role-tag ${user.role === 'admin' ? 'admin' : ''}">
                        ${user.role === 'admin' ? t('roleManager') : t('roleUser')}
                    </span>
                    ${user.must_change_password ? `<span class="role-tag">${t('pendingPassword')}</span>` : ''}
                    ${user.is_active ? '' : `<span class="role-tag">${t('tagDisabled')}</span>`}
                </div>
                <div class="user-row-meta">${t('lastLogin')}: ${sonGiris}</div>
            </div>
            <button class="btn" data-action="reset" ${user.is_active ? '' : 'disabled'}>
                ${t('btnResetPassword')}
            </button>
            <button class="btn btn-danger" data-action="deactivate"
                ${kendisi || !user.is_active ? 'disabled' : ''}
                title="${kendisi ? t('cannotDisableSelf') : t('disableAccount')}">
                ${t('btnDisable')}
            </button>
        </div>
    `;
}

export async function renderUsersPanel() {
    const host = document.getElementById('panelBody');
    host.innerHTML = `<div class="empty-state">${t('loading')}</div>`;

    let users;
    try {
        users = await listUsers();
    } catch (err) {
        host.innerHTML = `<div class="empty-state">${t('usersLoadFailed', { error: escapeHtml(err.message) })}</div>`;
        return;
    }

    const me = getUser();
    host.innerHTML = `
        <form class="user-create" id="userCreateForm" style="margin-bottom:18px">
            <label class="auth-label" for="newUsername">${t('newUserLabel')}</label>
            <input class="auth-input" id="newUsername" placeholder="${t('usernamePlaceholder')}" required
                autocomplete="off" style="margin-bottom:10px">

            <label class="auth-label" for="newUserPassword">${t('tempPasswordLabel')}</label>
            <input class="auth-input" id="newUserPassword" required minlength="8"
                autocomplete="off" style="margin-bottom:10px" value="${suggestPassword()}">

            <label class="auth-label" for="newUserRole">${t('roleLabel')}</label>
            <select class="auth-input" id="newUserRole" style="margin-bottom:12px">
                <option value="user">${t('roleUserOption')}</option>
                <option value="admin">${t('roleAdminOption')}</option>
            </select>

            <p class="auth-error" id="userCreateError" hidden></p>
            <button class="auth-submit" type="submit">${t('btnAddUser')}</button>
            <p class="auth-hint" style="text-align:left">
                ${t('userCreateHint')}
            </p>
        </form>

        <div class="nav-title" style="padding-left:0">${t('existingUsers', { count: users.length })}</div>
        <div id="userList">${users.map(u => userRow(u, me?.id)).join('')}</div>
    `;

    bindCreateForm();
    bindRowActions();
}

function bindCreateForm() {
    const form = document.getElementById('userCreateForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const error = document.getElementById('userCreateError');
        error.hidden = true;

        const username = document.getElementById('newUsername').value.trim();
        const password = document.getElementById('newUserPassword').value;
        const role = document.getElementById('newUserRole').value;

        try {
            await createUser(username, password, role);
            showToast('success', t('userAdded', { username, password }));
            renderUsersPanel();
        } catch (err) {
            error.textContent = err.message;
            error.hidden = false;
        }
    });
}

function bindRowActions() {
    document.getElementById('userList').addEventListener('click', async (e) => {
        const button = e.target.closest('button[data-action]');
        if (!button) return;

        const row = button.closest('.user-row');
        const userId = Number(row.dataset.userId);
        const username = row.querySelector('.user-row-name').textContent.trim().split('\n')[0];

        if (button.dataset.action === 'reset') {
            const yeni = suggestPassword();
            if (!confirm(t('confirmResetPassword', { username, password: yeni }))) return;
            try {
                await resetUserPassword(userId, yeni);
                showToast('success', t('passwordResetDone', { password: yeni }));
                renderUsersPanel();
            } catch (err) {
                showToast('error', err.message);
            }
        }

        if (button.dataset.action === 'deactivate') {
            if (!confirm(t('confirmDisableUser', { username }))) return;
            try {
                await deactivateUser(userId);
                showToast('success', t('userDisabled', { username }));
                renderUsersPanel();
            } catch (err) {
                showToast('error', err.message);
            }
        }
    });
}
