// Foundry Web UI — Oturum Kapisi ve Yetki Bazli Gorunurluk
//
// Uygulama, gecerli bir oturum dogrulanana kadar gizli kalir. Rol bazli
// gizleme SADECE arayuz kolayligidir; asil yetki kontrolu sunucudadir
// (her endpoint Depends(require_user/require_admin) ile korunur). Butonu
// gizlemek guvenlik saglamaz, gizlememek de acik yaratmaz.

import {
    login, logout, restoreSession, changePassword,
    configureAuth, getUser, isAdmin,
} from './auth.js';

let onAuthenticated = () => {};

const el = (id) => document.getElementById(id);

function show(node) { if (node) node.hidden = false; }
function hide(node) { if (node) node.hidden = true; }

function showLogin({ message } = {}) {
    show(el('authGate'));
    hide(el('appContainer'));
    show(el('loginForm'));
    hide(el('passwordForm'));

    const error = el('loginError');
    if (message) {
        error.textContent = message;
        show(error);
    } else {
        hide(error);
    }
    el('loginPassword').value = '';
    el('loginUsername').focus();
}

function showPasswordChange() {
    show(el('authGate'));
    hide(el('appContainer'));
    hide(el('loginForm'));
    show(el('passwordForm'));
    hide(el('passwordError'));
    el('oldPassword').focus();
}

function showApp() {
    hide(el('authGate'));
    show(el('appContainer'));
    applyRoleVisibility();
    renderUserChip();
}

/** Rolune gore admin kontrollerini goster/gizle. */
function applyRoleVisibility() {
    const admin = isAdmin();
    document.querySelectorAll('.admin-only').forEach(node => {
        node.hidden = !admin;
    });
}

function renderUserChip() {
    const user = getUser();
    const host = el('userChip');
    if (!host || !user) return;

    host.innerHTML = `
        <span class="user-chip-avatar">${user.username.slice(0, 2).toUpperCase()}</span>
        <span class="user-chip-text">
            <span class="user-chip-name">${user.username}</span>
            <span class="user-chip-role">${user.role === 'admin' ? 'Yönetici' : 'Kullanıcı'}</span>
        </span>
    `;
}

// --------------------------------------------------------------- olaylar

function bindLoginForm() {
    el('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const button = el('loginSubmit');
        const error = el('loginError');
        button.disabled = true;
        button.textContent = 'Giriş yapılıyor…';
        hide(error);

        try {
            const user = await login(el('loginUsername').value, el('loginPassword').value);
            if (user.must_change_password) {
                showPasswordChange();
            } else {
                showApp();
                onAuthenticated();
            }
        } catch (err) {
            error.textContent = err.message || 'Giriş başarısız';
            show(error);
            el('loginPassword').value = '';
            el('loginPassword').focus();
        } finally {
            button.disabled = false;
            button.textContent = 'Giriş yap';
        }
    });
}

function bindPasswordForm() {
    el('passwordForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const button = el('passwordSubmit');
        const error = el('passwordError');
        const yeni = el('newPassword').value;
        const tekrar = el('newPassword2').value;

        if (yeni !== tekrar) {
            error.textContent = 'Yeni parolalar eşleşmiyor';
            show(error);
            return;
        }

        button.disabled = true;
        button.textContent = 'Değiştiriliyor…';
        hide(error);

        try {
            await changePassword(el('oldPassword').value, yeni);
            // Sunucu parola degisiminde tum oturumlari duserur; yeniden giris gerekir.
            el('passwordForm').reset();
            showLogin({ message: 'Parolanız güncellendi. Yeni parolanızla giriş yapın.' });
        } catch (err) {
            error.textContent = err.message || 'Parola değiştirilemedi';
            show(error);
        } finally {
            button.disabled = false;
            button.textContent = 'Parolayı değiştir';
        }
    });
}

function bindLogout() {
    const button = el('btnLogout');
    if (!button) return;
    button.addEventListener('click', async () => {
        await logout();
        showLogin();
    });
}

/**
 * Uygulamayi oturum arkasina al. Gecerli oturum varsa uygulamayi acar,
 * yoksa giris ekranini gosterir.
 */
export async function initSessionGate(callbacks = {}) {
    onAuthenticated = callbacks.onAuthenticated || onAuthenticated;

    configureAuth({
        // Token suresi dolarsa veya admin hesabi kapatirsa: aninda girise dus
        onUnauthorized: () => showLogin({ message: 'Oturumunuz sona erdi, tekrar giriş yapın.' }),
        onPasswordChangeRequired: showPasswordChange,
    });

    bindLoginForm();
    bindPasswordForm();
    bindLogout();

    const user = await restoreSession();
    if (!user) {
        showLogin();
        return false;
    }
    if (user.must_change_password) {
        showPasswordChange();
        return false;
    }

    showApp();
    return true;
}
