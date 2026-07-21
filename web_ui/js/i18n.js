// Foundry Web UI — i18n (Internationalization Manager)

export const TRANSLATIONS = {
    tr: {
        brandName: "Foundry Core AI",
        brandTag: "Yerel AI Asistanı",
        pageTitle: "Sohbet",
        topbarSub: "Kurumsal Bilgi Tabanı",
        newChat: "Yeni Sohbet",
        historyTitle: "Sohbet Geçmişi",
        historySearchPlaceholder: "Sohbetlerde ara…",
        navWorkspace: "Çalışma Alanı",
        navManagement: "Yönetim",
        navDocs: "Bilgi Tabanı",
        navUploadPopup: "Belge Ekle",
        navUsers: "Kullanıcılar",
        navSettings: "Sistem Durumu",
        btnUpload: "Yükle",
        welcomeTitle: "Foundry Core AI",
        welcomeSub: "Kurumsal belgeleriniz ve politika dokümanlarınız üzerinde doğrudan arama yapın.",
        composerPlaceholder: "Belgeleriniz hakkında bir soru sorun…",
        composerHints: "<kbd>Enter</kbd> gönder · <kbd>Shift+Enter</kbd> yeni satır",
        statusReady: "Hazır",
        statusThinking: "Aranıyor…",
        statusGenerating: "Yanıt üretiliyor…",
        statusConnecting: "Bağlanıyor…",
        statusOnline: "Yerel",
        statusOffline: "Sunucu kapalı",
        statusLoadingModel: "Model yükleniyor…",
        btnCopy: "Kopyala",
        btnRedo: "Yeniden üret",
        sourcesHeader: "Kaynaklar",
        matchScore: "eşleşme",
        modalTitle: "Belge Yükle",
        modalSub: ".txt, .md, .pdf, .docx belgelerinizi bilgi tabanına ekleyin. Hemen parçalanır ve indekslenir.",
        dropzoneText: "Dosyayı buraya sürükleyin veya <span class=\"dropzone-link\">göz atmak için tıklayın</span>",
        dropzoneUploading: "yükleniyor ve indeksleniyor…",
        indexedDocsTitle: "İndeksli Belgeler",
        popoverTitle: "Eşleşen kaynak belge parçası.",
        toastNewChat: "Yeni sohbet başlatıldı",
        toastCopied: "Yanıt panoya kopyalandı",
        toastCodeCopied: "Kod panoya kopyalandı",
        toastLangChanged: "Dil Türkçe yapıldı",
        toastDocDeleted: "Belge silindi",
        toastDocUploaded: "başarıyla işlendi ve indekslendi",
        toastUploadError: "Yükleme hatası",
        suggestion1Title: "İzin hakları",
        suggestion1Desc: "Yıllık izin süresi ve talep süreci",
        suggestion1Query: "Yıllık izin hakkım kaç gün ve nasıl talep ederim?",
        suggestion2Title: "VPN kurulumu",
        suggestion2Desc: "SecureConnect adım adım",
        suggestion2Query: "VPN bağlantısı nasıl kurulur?",
        suggestion3Title: "Yan haklar",
        suggestion3Desc: "Yemek kartı ve sigorta detayları",
        suggestion3Query: "Yemek kartına aylık ne kadar yükleme yapılıyor?",
        suggestion4Title: "İş seyahati",
        suggestion4Desc: "Harcırah ve konaklama limitleri",
        suggestion4Query: "İş seyahatinde günlük harcırah ne kadar?",

        // --- Roller ve kullanıcı yönetimi ---
        // "Manager" Turkce'de de kullaniliyor; kurumsal kullanimda yaygin.
        roleManager: "Manager",
        roleUser: "Kullanıcı",
        tagDisabled: "kapalı",
        userNeverLoggedIn: "hiç giriş yapmadı",
        cannotDisableSelf: "Kendi hesabınızı kapatamazsınız",
        disableAccount: "Hesabı kapat",
        usernamePlaceholder: "kullanıcı adı",
        usersLoadFailed: "Kullanıcılar alınamadı: {error}",
        userAdded: "{username} eklendi. Geçici parola: {password}",
        confirmResetPassword: "{username} kullanıcısının parolası sıfırlanacak.\n\nYeni geçici parola:\n{password}\n\nBu parolayı kullanıcıya iletmeniz gerekir. Devam edilsin mi?",
        passwordResetDone: "Parola sıfırlandı: {password}",
        confirmDisableUser: "{username} hesabı kapatılacak ve açık oturumları anında sonlandırılacak. Devam edilsin mi?",
        userDisabled: "{username} kapatıldı",
        pendingPassword: "parola bekliyor",
        lastLogin: "Son giriş",
        btnResetPassword: "Parola sıfırla",
        btnDisable: "Kapat",
        newUserLabel: "Yeni kullanıcı",
        tempPasswordLabel: "Geçici parola",
        roleLabel: "Rol",
        roleUserOption: "Kullanıcı — yalnızca soru sorar",
        roleAdminOption: "Yönetici — belge ve kullanıcı yönetir",
        btnAddUser: "Kullanıcı ekle",
        userCreateHint: "Bu parolayı kullanıcıya siz iletirsiniz; ilk girişte değiştirmesi zorunludur.",
        existingUsers: "Mevcut kullanıcılar ({count})",
        dateLocale: "tr-TR",

        // --- Giriş ve oturum ---
        loggingIn: "Giriş yapılıyor…",
        loginFailed: "Giriş başarısız",
        btnLogin: "Giriş yap",
        passwordsDontMatch: "Yeni parolalar eşleşmiyor",
        changingPassword: "Değiştiriliyor…",
        passwordUpdated: "Parolanız güncellendi. Yeni parolanızla giriş yapın.",
        passwordChangeFailed: "Parola değiştirilemedi",
        btnChangePassword: "Parolayı değiştir",
        sessionExpired: "Oturumunuz sona erdi, tekrar giriş yapın.",

        // --- Genel durum ve hatalar ---
        loading: "Yükleniyor…",
        errorApiDown: "Hata: {error}. API sunucusunun çalıştığından emin olun.",
        queryFailed: "Sorgu gönderilemedi: {error}",
        serverError: "Sunucu hatası",
        noResponse: "Yanıt alınamadı.",
        noDocsYet: "Henüz belge yok. Yükle butonu ile başlayın.",
        noIndexedDocs: "Henüz indekslenmiş belge yok.",
        docsLoadFailed: "Belgeler yüklenemedi",
        confirmDeleteDoc: "Bu belgeyi ve tüm parçalarını silmek istediğinize emin misiniz?",
        noChatsYet: "Henüz sohbet yok.",
        labelChunks: "Parçalar",
        unitChunks: "parça",
        statusHealthy: "Çevrimiçi",
        statusUnhealthy: "Sorunlu",
        modelLoaded: "Yüklendi",
        modelNotLoaded: "Yüklenmedi",
        sectionConnection: "Bağlantı",

        // --- Giriş ekranı (statik HTML) ---
        loginTitle: "Giriş yapın",
        loginSub: "Kurumsal bilgi asistanına erişmek için hesabınızla giriş yapın.",
        labelUsername: "Kullanıcı adı",
        labelPassword: "Parola",
        loginHint: "Hesabınız yoksa sistem yöneticinizle iletişime geçin.",
        passwordSetTitle: "Parolanızı belirleyin",
        passwordSetSub: "Devam etmeden önce size verilen geçici parolayı değiştirmelisiniz.",
        labelCurrentPassword: "Mevcut parola",
        labelNewPassword: "Yeni parola",
        labelNewPassword2: "Yeni parola (tekrar)",
        passwordHint: "En az 8 karakter olmalıdır."
    },
    en: {
        brandName: "Foundry Core AI",
        brandTag: "Local AI Assistant",
        pageTitle: "Chat",
        topbarSub: "Enterprise Knowledge Base",
        newChat: "New Chat",
        historyTitle: "Chat History",
        historySearchPlaceholder: "Search chats…",
        navWorkspace: "Workspace",
        navManagement: "Management",
        navDocs: "Knowledge Base",
        navUploadPopup: "Upload Document",
        navUsers: "Users",
        navSettings: "System Status",
        btnUpload: "Upload",
        welcomeTitle: "Foundry Core AI",
        welcomeSub: "Search your corporate documents and policy files effortlessly.",
        composerPlaceholder: "Ask a question about your documents…",
        composerHints: "<kbd>Enter</kbd> to send · <kbd>Shift+Enter</kbd> for new line",
        statusReady: "Ready",
        statusThinking: "Searching…",
        statusGenerating: "Generating response…",
        statusConnecting: "Connecting…",
        statusOnline: "Local",
        statusOffline: "Server offline",
        statusLoadingModel: "Loading model…",
        btnCopy: "Copy",
        btnRedo: "Regenerate",
        sourcesHeader: "Sources",
        matchScore: "match",
        modalTitle: "Upload Document",
        modalSub: "Add .txt, .md, .pdf, .docx files to the local knowledge base. Chunked and indexed immediately.",
        dropzoneText: "Drop file here or <span class=\"dropzone-link\">click to browse</span>",
        dropzoneUploading: "uploading and indexing…",
        indexedDocsTitle: "Indexed Documents",
        popoverTitle: "Matched source document chunk.",
        toastNewChat: "New chat session started",
        toastCopied: "Response copied to clipboard",
        toastCodeCopied: "Code copied to clipboard",
        toastLangChanged: "Language set to English",
        toastDocDeleted: "Document deleted",
        toastDocUploaded: "successfully processed and indexed",
        toastUploadError: "Upload error",
        suggestion1Title: "Leave Rights",
        suggestion1Desc: "Annual leave duration and request process",
        suggestion1Query: "How many days of annual leave do I have and how do I request it?",
        suggestion2Title: "VPN Setup",
        suggestion2Desc: "SecureConnect step by step",
        suggestion2Query: "How do I set up a VPN connection?",
        suggestion3Title: "Benefits",
        suggestion3Desc: "Meal card and insurance details",
        suggestion3Query: "How much is loaded onto the meal card each month?",
        suggestion4Title: "Business travel",
        suggestion4Desc: "Per diem and accommodation limits",
        suggestion4Query: "What is the daily per diem for business travel?",

        // --- Roles and user management ---
        roleManager: "Manager",
        roleUser: "User",
        tagDisabled: "disabled",
        userNeverLoggedIn: "never signed in",
        cannotDisableSelf: "You cannot disable your own account",
        disableAccount: "Disable account",
        usernamePlaceholder: "username",
        usersLoadFailed: "Could not load users: {error}",
        userAdded: "{username} added. Temporary password: {password}",
        confirmResetPassword: "The password for {username} will be reset.\n\nNew temporary password:\n{password}\n\nYou need to pass this password on to the user. Continue?",
        passwordResetDone: "Password reset: {password}",
        confirmDisableUser: "{username}'s account will be disabled and any open sessions ended immediately. Continue?",
        userDisabled: "{username} disabled",
        pendingPassword: "password pending",
        lastLogin: "Last sign-in",
        btnResetPassword: "Reset password",
        btnDisable: "Disable",
        newUserLabel: "New user",
        tempPasswordLabel: "Temporary password",
        roleLabel: "Role",
        roleUserOption: "User — can only ask questions",
        roleAdminOption: "Manager — manages documents and users",
        btnAddUser: "Add user",
        userCreateHint: "You pass this password to the user; they must change it on first sign-in.",
        existingUsers: "Existing users ({count})",
        dateLocale: "en-US",

        // --- Sign-in and session ---
        loggingIn: "Signing in…",
        loginFailed: "Sign-in failed",
        btnLogin: "Sign in",
        passwordsDontMatch: "New passwords do not match",
        changingPassword: "Changing…",
        passwordUpdated: "Your password has been updated. Sign in with your new password.",
        passwordChangeFailed: "Could not change password",
        sessionExpired: "Your session has expired, please sign in again.",
        btnChangePassword: "Change password",

        // --- General status and errors ---
        loading: "Loading…",
        errorApiDown: "Error: {error}. Make sure the API server is running.",
        queryFailed: "Could not send query: {error}",
        serverError: "Server error",
        noResponse: "No response received.",
        noDocsYet: "No documents yet. Use the Upload button to get started.",
        noIndexedDocs: "No indexed documents yet.",
        docsLoadFailed: "Could not load documents",
        confirmDeleteDoc: "Are you sure you want to delete this document and all of its chunks?",
        noChatsYet: "No chats yet.",
        labelChunks: "Chunks",
        unitChunks: "chunks",
        statusHealthy: "Online",
        statusUnhealthy: "Degraded",
        modelLoaded: "Loaded",
        modelNotLoaded: "Not loaded",
        sectionConnection: "Connection",

        // --- Sign-in screen (static HTML) ---
        loginTitle: "Sign in",
        loginSub: "Sign in with your account to access the enterprise knowledge assistant.",
        labelUsername: "Username",
        labelPassword: "Password",
        loginHint: "If you don't have an account, contact your system administrator.",
        passwordSetTitle: "Set your password",
        passwordSetSub: "You must change the temporary password you were given before continuing.",
        labelCurrentPassword: "Current password",
        labelNewPassword: "New password",
        labelNewPassword2: "New password (repeat)",
        passwordHint: "Must be at least 8 characters."
    }
};

let currentLang = localStorage.getItem('foundry-lang') || 'tr';

export function getLanguage() {
    return currentLang;
}

export function initLanguage() {
    updateDOMTranslations();
}

export function t(key, params) {
    const dict = TRANSLATIONS[currentLang] || TRANSLATIONS.tr;
    let text = dict[key] || TRANSLATIONS.tr[key] || key;
    // {isim} yer tutucularini doldur: t('userAdded', { username: 'ayse' })
    if (params) {
        for (const [name, value] of Object.entries(params)) {
            text = text.split(`{${name}}`).join(value);
        }
    }
    return text;
}

export function setLanguage(lang) {
    if (TRANSLATIONS[lang]) {
        currentLang = lang;
        localStorage.setItem('foundry-lang', lang);
        updateDOMTranslations();
    }
}

export function toggleLanguage() {
    const nextLang = currentLang === 'tr' ? 'en' : 'tr';
    setLanguage(nextLang);
    return nextLang;
}

export function updateDOMTranslations() {
    const dict = TRANSLATIONS[currentLang];

    // <html lang> sabit "tr" idi ve hic guncellenmiyordu. Bu yalnizca
    // bir etiket degil: CSS text-transform:uppercase harf donusumunu
    // sayfanin diline gore yapar ve Turkce'de "i" -> "İ" olur. Sonuc:
    // Ingilizce arayuzde "CHAT HISTORY" yerine "CHAT HİSTORY" goruluyordu.
    // Ekran okuyucularin telaffuzu da bu etikete bakar.
    document.documentElement.lang = currentLang;

    // Update data-i18n text content
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        if (dict[key]) {
            el.innerHTML = dict[key];
        }
    });

    // Update data-i18n-placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.dataset.i18nPlaceholder;
        if (dict[key]) {
            el.placeholder = dict[key];
        }
    });

    // Oneri kartlarinin gonderdigi sorgu metni de dile bagli olmali; aksi
    // halde Ingilizce arayuzde karta tiklayinca Turkce sorgu gonderilirdi.
    document.querySelectorAll('[data-i18n-quick]').forEach(el => {
        const key = el.dataset.i18nQuick;
        if (dict[key]) {
            el.dataset.quick = dict[key];
        }
    });

    // Update language badge button text
    const langSpan = document.getElementById('langText');
    if (langSpan) langSpan.textContent = currentLang.toUpperCase();
}
