async function post(path, body) {
  const r = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  return r.json();
}

async function get(path) {
  const r = await fetch(path);
  return r.json();
}

function renderStatus(data) {
  document.getElementById('meta').textContent = `运行中: ${data.running ? '是' : '否'} | 间隔: ${data.interval_seconds}s | 规则数: ${data.rules.length}`;

  const rows = document.getElementById('rows');
  rows.innerHTML = '';
  for (const item of data.results) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${item.site_name}</td>
      <td>${item.product_name}</td>
      <td class="${item.in_stock ? 'stock' : 'out'}">${item.in_stock ? '有货' : '缺货'}</td>
      <td>${item.reason}</td>
      <td>${item.checked_at}</td>
    `;
    rows.appendChild(tr);
  }

  document.getElementById('errors').textContent = data.errors.length ? data.errors.join('\n') : '暂无';
}

function fillConfig(config) {
  document.getElementById('intervalInput').value = config.interval_seconds ?? 60;
  document.getElementById('smtpEnabled').value = String(Boolean(config.smtp?.enabled));
  document.getElementById('smtpHost').value = config.smtp?.host ?? '';
  document.getElementById('smtpPort').value = config.smtp?.port ?? 587;
  document.getElementById('smtpUser').value = config.smtp?.username ?? '';
  document.getElementById('smtpPassword').value = config.smtp?.password ?? '';
  document.getElementById('smtpFrom').value = config.smtp?.from_email ?? '';
  document.getElementById('smtpTo').value = config.smtp?.to_email ?? '';
  document.getElementById('rulesText').value = JSON.stringify(config.rules ?? [], null, 2);
}

function collectConfig() {
  return {
    interval_seconds: Number(document.getElementById('intervalInput').value),
    user_agent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    smtp: {
      enabled: document.getElementById('smtpEnabled').value === 'true',
      host: document.getElementById('smtpHost').value,
      port: Number(document.getElementById('smtpPort').value || 587),
      username: document.getElementById('smtpUser').value,
      password: document.getElementById('smtpPassword').value,
      from_email: document.getElementById('smtpFrom').value,
      to_email: document.getElementById('smtpTo').value,
      use_tls: true,
    },
    rules: JSON.parse(document.getElementById('rulesText').value),
  };
}

async function refresh() {
  const status = await get('/api/status');
  renderStatus(status);
}

async function loadConfig() {
  const data = await get('/api/config');
  if (data.ok) fillConfig(data.config);
}

document.getElementById('startBtn').onclick = async () => { await post('/api/start'); await refresh(); };
document.getElementById('stopBtn').onclick = async () => { await post('/api/stop'); await refresh(); };
document.getElementById('checkBtn').onclick = async () => { await post('/api/check-now'); await refresh(); };
document.getElementById('reloadBtn').onclick = async () => { await post('/api/reload'); await loadConfig(); await refresh(); };
document.getElementById('saveConfigBtn').onclick = async () => {
  const msg = document.getElementById('saveMsg');
  try {
    const payload = collectConfig();
    const result = await post('/api/config', payload);
    if (!result.ok) throw new Error(result.error || '保存失败');
    msg.textContent = '配置保存成功';
    await refresh();
  } catch (err) {
    msg.textContent = `保存失败: ${err.message}`;
  }
};

setInterval(refresh, 5000);
loadConfig();
refresh();
