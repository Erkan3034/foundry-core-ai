// Foundry Web UI — Rich Markdown Renderer

export function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

export function renderMarkdown(text) {
    if (!text) return '';
    let safe = escapeHtml(text);

    // 1. Source inline badge
    safe = safe.replace(/\[Kaynak:\s*([^\]]+)\]/gi, (match, docName) => {
        return `<span class="source-inline-badge" data-doc="${escapeHtml(docName.trim())}">📄 ${escapeHtml(docName.trim())}</span>`;
    });

    // 2. Fenced Code Blocks (```lang\ncode\n```)
    safe = safe.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        const language = lang || 'text';
        return `<div class="code-block-wrapper"><div class="code-block-header"><span>${language}</span><button class="copy-code-btn" type="button">Kopyala</button></div><pre><code>${code.trim()}</code></pre></div>`;
    });

    // 3. Inline Code (`code`)
    safe = safe.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

    // 4. Bold & Italic
    safe = safe.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    safe = safe.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // 5. Images (![alt](url)) & Links ([text](url))
    safe = safe.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img class="chat-img" src="$2" alt="$1">');
    safe = safe.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

    // 6. Markdown Tables (| col1 | col2 |)
    const lines = safe.split('\n');
    const out = [];
    let list = null;
    let tableLines = [];

    const flushTable = () => {
        if (!tableLines.length) return;
        let html = '<div class="ui-table-wrapper"><table class="ui-table">';
        let isHeader = true;
        for (let i = 0; i < tableLines.length; i++) {
            const line = tableLines[i].trim();
            if (line.match(/^\|?\s*:?-+:?\s*\|/)) {
                isHeader = false;
                continue;
            }
            const cells = line.split('|').map(c => c.trim()).filter((c, idx, arr) => idx > 0 && idx < arr.length - 1 || c !== '');
            if (!cells.length) continue;
            if (isHeader) {
                html += '<thead><tr>' + cells.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>';
            } else {
                html += '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>';
            }
        }
        html += '</tbody></table></div>';
        out.push(html);
        tableLines = [];
    };

    const flushList = () => {
        if (!list) return;
        out.push(`<${list.type}>` + list.items.map(i => `<li>${i}</li>`).join('') + `</${list.type}>`);
        list = null;
    };

    for (const raw of lines) {
        const line = raw.trim();

        if (line.startsWith('|') && line.endsWith('|')) {
            flushList();
            tableLines.push(line);
            continue;
        } else if (tableLines.length) {
            flushTable();
        }

        if (!line) { flushList(); continue; }

        if (line.startsWith('&gt;') || line.startsWith('>')) {
            flushList();
            out.push(`<blockquote class="chat-quote">${line.replace(/^(&gt;|>)\s*/, '')}</blockquote>`);
            continue;
        }

        const ol = line.match(/^(\d+)[.)]\s+(.*)/);
        const ul = line.match(/^[-•*]\s+(.*)/);
        if (ol) {
            if (!list || list.type !== 'ol') { flushList(); list = { type: 'ol', items: [] }; }
            list.items.push(ol[2]);
        } else if (ul) {
            if (!list || list.type !== 'ul') { flushList(); list = { type: 'ul', items: [] }; }
            list.items.push(ul[1]);
        } else if (!line.startsWith('<div') && !line.startsWith('<pre') && !line.startsWith('<blockquote')) {
            flushList();
            out.push(`<p>${line}</p>`);
        } else {
            flushList();
            out.push(line);
        }
    }
    flushList();
    flushTable();
    return out.join('');
}
