"""测试 Wikipedia 院系段落 + Wikidata P527 子实体名称"""
import sys, io, os, re
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import requests
headers = {"User-Agent": "Mozilla/5.0 (compatible; UniversityMapBot/1.0)"}

# ── 1. Wikipedia 院系与师资 段落 wikitext ───────────────────────────────
r = requests.get(
    "https://zh.wikipedia.org/w/api.php?action=parse&page=北京大学"
    "&prop=wikitext&section=15&format=json",
    headers=headers, timeout=12
)
wikitext = r.json()["parse"]["wikitext"]["*"]
print("=== 院系与师资 wikitext ===")
print(wikitext[:2000])

# ── 2. 从 wikitext 提取学院名 ──────────────────────────────────────────
# [[北京大学XXX学院|XXX学院]] 或 [[北京大学XXX系|XXX系]]
colleges = re.findall(r'\[\[(?:[^\]|]*\|)?([^\]]+(?:学院|研究院|学部|研究所|系|学校))\]\]', wikitext)
print("\n提取到的学院/系:")
for c in sorted(set(colleges)):
    print(" ", c)

# ── 3. Wikidata P527 子实体 批量查名 ──────────────────────────────────
r2 = requests.get(
    "https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q16952"
    "&props=claims&format=json",
    headers=headers, timeout=15
)
qids_p527 = []
for c in r2.json()["entities"]["Q16952"]["claims"].get("P527", []):
    try:
        qids_p527.append(c["mainsnak"]["datavalue"]["value"]["id"])
    except Exception:
        pass

print(f"\nP527 子实体 QID 数量: {len(qids_p527)}")
# 批量查这些 QID 的中文标签
ids_str = "|".join(qids_p527[:20])
r3 = requests.get(
    f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={ids_str}"
    "&props=labels&languages=zh&format=json",
    headers=headers, timeout=15
)
for qid, ent in r3.json()["entities"].items():
    label = ent.get("labels", {}).get("zh", {}).get("value", "")
    if label:
        print(f"  {qid}: {label}")
