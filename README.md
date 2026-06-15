# 全国高校地图查询系统

基于中国地图的全国高校查询与志愿辅助系统，支持地图筛选、学校库浏览、录取分数线查询、志愿冲稳保智能推荐。

## 技术栈

| 类别 | 核心技术 |
|------|----------|
| 前端 | Vue 3 + Vite + TypeScript + Element Plus + ECharts |
| 后端 | FastAPI + Python 3.12 + SQLAlchemy 2 |
| 数据库 | PostgreSQL 16 |
| 运行环境 | Node 20 / pnpm 10 · Python 3.12 |

详细版本基线见 [TECH_STACK.md](./TECH_STACK.md)。

## 已实现功能

### 地图查询（首页）

- ECharts 中国地图，省份颜色深浅表示高校数量
- 鼠标悬停省份展示本科 / 专科 / 985 / 211 统计 tooltip
- 点击省份联动右侧学校列表（点击「查看全国」恢复）
- 左侧多维度筛选面板：院校层次、985 / 211 / 双一流属性、办学性质、院校类型、省份
- 右侧学校列表：统计卡片 + 可滚动学校卡片
- 学校详情抽屉：基本信息、简介、热门专业、往年录取趋势图、地理位置
- 院校对比：最多选 4 所学校横向对比关键指标
- AI 问答助手（右下角悬浮按钮）：自然语言检索院校，结果可一键应用到筛选

### 学校库

- 全量院校列表，支持关键词搜索 + 多维筛选
- 分页浏览（每页条数可选），支持跳页
- 表格列可拖拽调整宽度，缩短某列时多余宽度自动分配给其余列
- 点击院校打开详情抽屉，支持加入对比

### 分数线查询

- 按生源省份、年份、科类（物理类 / 历史类 / 理科 / 文科）查询全国各院校录取最低分
- 最低分加粗蓝色高亮；估算位次通过一分一段表关联子查询实时计算
- 支持 985 / 211 / 双一流快捷筛选，支持关键词搜索
- 分页 + 可拖拽列宽表格，支持院校对比

### 志愿辅助

- 输入高考分数 + 省份 + 年份 + 科类，一键生成**冲一冲 / 稳一稳 / 保一保**三类推荐院校
- 算法：分数经一分一段表换算为全省位次，与院校历年最低录取位次对比
  - **冲**：院校录取位次优于考生，差距 < 30%
  - **稳**：考生位次优于录取线，余量 0–30%
  - **保**：考生位次优于录取线，余量 30%–150%
- 页面展示估算位次、各类院校数量、每所院校的位次差距（余量/差距）
- 支持点击院校打开详情抽屉、加入对比

## 目录结构

```
china-university-map/
├── frontend/
│   └── src/
│       ├── views/                  # 页面
│       │   ├── HomeMapView.vue     # 地图查询首页
│       │   ├── SchoolLibraryView.vue  # 学校库
│       │   ├── ScoreQueryView.vue  # 分数线查询
│       │   └── VolunteerView.vue   # 志愿辅助
│       ├── components/
│       │   ├── layout/             # AppHeader 导航
│       │   ├── school-map/         # 地图、筛选、学校卡片、详情抽屉
│       │   ├── compare/            # 院校对比浮动栏 + 对比抽屉
│       │   └── ai-assistant/       # AI 问答
│       ├── api/index.ts            # 统一请求层（自动 camelCase 转换）
│       ├── composables/            # useSchoolCompare、useSchoolData 等
│       ├── router/index.ts         # 路由（/、/schools、/scores、/volunteer）
│       ├── styles/                 # SCSS 变量 + 全局样式
│       └── assets/maps/china.json  # 本地 GeoJSON
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI 入口
│       ├── models/                 # SQLAlchemy ORM 模型
│       ├── schemas/                # Pydantic v2 响应模型
│       ├── routers/                # 路由：schools / filters / admission / volunteer / stats / majors
│       ├── services/               # 业务逻辑（含 score_rank_service 一分一段换算）
│       └── migrations/             # Alembic 迁移脚本
├── docker-compose.yml
├── TECH_STACK.md
└── README.md
```

## 启动方式

### 前端

```bash
cd frontend

# 启用 corepack 并准备 pnpm（首次）
corepack enable
corepack prepare pnpm@10.21.0 --activate

pnpm install
pnpm dev
# → http://localhost:5173
```

### 后端

```bash
cd backend

# 创建并激活虚拟环境
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

# 复制环境变量并填写数据库连接
cp .env.example .env   # 编辑 DATABASE_URL

uvicorn app.main:app --reload --port 8010
# → http://localhost:8010/api/health
```

### 数据库

项目使用 PostgreSQL，通过 Alembic 管理迁移：

```bash
cd backend
alembic upgrade head
```

## 地图说明

地图使用 ECharts 6 + 本地 GeoJSON（`frontend/src/assets/maps/china.json`）渲染，不依赖在线 CDN 或商业地图 SDK。若地图文件缺失，系统自动降级为省份卡片模式，核心筛选功能不受影响。

## 环境变量

后端通过 `backend/.env` 读取配置，参考 `backend/.env.example`：

```
DATABASE_URL=postgresql://user:password@localhost:5432/university_map
```

`.env` 文件已加入 `.gitignore`，不会被提交到仓库。
