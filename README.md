# VPS Replenishment Monitoring

一个可扩展的 VPS 补货监控面板，支持：

- 多站点规则（通过 `product_anchor + keywords` 适配不同 VPS 页面结构）
- 精准监控指定套餐（例如 `US.LA.TRI.Basic`）
- 补货时邮件通知（状态从缺货 -> 有货时触发）
- Web 可视化面板（查看实时状态、错误日志、手动检测、在线改配置）

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

### 4) 启动服务

```bash
python -m app.server
```

默认端口：`8899`（可通过环境变量修改）：

```bash
PORT=9000 python -m app.server
```

打开：`http://localhost:8899`

### 5) 在 WebUI 配置规则和邮件通知

进入面板后，在 **“面板配置（监控规则 + 邮件通知）”** 区域直接修改并保存：

- `interval_seconds`（轮询间隔）
- `rules`（监控规则 JSON 数组）
- SMTP（启用、host、port、用户名、密码、收发件邮箱）

保存后立即生效（服务端会进行字段校验，异常会在页面提示）。

### 6) 面板操作

- 点击“立即检测”做一次手动检查
- 点击“开始轮询”进入自动监控
- 检测到从缺货 -> 有货时会触发邮件通知（仅状态变化时触发）

---

## 面板更新流程（升级到最新版本）

### 方式 A：直接在服务器上更新

```bash
cd VPS-Replenishment-Monitoring
git pull
```

如果你使用 systemd/pm2/supervisor，请重启服务让新代码生效。

### 方式 B：本地修改后发布

```bash
git add .
git commit -m "feat: your update"
git push
```

然后在部署机器执行 `git pull` + 重启进程。

> 更新前建议备份 `config.json`（如果你不只在 WebUI 管理配置）。

## 精准识别建议

1. 先在浏览器检查页面 HTML 文本（右键查看源代码）
2. 将套餐名放到 `product_anchor`
3. 选择与该套餐卡片强相关的状态词作为 tokens
4. 如果网站是 JS 动态渲染，可改为监控其公开 API 或在后续接入 Playwright 抓取

## API

- `GET /api/status`
- `GET /api/config`
- `POST /api/config`
- `POST /api/start`
- `POST /api/stop`
- `POST /api/check-now`
- `POST /api/reload`

## 测试

```bash
python -m unittest discover -s tests
```
