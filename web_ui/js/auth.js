// Foundry Web UI — Kimlik Dogrulama Istemcisi
//
// Tum API cagrilari apiFetch() uzerinden gecer; token'i ekler ve 401/403
// durumlarini tek yerden yonetir. Boylece bir endpoint'e header eklemeyi
// unutmak mumkun olmaz.

import { API_BASE } from './config.js';

const TOKEN_KEY = 'foundry_token';

// Sunucu tarafi oturum omru 12 saat (SESSION_TTL_HOURS). Token burada
// yalnizca kolaylik icin saklanir; asil gecerlilik sunucuda tutulur, bu
// yuzden calinan bir token admin tarafindan aninda iptal edilebilir.
let currentUser = null;
let onUnauthorized = () => {};
let onPasswordChangeRequired = () => {};

export function configureAuth(handlers) {
    onUnauthorized = handlers.onUnauthorized || onUnauthorized;
    onPasswordChangeRequired = handlers.onPasswordChangeRequired || onPasswordChangeRequired;
}

export function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

export function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    currentUser = null;
}

export function getUser() {
    return currentUser;
}

export function isAdmin() {
    return currentUser?.role === 'admin';
}

export class AuthError extends Error {}

/**
 * Yetkili API cagrisi. Token'i ekler, 401'de oturumu dusurur.
 */
export async function apiFetch(path, options = {}) {
    const headers = { ...(options.headers || {}) };
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

    if (response.status === 401) {
        clearSession();
        onUnauthorized();
        throw new AuthError('Oturum sona erdi');
    }

    if (response.status === 403) {
        // Zorunlu parola degisimi mi, yoksa gercek yetki eksikligi mi?
        const body = await response.clone().json().catch(() => ({}));
        const code = body?.detail?.code;
        if (code === 'password_change_required') {
            onPasswordChangeRequired();
            throw new AuthError('Parola degisimi gerekli');
        }
    }

    return response;
}

export async function login(username, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
        // Sunucu kullanici adi/parola ayrimi yapmaz; mesaji oldugu gibi goster.
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || 'Giris basarisiz');
    }

    const data = await response.json();
    setToken(data.token);
    currentUser = data.user;
    return data.user;
}

export async function logout() {
    try {
        await apiFetch('/auth/logout', { method: 'POST' });
    } catch {
        // Sunucuya ulasilamasa bile yerel oturumu temizle
    }
    clearSession();
}

/** Sayfa acilisinda mevcut token gecerli mi? */
export async function restoreSession() {
    if (!getToken()) return null;
    try {
        const response = await apiFetch('/auth/me');
        if (!response.ok) return null;
        currentUser = await response.json();
        return currentUser;
    } catch {
        return null;
    }
}

export async function changePassword(oldPassword, newPassword) {
    const response = await fetch(`${API_BASE}/auth/change-password`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });

    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail || 'Parola degistirilemedi');

    // Sunucu parola degisiminde TUM oturumlari duserur; token artik gecersiz.
    clearSession();
    return body;
}

// ------------------------------------------------------------- yonetim

export async function listUsers() {
    const response = await apiFetch('/auth/users');
    if (!response.ok) throw new Error('Kullanicilar alinamadi');
    return response.json();
}

export async function createUser(username, password, role) {
    const response = await apiFetch('/auth/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, role }),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail || 'Kullanici olusturulamadi');
    return body;
}

export async function resetUserPassword(userId, newPassword) {
    const response = await apiFetch(`/auth/users/${userId}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_password: newPassword }),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail || 'Parola sifirlanamadi');
    return body;
}

export async function deactivateUser(userId) {
    const response = await apiFetch(`/auth/users/${userId}/deactivate`, { method: 'POST' });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail || 'Hesap kapatilamadi');
    return body;
}
