const form = document.querySelector('#chat-form');
const input = document.querySelector('#message-input');
const messages = document.querySelector('#messages');
const sendButton = document.querySelector('#send-button');
const historyPanel = document.querySelector('#history-panel');
const historyBackdrop = document.querySelector('#history-backdrop');
const historySearch = document.querySelector('#history-search');
const characterCount = document.querySelector('#character-count');

const escapeHtml = (value) => {
  const element = document.createElement('div');
  element.textContent = value;
  return element.innerHTML;
};

const currentTime = () => new Intl.DateTimeFormat([], {
  hour: '2-digit', minute: '2-digit',
}).format(new Date());

function addMessage(text, role, meta = currentTime()) {
  const isUser = role === 'user';
  const article = document.createElement('article');
  article.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
  article.innerHTML = `
    <div class="avatar ${isUser ? 'user-avatar' : 'bot-avatar'}">${isUser ? 'Y' : '✦'}</div>
    <div class="message-body">
      <div class="message-heading"><strong>${isUser ? 'You' : 'Nova'}</strong><span>${escapeHtml(meta)}</span></div>
      <div class="bubble"><p>${escapeHtml(text)}</p></div>
    </div>`;
  messages.append(article);
  messages.scrollTop = messages.scrollHeight;
  return article;
}

function showTyping() {
  const article = document.createElement('article');
  article.className = 'message bot-message typing';
  article.innerHTML = `<div class="avatar bot-avatar">✦</div><div class="message-body"><div class="message-heading"><strong>Nova</strong><span>Thinking locally…</span></div><div class="bubble"><i></i><i></i><i></i></div></div>`;
  messages.append(article);
  messages.scrollTop = messages.scrollHeight;
  return article;
}

function bindHistoryItem(item) {
  item.addEventListener('click', () => {
    document.querySelectorAll('.history-item').forEach((entry) => entry.classList.remove('is-active'));
    item.classList.add('is-active');
    input.value = item.dataset.prompt;
    updateComposer();
    closeHistory();
    input.focus();
  });
}

function updateRecentCount() {
  const visible = [...document.querySelectorAll('.history-item')].filter((item) => !item.hidden);
  document.querySelector('#recent-count').textContent = visible.length;
}

function rememberPrompt(message) {
  const items = [...document.querySelectorAll('.history-item')];
  const duplicate = items.find((item) => item.dataset.prompt === message);
  document.querySelectorAll('.history-item').forEach((item) => item.classList.remove('is-active'));
  if (duplicate) {
    duplicate.classList.add('is-active');
    return;
  }
  const button = document.createElement('button');
  button.className = 'history-item is-active';
  button.dataset.prompt = message;
  button.innerHTML = `<span class="history-icon">✦</span><span><strong>${escapeHtml(message)}</strong><small>Just now</small></span><b>•••</b>`;
  document.querySelector('#recent-list').prepend(button);
  bindHistoryItem(button);
  updateRecentCount();
}

async function sendMessage(message) {
  addMessage(message, 'user');
  rememberPrompt(message);
  const typing = showTyping();
  sendButton.disabled = true;
  input.disabled = true;
  try {
    const response = await fetch('/api/chat', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message}),
    });
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    const data = await response.json();
    typing.remove();
    addMessage(data.reply, 'bot', `${data.intent} · ${Math.round(data.confidence * 100)}% confidence`);
  } catch (error) {
    typing.remove();
    const failed = addMessage('I could not reach the Python server. Check that Uvicorn is running and try again.', 'bot', 'Connection error');
    failed.classList.add('error-message');
  } finally {
    sendButton.disabled = false;
    input.disabled = false;
    input.focus();
  }
}

function resetChat() {
  messages.innerHTML = `<div class="date-label"><span>New conversation</span></div><article class="message bot-message"><div class="avatar bot-avatar">✦</div><div class="message-body"><div class="message-heading"><strong>Nova</strong><span>Ready</span></div><div class="bubble"><p>Fresh start. What would you like to explore?</p></div></div></article>`;
  document.querySelectorAll('.history-item').forEach((item) => item.classList.remove('is-active'));
  closeHistory();
  input.focus();
}

function openHistory() { historyPanel.classList.add('is-open'); historyBackdrop.classList.add('is-open'); }
function closeHistory() { historyPanel.classList.remove('is-open'); historyBackdrop.classList.remove('is-open'); }
function updateComposer() {
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, 140)}px`;
  characterCount.textContent = `${input.value.length} / 1000`;
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  input.value = '';
  updateComposer();
  sendMessage(message);
});
input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); }
});
input.addEventListener('input', updateComposer);
document.querySelectorAll('.prompt-chip').forEach((button) => button.addEventListener('click', () => {
  input.value = button.textContent.replace(/^\d{2}/, '').trim();
  form.requestSubmit();
}));
document.querySelectorAll('.history-item').forEach(bindHistoryItem);
document.querySelector('#new-chat-button').addEventListener('click', resetChat);
document.querySelector('#history-toggle').addEventListener('click', openHistory);
document.querySelector('#history-close').addEventListener('click', closeHistory);
historyBackdrop.addEventListener('click', closeHistory);
document.querySelector('.notice button').addEventListener('click', (event) => event.currentTarget.parentElement.remove());
historySearch.addEventListener('input', () => {
  const query = historySearch.value.trim().toLowerCase();
  document.querySelectorAll('.history-item').forEach((item) => { item.hidden = !item.textContent.toLowerCase().includes(query); });
  updateRecentCount();
});
fetch('/api/health').then((response) => response.json()).then((data) => {
  document.querySelector('#model-summary').textContent = `${data.intents} intents · ${data.examples} examples`;
}).catch(() => { document.querySelector('#model-summary').textContent = 'Model status unavailable'; });
updateComposer();
