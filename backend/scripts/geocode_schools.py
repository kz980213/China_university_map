"""批量地理编码：用高德地图 Geocoding API 填充 schools 表的 longitude / latitude。

准备工作：
  1. 登录 https://lbs.amap.com/ → 控制台 → 应用管理 → 新建应用 → 添加 Key
     服务平台选"Web服务"，免费额度每日 30 万次、QPS 200，足以一次性跑完全部 2919 所。
  2. 将 Key 写入 backend/.env：
       AMAP_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  3. 在 backend/ 目录下运行：
       python scripts/geocode_schools.py            # 正式写库
       python scripts/geocode_schools.py --dry-run  # 仅打印，不写库
       python scripts/geocode_schools.py --all      # 重跑所有（含已有坐标的）

策略：
  - 默认只处理 longitude IS NULL 的学校（幂等，可断点续跑）
  - 查询参数：address=学校名称&city=城市，命中率通常 >95%
  - 第一次查询失败时，去掉 city 再试一次（覆盖"所在地"不精确的情况）
  - API 调用间隔 100ms（10 QPS），远低于免费 QPS 上限，避免限速
  - 失败学校汇总在末尾打印，不中断整体流程
"""

import argparse
import os
import sys
import time
from urllib.parse import urlencode
from urllib.request import urlopen
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from app.database import SessionLocal
from app.models.school import School

# ── 高德 Geocoding 接口 ────────────────────────────────────────────────────────
AMAP_GEO_URL = "https://restapi.amap.com/v3/geocode/geo"
REQUEST_INTERVAL = 0.12      # 每次请求后等待（秒），约 8 QPS
MAX_RETRIES = 3              # 单条网络错误重试次数


def get_api_key() -> str:
    key = os.environ.get("AMAP_API_KEY", "").strip()
    if not key:
        # 尝试从 .env 手动读取（不依赖 pydantic-settings）
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("AMAP_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not key:
        print("❌ 未找到 AMAP_API_KEY")
        print("   请在 backend/.env 中添加：AMAP_API_KEY=你的高德Web服务Key")
        print("   获取地址：https://lbs.amap.com/")
        sys.exit(1)
    return key


def geocode(address: str, city: str, api_key: str, with_city: bool = True) -> tuple[float, float] | None:
    """调用高德 Geocoding API，返回 (longitude, latitude) 或 None。"""
    params: dict = {"address": address, "key": api_key, "output": "json"}
    if with_city:
        params["city"] = city
    url = f"{AMAP_GEO_URL}?{urlencode(params)}"

    for attempt in range(MAX_RETRIES):
        try:
            with urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("status") == "1" and data.get("geocodes"):
                loc = data["geocodes"][0]["location"]   # "116.397499,39.908722"
                lng, lat = map(float, loc.split(","))
                return lng, lat
            return None
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                return None
            time.sleep(0.5)
    return None


def run(dry_run: bool = False, all_schools: bool = False) -> None:
    api_key = get_api_key()
    db = SessionLocal()

    try:
        stmt = select(School)
        if not all_schools:
            stmt = stmt.where(School.longitude.is_(None))
        stmt = stmt.order_by(School.id)
        schools = db.scalars(stmt).all()
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        db.close()
        sys.exit(1)

    total = len(schools)
    if total == 0:
        print("✓ 所有学校已有坐标，无需处理。")
        db.close()
        return

    print(f"待处理: {total} 所学校{'（dry-run 模式，不写库）' if dry_run else ''}")
    print("-" * 60)

    success = 0
    failed: list[tuple[str, str]] = []   # (school_code, name)

    for i, school in enumerate(schools, 1):
        # 第一次：带城市查
        result = geocode(school.name, school.city, api_key, with_city=True)
        time.sleep(REQUEST_INTERVAL)

        # 失败时去掉城市再试
        if result is None:
            result = geocode(school.name, school.city, api_key, with_city=False)
            time.sleep(REQUEST_INTERVAL)

        if result:
            lng, lat = result
            prefix = "[dry]" if dry_run else "✓"
            print(f"  [{i}/{total}] {prefix} {school.name:<30} {lng:.5f}, {lat:.5f}")
            if not dry_run:
                db.execute(
                    update(School)
                    .where(School.id == school.id)
                    .values(longitude=lng, latitude=lat)
                )
                # 每 50 条提交一次，减少事务持有时间
                if i % 50 == 0:
                    db.commit()
            success += 1
        else:
            print(f"  [{i}/{total}] ✗ {school.name} ({school.city}) — 未命中")
            failed.append((school.school_code, school.name))

    if not dry_run:
        db.commit()

    db.close()

    print()
    print("=" * 60)
    print(f"完成: {success}/{total} 成功")
    if failed:
        print(f"失败 {len(failed)} 所（可手动补充或重跑）：")
        for code, name in failed:
            print(f"  {code}  {name}")
    else:
        print("全部命中！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="高德地理编码批量脚本")
    parser.add_argument("--dry-run", action="store_true", help="只打印结果，不写入数据库")
    parser.add_argument("--all", action="store_true", help="重跑所有学校（含已有坐标的）")
    args = parser.parse_args()
    run(dry_run=args.dry_run, all_schools=args.__dict__["all"])
