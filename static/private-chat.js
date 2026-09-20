'use strict';
(() => {
    const cfg = window.privateChatConfig;
    let partner = cfg.partner || null;
    let signature = '';
    let busy = false;
    let sending = false;
    let messages, input, form, error;
    const root = cfg.list ? document.getElementById('chat-preview') : document.querySelector('.chat-container');

    function setup() {
        signature = '';
        if (cfg.list) {
            root.replaceChildren();
            root.append(textElement('div', `Chat mit ${partner.username}`, 'chat-header-fixed'));
            messages = document.createElement('div'); messages.id = 'chat-messages';
            form = document.createElement('form'); form.id = 'sendForm';
            const row = textElement('div', '', 'chat-form-row');
            input = document.createElement('input'); input.id = 'msgInput'; input.type = 'text'; input.required = true; input.maxLength = 10000; input.placeholder = 'Nachricht...'; input.setAttribute('aria-label', 'Nachricht');
            const submit = textElement('button', 'Senden'); submit.type = 'submit';
            row.append(input, submit); form.append(row); root.append(messages, form);
        } else {
            messages = document.getElementById('messages'); input = document.getElementById('msgInput'); form = document.getElementById('sendForm');
            document.getElementById('chat-partner').textContent = partner.username;
        }
        error = textElement('p', '', 'chat-error'); error.setAttribute('role', 'status'); root.append(error);
        form.addEventListener('submit', send);
        input.focus();
    }

    function render(rows) {
        const next = JSON.stringify(rows);
        if (next === signature) return;
        const scroll = !signature || messages.scrollHeight - messages.scrollTop - messages.clientHeight < 80;
        signature = next;
        const nodes = rows.map(m => {
            const mine = m.sender_id === cfg.userId;
            const row = textElement('div', '', 'chat-msg-row ' + (mine ? 'me' : 'them'));
            const meta = textElement('div', `${mine ? 'Du' : m.sender_name}\n${new Date(m.timestamp).toLocaleString()}`, 'chat-msg-meta');
            const bubble = textElement('div', m.content, 'chat-msg-bubble');
            row.append(...(mine ? [bubble, meta] : [meta, bubble]));
            return row;
        });
        messages.replaceChildren(...(nodes.length ? nodes : [textElement('p', 'Noch keine Nachrichten.')]));
        if (scroll) messages.scrollTop = messages.scrollHeight;
    }

    async function previews() {
        if (!cfg.list) return;
        const rows = await requestJSON('/api/chat/private/conversations');
        const byId = new Map(rows.map(m => [m.partner_id, m]));
        cfg.users.forEach(user => {
            const el = document.getElementById('last-msg-' + user.id);
            if (!el) return;
            const m = byId.get(user.id);
            el.textContent = m ? `${m.sender_id === cfg.userId ? 'Du' : user.username}: ${m.content} (${new Date(m.timestamp).toLocaleString()})` : 'Noch keine Nachrichten';
        });
    }

    async function refresh() {
        if (busy) return;
        busy = true;
        const selected = partner?.id;
        try {
            if (selected) {
                const rows = await requestJSON(`/chat/private/${cfg.userId}/${selected}`);
                if (partner?.id === selected) {render(rows); if (!sending) error.textContent = '';}
            }
            await previews();
        } catch (e) { if (error) error.textContent = e.message; }
        finally {busy = false;}
    }

    async function send(event) {
        event.preventDefault();
        const content = input.value.trim();
        if (!content || sending) return;
        sending = true;
        const selected = partner.id;
        const field = input;
        const button = form.querySelector('button'); button.disabled = true;
        try {
            await requestJSON('/chat/private/send', jsonOptions({receiver_id: selected, content}));
            if (input === field && input.value.trim() === content) input.value = '';
            signature = '';
            await refresh();
        } catch (e) {error.textContent = e.message;}
        finally {sending = false; button.disabled = false;}
    }

    if (cfg.list) {
        document.querySelectorAll('[data-chat-user]').forEach(item => {
            item.addEventListener('click', () => {
                partner = cfg.users.find(u => u.id === Number(item.dataset.chatUser));
                setup(); refresh();
            });
            item.addEventListener('keydown', e => {if(e.key === 'Enter' || e.key === ' ') {e.preventDefault(); item.click();}});
        });
    } else setup();
    refresh();
    const timer = setInterval(refresh, 1500);
    window.addEventListener('pagehide', () => clearInterval(timer), {once: true});
})();
