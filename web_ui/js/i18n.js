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
        statusOnline: "Çevrimiçi · yerel",
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
        suggestion2Query: "VPN bağlantısı nasıl kurulur?"
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
        statusOnline: "Online · local",
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
        suggestion2Query: "How do I set up a VPN connection?"
    }
};

let currentLang = localStorage.getItem('foundry-lang') || 'tr';

export function getLanguage() {
    return currentLang;
}

export function initLanguage() {
    updateDOMTranslations();
}

export function t(key) {
    const dict = TRANSLATIONS[currentLang] || TRANSLATIONS.tr;
    return dict[key] || key;
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

    // Update language badge button text
    const langSpan = document.getElementById('langText');
    if (langSpan) langSpan.textContent = currentLang.toUpperCase();
}
