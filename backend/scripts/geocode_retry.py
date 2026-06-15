"""对首次地理编码失败的学校进行多策略重试。

策略（依次尝试，命中即停）：
  1. 学校名 + 省份（去掉城市层级，避免城市名格式不匹配）
  2. 学校名（不带任何地理约束）
  3. 学校名去掉常见后缀后 + 省份（"河北软件职业技术学院" → "河北软件职业"）

运行：
  cd backend
  python scripts/geocode_retry.py
  python scripts/geocode_retry.py --dry-run
"""

import argparse
import os
import re
import sys
import time
from urllib.parse import urlencode
from urllib.request import urlopen
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from app.database import SessionLocal
from app.models.school import School

AMAP_GEO_URL = "https://restapi.amap.com/v3/geocode/geo"
REQUEST_INTERVAL = 0.15
MAX_RETRIES = 2

# 省份名到高德接受的简称映射（DB 可能存全称）
PROVINCE_NORMALIZE = {
    "内蒙古自治区": "内蒙古", "西藏自治区": "西藏",
    "新疆维吾尔自治区": "新疆", "宁夏回族自治区": "宁夏",
    "广西壮族自治区": "广西",
}

# 名称中常见的长后缀，去掉后用于第三策略
STRIP_SUFFIXES = ["职业技术学院", "职业学院", "技术学院", "职业大学"]


def get_api_key() -> str:
    key = os.environ.get("AMAP_API_KEY", "").strip()
    if not key:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("AMAP_API_KEY="):
                        key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not key:
        print("❌ 未找到 AMAP_API_KEY，请在 backend/.env 中设置")
        sys.exit(1)
    return key


def _call(address: str, city: str, api_key: str) -> tuple[float, float] | None:
    params = {"address": address, "key": api_key, "output": "json"}
    if city:
        params["city"] = city
    url = f"{AMAP_GEO_URL}?{urlencode(params)}"
    for _ in range(MAX_RETRIES):
        try:
            with urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("status") == "1" and data.get("geocodes"):
                lng, lat = map(float, data["geocodes"][0]["location"].split(","))
                return lng, lat
            return None
        except Exception:
            time.sleep(0.3)
    return None


def geocode_with_fallback(school: School, api_key: str) -> tuple[tuple[float, float] | None, str]:
    """返回 (坐标或None, 使用的策略描述)"""
    name = school.name
    province = PROVINCE_NORMALIZE.get(school.province, school.province).replace("省", "").replace("市", "")

    # 策略1：名称 + 省份
    r = _call(name, province, api_key)
    time.sleep(REQUEST_INTERVAL)
    if r:
        return r, f"省份={province}"

    # 策略2：仅名称
    r = _call(name, "", api_key)
    time.sleep(REQUEST_INTERVAL)
    if r:
        return r, "无地理约束"

    # 策略3：去后缀 + 省份
    short = name
    for suffix in STRIP_SUFFIXES:
        if suffix in name:
            short = name.replace(suffix, "")
            break
    if short != name:
        r = _call(short, province, api_key)
        time.sleep(REQUEST_INTERVAL)
        if r:
            return r, f"简化名={short}"

    return None, "全部策略失败"


def run(dry_run: bool = False) -> None:
    api_key = get_api_key()
    db = SessionLocal()

    try:
        schools = db.scalars(
            select(School).where(School.longitude.is_(None)).order_by(School.id)
        ).all()
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        db.close()
        sys.exit(1)

    total = len(schools)
    if total == 0:
        print("✓ 无待处理学校（longitude 均已填充）")
        db.close()
        return

    print(f"待重试: {total} 所{'（dry-run）' if dry_run else ''}")
    print("-" * 70)

    success, still_failed = 0, []

    for i, school in enumerate(schools, 1):
        result, strategy = geocode_with_fallback(school, api_key)
        if result:
            lng, lat = result
            tag = "[dry]" if dry_run else "✓"
            print(f"  [{i}/{total}] {tag} {school.name:<28} {lng:.5f},{lat:.5f}  [{strategy}]")
            if not dry_run:
                db.execute(
                    update(School).where(School.id == school.id).values(longitude=lng, latitude=lat)
                )
                if i % 30 == 0:
                    db.commit()
            success += 1
        else:
            print(f"  [{i}/{total}] ✗ {school.name} ({school.province} {school.city})")
            still_failed.append(school)

    if not dry_run:
        db.commit()
    db.close()

    print()
    print("=" * 70)
    print(f"重试结果: {success}/{total} 成功")
    if still_failed:
        print(f"\n仍失败 {len(still_failed)} 所，可手动填入坐标：")
        print("（在百度/高德地图搜索学校名，右键→复制坐标，或搜索结果 URL 中含经纬度）")
        print()
        for s in still_failed:
            print(f"  school_code={s.school_code}  {s.name}  ({s.province} {s.city})")
        if not dry_run:
            print()
            print("手动更新示例（在 backend/ 目录执行 python 进入交互式环境）：")
            print("  from app.database import SessionLocal")
            print("  from app.models.school import School")
            print("  from sqlalchemy import update")
            print("  db = SessionLocal()")
            print("  db.execute(update(School).where(School.school_code=='4111010040').values(longitude=116.3683, latitude=39.9275))")
            print("  db.commit()")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
