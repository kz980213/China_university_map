# 技术栈版本基线

> ⚠️ 版本管理规范：未经确认，不允许升级依赖版本；不允许使用 latest；不允许随意更换技术栈。

---

## 前端

| 类别 | 技术 | 锁定版本 |
|------|------|----------|
| | 运行时 | Node.js | 22.22.0 |
| | 包管理器 | pnpm | 10.21.0 |
| | 框架 | Vue | 3.5.35 |
| | 构建工具 | Vite | 8.0.16 |
| | 语言 | TypeScript | 5.9.3 |
| | Vue 插件 | @vitejs/plugin-vue | 6.0.7 |
| | 路由 | vue-router | 5.1.0 |
| | 状态管理 | pinia | 3.0.4 |
| | UI 组件库 | element-plus | 2.14.1 |
| | 图表 | echarts | 6.1.0 |
| | CSS 预处理器 | sass | 1.100.0 |
| | 类型检查 | vue-tsc | 3.2.0 |
| | Node 类型 | @types/node | 22.19.7 |

## 后端

| 类别 | 技术 | 锁定版本 |
|------|------|----------|
| | 运行时 | Python | 3.12.13 |
| | Web 框架 | fastapi | 0.136.3 |
| | ASGI 服务器 | uvicorn[standard] | 0.48.0 |
| | 数据验证 | pydantic | 2.13.4 |
| | 配置管理 | pydantic-settings | 2.14.1 |
| | ORM | SQLAlchemy | 2.0.50 |
| | 数据库迁移 | alembic | 1.18.4 |
| | PostgreSQL 驱动 | psycopg[binary] | 3.3.4 |
| | 环境变量 | python-dotenv | 1.2.2 |
| | 测试 | pytest | 9.0.3 |

## 数据库（第二阶段启用）

| 类别 | 技术 | 版本 |
|------|------|------|
| | 关系型数据库 | PostgreSQL | 16.x |
| | 缓存 | Redis | 7.x |

---

## 地图方案

| 类别 | 技术 | 说明 |
|------|------|------|
| 地图引擎 | ECharts 6.1.0 | 渲染中国地图 |
| 地图数据 | 本地 GeoJSON | `frontend/src/assets/maps/china.json`，从 DataV.GeoAtlas 获取 |
| 数据加载 | 本地 `import` | 不依赖在线 CDN |
| 省份名称归一化 | `@/utils/province.ts` | `normalizeProvinceName` / `toMapProvinceName` |

### 当前不使用

- 高德地图 JS API
- 百度地图 JS API
- Mapbox GL JS
- MapLibre GL JS
- 任何商业地图 SDK

### 地图数据来源说明

地图 GeoJSON 数据需在正式上线前确认使用授权。

---

## 版本锁定规范

1. `package.json` 中所有依赖必须使用精确版本（不允许 `^`、`~`、`latest`）
2. `requirements.txt` 中所有依赖必须使用精确版本（不允许 `latest`）
3. `pnpm-lock.yaml` 必须提交到版本控制
4. 后续依赖升级必须先说明原因，经确认后再修改版本
5. 不允许随意更换技术栈中的核心框架或库
6. `frontend/.nvmrc` 和 `frontend/.npmrc` 用于强制 Node.js 和 pnpm 版本
7. `backend/.python-version` 用于指定 Python 版本