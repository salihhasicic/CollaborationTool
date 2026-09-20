'use strict';
window.requestJSON = async function(url, options = {}) {
    const response = await fetch(url, {credentials: 'same-origin', ...options});
    let body;
    try { body = await response.json(); } catch { throw new Error('Die Antwort konnte nicht geladen werden. Bitte erneut versuchen.'); }
    if (!response.ok) {
        if (response.status === 401 && !location.pathname.startsWith('/login')) location.assign('/login');
        throw new Error(body.message || body.error || 'Die Anfrage konnte nicht ausgeführt werden.');
    }
    return body;
};
window.jsonOptions = body => ({method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
window.textElement = (tag, text, className) => {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    return node;
};
document.addEventListener('error', event => {
    if (event.target instanceof HTMLImageElement && !event.target.src.endsWith('/static/avatar.svg')) {
        event.target.src = '/static/avatar.svg';
    }
}, true);
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('nav a').forEach(a => a.setAttribute('aria-label', a.textContent.trim()));
    document.querySelectorAll('img').forEach(img => {
        if (img.complete && img.naturalWidth === 0) img.src = '/static/avatar.svg';
    });
    if (location.pathname === '/login') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_id');
    }
});
