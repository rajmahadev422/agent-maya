
const $ = s => document.querySelector(s);
const wrap = $('#wrap'), feed = $('#feed'), list = $('#list'), input = $('#in'), sendBtn = $('#send');

/* thinking button */
let think = localStorage.getItem('think') !== 'off', canThink = true;
const thinkBtn = $('#think');
function renderThink() {
    if (!canThink) {
        thinkBtn.disabled = true;
        thinkBtn.setAttribute('aria-pressed', 'false');
        thinkBtn.textContent = 'Think: n/a';
        thinkBtn.title = 'This model has no thinking mode';
        return;
    }
    thinkBtn.disabled = false;
    thinkBtn.setAttribute('aria-pressed', think);
    thinkBtn.textContent = 'Think: ' + (think ? 'on' : 'off');
}
thinkBtn.onclick = () => {
    think = !think;
    localStorage.setItem('think', think ? 'on' : 'off');
    renderThink();
    console.log(think)
};
renderThink();

/* chats */
let chats = [], current = null, busy = false, stick = true;

const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const api = async (u, o) => { const r = await fetch(u, o); if (!r.ok) throw new Error(await r.text()); return r.json(); };
const ago = t => { const s = Date.now() / 1000 - t; return s < 60 ? 'just now' : s < 3600 ? Math.floor(s / 60) + 'm ago' : s < 86400 ? Math.floor(s / 3600) + 'h ago' : Math.floor(s / 86400) + 'd ago'; };
const scroll = () => { if (stick) feed.scrollTop = feed.scrollHeight; };
feed.onscroll = () => { stick = feed.scrollHeight - feed.scrollTop - feed.clientHeight < 80; };

/* ---------- sidebar ---------- */
function renderList() {
    list.replaceChildren(...chats.map(c => {
        const b = el('button', 'chat' + (c.id === current ? ' on' : ''));
        b.append(el('span', 't', c.title), el('span', 'm', `${c.turns} messages, ${ago(c.updated)}`));
        b.onclick = () => openChat(c.id);
        return b;
    }));
}
async function refresh() { chats = await api('/api/chats'); renderList(); }
function setTitle() { const c = chats.find(c => c.id === current); $('#title').textContent = c ? c.title : 'New chat'; }
const closeSide = () => $('#side').classList.remove('open');

/* ---------- message builders ---------- */
const showEmpty = () => wrap.replaceChildren(el('div', 'empty', 'Ask Maya something, or open a saved chat from the list.'));
function row(role) {
    const r = el('div', 'row ' + role), b = el('div', 'body');
    r.append(el('div', 'who', role === 'user' ? 'You' : 'Maya'), b);
    wrap.append(r); scroll(); return b;
}
const addUser = text => { row('user').textContent = text; };
const asst = () => ({ body: row('maya'), think: null, ans: null, t0: Date.now() });

function addThink(s, text, open = true) {
    if (!s.think) {
        const d = el('details', 'think'); d.open = open;
        d.append(el('summary', null, 'Thinking'), el('div', 'tx'));
        s.body.append(d); s.think = d;
    }
    s.think.lastChild.textContent += text; scroll();
}
function closeThink(s) {
    if (s.think && s.think.open) {
        s.think.open = false;
        s.think.firstChild.textContent = 'Thought for ' + Math.max(1, Math.round((Date.now() - s.t0) / 1000)) + 's';
    }
}
function addContent(s, text) {
    if (!s.ans) { s.ans = el('div', 'ans'); s.body.append(s.ans); }
    s.ans.textContent += text; scroll();
}
function addTool(s, name, args) {
    const c = el('div', 'tool run'); c.dataset.name = name;
    const h = el('div', 'th'); h.append(el('span', 'fn', name + '()'), el('span', 'st', 'running'));
    c.append(h, el('div', 'lbl', 'Arguments'), el('pre', null, JSON.stringify(args, null, 2)));
    s.body.append(c); scroll();
}
function addResult(name, text) {
    const c = [...wrap.querySelectorAll('.tool.run')].find(x => x.dataset.name === name);
    if (!c) return;
    const failed = /^(Tool failed|Error)/.test(text);
    c.classList.remove('run'); c.classList.toggle('fail', failed);
    c.querySelector('.st').textContent = failed ? 'failed' : 'done';
    const d = el('details'); d.open = text.length < 400;
    d.append(el('summary', null, 'Result'), el('pre', null, text));
    c.append(d); scroll();
}
function note(text, err) { wrap.append(el('p', 'note' + (err ? ' err' : ''), text)); scroll(); }

/* ---------- open a saved chat ---------- */
async function openChat(id) {
    if (busy) return;
    current = id; renderList(); closeSide();
    const d = await api('/api/chats/' + id);
    wrap.replaceChildren();
    for (const m of d.messages) {
        if (m.role === 'user') addUser(m.content);
        else if (m.role === 'assistant') {
            if (!(m.thinking || m.content || m.tool_calls.length)) continue;
            const s = asst();
            if (m.thinking) addThink(s, m.thinking, false);
            if (m.content) addContent(s, m.content);
            m.tool_calls.forEach(c => addTool(s, c.name, c.arguments));
        } else if (m.role === 'tool') addResult(m.name, m.content);
    }
    wrap.querySelectorAll('.tool.run').forEach(c => { c.classList.remove('run'); c.querySelector('.st').textContent = 'no result saved'; });
    if (!wrap.children.length) showEmpty();
    setTitle(); stick = true; feed.scrollTop = feed.scrollHeight;
}

/* ---------- send + stream ---------- */
async function send(text) {
    text = text.trim();
    if (busy || !text) return;
    busy = true; sendBtn.disabled = true; sendBtn.textContent = 'Working…';
    try {
        if (!current) {
            current = (await api('/api/chats', { method: 'POST' })).id;
            chats.unshift({ id: current, title: text.slice(0, 48), turns: 0, updated: Date.now() / 1000 });
            renderList(); setTitle();
        }
        if (wrap.querySelector('.empty')) wrap.replaceChildren();
        addUser(text); stick = true;
        let s = null; const S = () => s || (s = asst());

        const res = await fetch(`/api/chats/${current}/message`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text, think })
        });
        if (!res.ok) throw new Error(await res.text());
        const reader = res.body.getReader(), dec = new TextDecoder(); let buf = '';
        const handle = e => {
            if (e.type === 'step') s = null;
            else if (e.type === 'thinking') addThink(S(), e.text);
            else if (e.type === 'content') { closeThink(S()); addContent(s, e.text); }
            else if (e.type === 'tool_call') { closeThink(S()); addTool(s, e.name, e.arguments); }
            else if (e.type === 'tool_result') addResult(e.name, e.result);
            else if (e.type === 'notice') note(e.text);
            else if (e.type === 'error') note(e.text, true);
        };
        for (; ;) {
            const { done, value } = await reader.read(); if (done) break;
            buf += dec.decode(value, { stream: true });
            let i; while ((i = buf.indexOf('\n')) >= 0) { const line = buf.slice(0, i); buf = buf.slice(i + 1); if (line.trim()) handle(JSON.parse(line)); }
        }
    } catch (err) { note(String(err.message || err), true); }
    busy = false; sendBtn.disabled = false; sendBtn.textContent = 'Send';
    wrap.querySelectorAll('.tool.run').forEach(c => { c.classList.remove('run'); c.querySelector('.st').textContent = 'no result'; });
    await refresh(); setTitle(); input.focus();
}

/* Voice transcribtion */
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
const mic = $('#mic');

if (!SR) {
    mic.onclick = () => note('This browser has no speech recognition. Use Chrome or Edge.', true);
} else {
    const rec = new SR();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = 'en-IN';
    let base = '';

    rec.onstart = () => mic.classList.add('on');
    rec.onend = () => mic.classList.remove('on');
    rec.onerror = e => note('Speech recognition error: ' + e.error, true);
    rec.onresult = e => {
        let text = '';
        for (const r of e.results) text += r[0].transcript;
        input.value = base + text;
        input.oninput();
    };

    mic.onclick = () => {
        try {
            if (mic.classList.contains('on')) rec.stop();
            else { base = input.value ? input.value + ' ' : ''; rec.start(); }
        } catch (err) { note(String(err), true); }
    };
}

/* ---------- wiring ---------- */
$('#form').onsubmit = e => { e.preventDefault(); const t = input.value; input.value = ''; input.style.height = 'auto'; send(t); };
input.onkeydown = e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); $('#form').requestSubmit(); } };
input.oninput = () => { input.style.height = 'auto'; input.style.height = input.scrollHeight + 'px'; };
$('#new').onclick = () => { if (busy) return; current = null; showEmpty(); setTitle(); renderList(); closeSide(); input.focus(); };
$('#menu').onclick = () => $('#side').classList.toggle('open');

(async () => {
    showEmpty();
    const i = await api('/api/info');
    $('#model').textContent = i.model;
    $('#dir').textContent = i.data_dir;
    canThink = i.capabilities.includes('thinking');
    renderThink()
    await refresh();
})();