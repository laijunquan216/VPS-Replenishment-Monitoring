# VPS Replenishment Monitoring

一个可扩展的 VPS 补货监控面板，支持：

- 多站点规则（通过 `product_anchor + keywords` 适配不同 VPS 页面结构）
- 精准监控指定套餐（例如 `US.LA.TRI.Basic`）
- 补货时邮件通知（状态从缺货 -> 有货时触发）
- Web 可视化面板（查看实时状态、错误日志、手动检测）

## 快速开始

```bash
python -m app.server
```

打开 `http://localhost:8080`。

## 配置

编辑 `config.json`：

- `interval_seconds`: 轮询间隔
- `smtp.enabled=true`: 启用邮件通知
- `rules[]`: 每个网站一条规则
  - `product_anchor`: 套餐名称（用于定位页面区块）
  - `unavailable_tokens`: 缺货关键词
  - `available_tokens`: 有货关键词

### 精准识别建议

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
