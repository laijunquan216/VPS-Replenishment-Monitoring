# VPS Replenishment Monitoring

一个可扩展的 VPS 补货监控面板，支持：

- 多站点规则（通过 `product_anchor + keywords` 适配不同 VPS 页面结构）
- 精准监控指定套餐（例如 `US.LA.TRI.Basic`）
- 补货时邮件通知（状态从缺货 -> 有货时触发）
- Web 可视化面板（查看实时状态、错误日志、手动检测）

## 安装流程（推荐）

> 适用于 Linux / macOS / WSL。Windows PowerShell 仅命令有少量差异。

### 1) 获取代码

```bash
git clone https://github.com/laijunquan216/VPS-Replenishment-Monitoring.git
cd VPS-Replenishment-Monitoring
```

### 2) 检查 Python 版本

要求 Python 3.10+：

```bash
python3 --version
```

### 3) 创建并启用虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4) 配置监控规则

项目默认使用 `config.json`，你只需要按需修改：

- `interval_seconds`：轮询间隔（秒）
- `rules[]`：每个站点一条规则
  - `site_name`：站点名称（展示用）
  - `url`：监控页面地址
  - `product_name`：套餐名称（展示用）
  - `product_anchor`：用于定位套餐区块的锚点文本（建议与套餐标题一致）
  - `unavailable_tokens`：缺货关键词
  - `available_tokens`：有货关键词

示例已内置：

- VMISS：`US.LA.TRI.Basic`
- MadcityServers：`New York Amd Ryzen Standard`

### 5) 配置邮件通知（可选）

在 `config.json` 中将 SMTP 打开：

```json
"smtp": {
  "enabled": true,
  "host": "smtp.example.com",
  "port": 587,
  "username": "your_user",
  "password": "your_password_or_app_token",
  "from_email": "alert@example.com",
  "to_email": "you@example.com",
  "use_tls": true
}
```

> 建议使用邮箱的应用专用密码（App Password），不要使用主密码。

### 6) 启动服务

```bash
python -m app.server
```

启动后打开：`http://localhost:8080`

### 7) 面板操作

- 点击“立即检测”做一次手动检查
- 点击“开始轮询”进入自动监控
- 检测到从缺货 -> 有货时会触发邮件通知（仅状态变化时触发）

---

## 精准识别建议

1. 先在浏览器检查页面 HTML 文本（右键查看源代码）
2. 将套餐名放到 `product_anchor`
3. 选择与该套餐卡片强相关的状态词作为 tokens
4. 如果网站是 JS 动态渲染，可改为监控其公开 API 或在后续接入 Playwright 抓取

## API

- `GET /api/status`
- `POST /api/start`
- `POST /api/stop`
- `POST /api/check-now`
- `POST /api/reload`

## 测试

```bash
python -m unittest discover -s tests
```
