# 全国高校地图查询系统

基于中国地图的全国高校查询系统，支持学校筛选、详情查看及 AI 问答辅助查询。

## 当前阶段：第一阶段 MVP

第一阶段目标：前端 mock 可运行版本 + 后端基础骨架。不包含真实数据库、真实分数线、真实大模型、真实爬虫。

## 技术栈版本

详见 [TECH_STACK.md](./TECH_STACK.md)。

| 类别 | 核心技术 | 版本 |
|------|----------|------|
| 前端 | Vue 3 + Vite + TypeScript + Element Plus + ECharts | 见 TECH_STACK.md |
| 后端 | FastAPI + Python 3.12 | 见 TECH_STACK.md |
| 数据库 | PostgreSQL 16 + Redis 7（第二阶段启用） | 见 TECH_STACK.md |

## 目录结构

```
china-university-map/
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── main.ts         # 入口
│   │   ├── App.vue         # 根组件
│   │   ├── router/         # 路由
│   │   ├── views/          # 页面
│   │   ├── components/     # 组件
│   │   │   ├── layout/     # 布局组件
│   │   │   ├── school-map/ # 地图查询相关组件
│   │   │   └── ai-assistant/ # AI 问答组件
│   │   ├── mock/           # 模拟数据
│   │   ├── types/          # TypeScript 类型
│   │   ├── composables/    # 组合式函数
│   │   ├── utils/          # 工具函数（省份名称归一化等）
│   │   ├── assets/maps/    # 地图数据（china.json）
│   │   └── styles/         # 样式
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── .nvmrc
│   └── .npmrc
├── backend/                # 后端项目
│   ├── app/
│   │   ├── main.py         # FastAPI 入口
│   │   ├── config.py       # 配置
│   │   └── routers/        # 路由
│   ├── tests/              # 测试
│   ├── requirements.txt
│   └── .python-version
├── docs/                   # 文档预留
├── docker-compose.yml      # Docker 服务（第二阶段启用）
├── TECH_STACK.md           # 技术栈版本基线
└── README.md               # 项目说明
```

## 前端启动方式

```bash
cd frontend

# 启用 corepack 并准备 pnpm
corepack enable
corepack prepare pnpm@10.21.0 --activate

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

访问 http://localhost:5173

## 后端启动方式

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload
```

访问 http://localhost:8000/api/health 验证后端。

## 第一阶段功能边界

### 已实现功能

1. 首页地图查询页面（三栏布局）
2. 顶部导航栏（地图查询、学校库、分数线、志愿辅助）
3. 左侧筛选面板（院校层次、院校属性、办学性质、院校类型、地区筛选）
4. 中间 ECharts 中国地图展示（基于本地 GeoJSON，省份颜色深浅表示高校数量，hover tooltip 统计信息，点击省份联动右侧列表）
5. 右侧学校列表（统计卡片 + 学校卡片列表）
6. 学校详情抽屉（基本信息、简介、热门专业）
7. 前端 mock 学校数据（22+ 所学校）
8. 本地搜索和筛选（按名称、省份、城市、专业）
9. AI 问答助手（基于 mock 数据本地检索）
10. 后端 FastAPI 基础骨架和 /api/health 接口
11. 地图缺省降级方案（缺少 china.json 时自动切换为省份卡片模式）

### 第一阶段不做事项

1. 不做真实用户登录
2. 不做真实数据库连接
3. 不做真实高校数据爬虫
4. 不做真实录取分数线
5. 不接真实大模型 API
6. 不写任何 API Key
7. 不做 RAG
8. 不做志愿推荐算法
9. 不做移动端适配
10. 不接高德地图、百度地图等商业 SDK
11. 不使用在线 CDN 地图数据
12. 不做复杂后台管理系统
13. 不做 Docker 部署
14. 不做 CI/CD
15. 不做权限系统
16. 不要重构成过度复杂架构

## 验收标准

### 前端验收

1. `cd frontend` 后 `pnpm install` 成功
2. `pnpm dev` 可以启动
3. 首页能看到顶部导航、左侧筛选、中间地图区域、右侧学校列表
4. 搜索「南京」能筛出南京相关学校
5. 勾选 985 只显示 985 学校
6. 勾选本科只显示本科院校
7. 点击江苏省后只显示江苏学校
8. 点击南京大学卡片能打开学校详情抽屉
9. 点击重置按钮可以恢复全部学校
10. 右下角可以看到 AI 问答按钮
11. 点击 AI 问答按钮可以打开聊天抽屉
12. 点击「江苏有哪些985？」可以返回南京大学、东南大学
13. 输入「有哪些学校有计算机专业？」可以返回相关学校
14. 输入「南京大学在哪里？」可以返回南京大学省市和基础信息
15. AI 回答中的学校卡片点击后可以打开学校详情抽屉
16. 点击「应用到筛选条件」后，首页筛选和右侧列表同步更新
17. 鼠标悬停地图省份能看到高校统计 tooltip
18. 点击地图省份后右侧列表只显示该省学校
19. 点击「查看全国」恢复全国学校列表
20. 搜索功能正常
21. 左侧筛选功能正常
22. AI 问答助手正常
23. 浏览器控制台无明显运行时报错

### 后端验收

1. `cd backend` 后可以创建虚拟环境
2. `pip install -r requirements.txt` 成功
3. `uvicorn app.main:app --reload` 可以启动
4. `GET /api/health` 返回 200
5. `pytest` 可以执行并通过
6. 后端不依赖 PostgreSQL 也能启动

### 文档验收

1. README.md 存在
2. TECH_STACK.md 存在
3. TECH_STACK.md 中明确写了版本基线
4. package.json 中依赖版本全部为精确版本
5. requirements.txt 中依赖版本全部为精确版本
6. .nvmrc 存在
7. .npmrc 存在
8. .python-version 存在
9. pnpm-lock.yaml 存在

## 地图功能说明

### ECharts + 本地 GeoJSON

本项目使用 ECharts 6.1.0 渲染中国地图，地图数据来自本地 GeoJSON 文件。

**地图数据文件**：`frontend/src/assets/maps/china.json`

**数据来源**：从 DataV.GeoAtlas 下载（请确认正式上线前的使用授权）。

### 降级方案

如果 `china.json` 不存在或加载失败，系统会自动切换为省份卡片降级模式，所有核心功能（点击筛选、统计展示）不受影响。控制台会输出友好提示。

### 不使用在线 CDN / 商业 SDK

本项目不依赖在线 CDN 加载地图数据，也不使用高德、百度、Mapbox、MapLibre 等商业地图 SDK。

## 说明

当前前端 mock 页面不依赖 docker-compose。docker-compose 是为后续真实数据库阶段预留。