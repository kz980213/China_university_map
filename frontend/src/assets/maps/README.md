# 中国地图 GeoJSON 数据说明

## 文件

此目录用于放置中国地图 GeoJSON 数据文件：

- `china.json` — 中国地图 GeoJSON 数据

## 获取方式

china.json 需要从以下途径获取：

1. **DataV.GeoAtlas**：http://datav.aliyun.com/portal/school/atlas/area_selector
   - 选择「中国」→ 下载 GeoJSON

2. **其他 GeoJSON 数据源**（请确保数据来源合法合规）

## 文件要求

- 格式：GeoJSON
- 编码：UTF-8
- 坐标系：WGS-84（EPSG:4326）
- 必须包含中国所有省份的边界数据
- Feature 的 properties 中必须包含 `name` 字段

## 省份名称要求

GeoJSON 中的省份名称建议包含「省/市/自治区」后缀，如：
- 北京市
- 上海市
- 江苏省
- 广东省
- 内蒙古自治区

系统会自动通过 `normalizeProvinceName` 将地图名称映射到 mock 数据中的简称。

## 降级方案

如果 china.json 不存在或加载失败，系统会自动切换为省份卡片降级模式，展示省份按钮列表，所有核心功能（点击筛选、统计展示）不受影响。

控制台会输出：
```
当前未检测到本地中国地图 GeoJSON，已切换为省份卡片模式。
```

## 正式上线前

请确认 china.json 的数据来源和使用授权情况。