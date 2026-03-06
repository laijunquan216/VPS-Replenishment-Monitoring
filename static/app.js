async function post(path) {
  const r = await fetch(path, { method: 'POST' });
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

async function refresh() {
  const r = await fetch('/api/status');
  renderStatus(await r.json());
}

document.getElementById('startBtn').onclick = async () => { await post('/api/start'); await refresh(); };
document.getElementById('stopBtn').onclick = async () => { await post('/api/stop'); await refresh(); };
document.getElementById('checkBtn').onclick = async () => { await post('/api/check-now'); await refresh(); };
document.getElementById('reloadBtn').onclick = async () => { await post('/api/reload'); await refresh(); };

setInterval(refresh, 5000);
refresh();
