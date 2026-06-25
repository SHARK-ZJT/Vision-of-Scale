# AGENTS.md — Vision of Scale

文生图应用 — 巨构与人的对比 (Megastructure vs Human Scale)
FastAPI + HTMX + Alpine.js + 火山引擎 即梦AI

## Startup Workflow

开始工作前：

1. **激活虚拟环境** `venv\Scripts\activate` (Windows) 或 `source venv/bin/activate` (Mac/Linux)
2. **完整阅读本文件**
3. **运行 `./init.sh`** 确认环境健康
4. **读取 `feature_list.json`** 了解当前 feature 状态
5. **读取 `progress.md`** 了解会话进展

如果基线验证失败，先修复再开始新功能。

## 工作规则

- **一次只做一个 feature**：从 `feature_list.json` 中挑选一个未完成的 feature
- **验证必须通过**：完成时必须运行验证命令并确认通过
- **更新制品**：会话结束前更新 `progress.md` 和 `feature_list.json`
- **不要越界**：不要修改与当前 feature 无关的文件
- **保持干净状态**：下次会话必须能直接运行 `./init.sh`

## 项目结构速览

```
app/
├── main.py              # FastAPI 入口
├── config.py            # 配置 (pydantic-settings)
├── models/              # SQLAlchemy ORM 模型
├── schemas/             # Pydantic 请求/响应
├── routers/             # 路由处理器
│   ├── pages.py         # HTML 页面路由
│   ├── generate.py      # POST /api/generate
│   ├── gallery.py       # 图库 HTMX partials
│   ├── templates_api.py # 模板 API
│   └── collections_api.py # 收藏 CRUD
├── services/            # 业务逻辑
├── templates/           # Jinja2 HTML
└── static/              # CSS, JS, 图片
```

## Definition of Done

一个 feature 完成的条件：

- [ ] 目标功能已实现（前后端完整）
- [ ] 验证已通过（`python -m compileall .` 无错误）
- [ ] 应用能正常启动：`uvicorn app.main:app --reload`
- [ ] 证据已记录在 `feature_list.json` 或 `progress.md`

## 会话结束

结束会话前：

1. 更新 `progress.md` 记录当前状态
2. 更新 `feature_list.json` 标记 feature 状态
3. 记录未解决的阻塞项和风险
4. 运行 `git add . && git commit -m "描述信息"` 提交当前安全状态

## 验证命令

```bash
# 完整验证（推荐）
./init.sh

# 手动启动开发服务器测试
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 升级处理

遇到以下情况时：
- **架构决策**：查阅 README 或询问用户
- **需求不明确**：检查 feature 描述，否则询问用户
- **重复验证失败**：更新进度，标记人工审查
- **范围模糊**：重新阅读 `feature_list.json` 中的完成定义
