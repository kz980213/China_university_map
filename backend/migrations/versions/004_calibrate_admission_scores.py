"""calibrate admission_scores: nullable school_id/min_rank + raw/meta columns

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-10

── 变更说明 ─────────────────────────────────────────────────────────────────

1. school_id   NOT NULL → nullable
   原因：约 7.5% 的行无法精确匹配到 schools 表（raw_school_name 保留原始文本）。

   JOIN / 查询行为：
     SQL NULL ≠ 任何值，因此：
     • INNER JOIN schools ON admission_scores.school_id = schools.id
       → NULL 行自动被排除，不影响已匹配行的结果。
     • 学校详情接口（WHERE school_id = :sid）同理：
       孤儿行（school_id=NULL）天然不出现在该学校的分数线列表。
     • 孤儿行通过 match_status='unmatched' 或 raw_school_name 单独查询，
       用于后台审计与二次匹配，不干扰线上展示逻辑。

2. min_rank    NOT NULL → nullable
   原因：部分数据源（早期年份、特殊批次）缺失位次字段。

3. 新增原始文本列（用于导入审计和二次匹配）：
   raw_school_name  String(200)  —— 数据源原始院校名称
   raw_school_code  String(20)   —— 数据源原始院校代码
   raw_major_name   String(200)  —— 数据源原始专业名称
   raw_major_code   String(20)   —— 数据源原始专业代码

4. 新增录取附加信息列：
   admission_group   String(20)   —— 招生组（部分省份院校线也有，故不加约束）
   score_subject_req String(100)  —— 选考科目要求（专业级字段，院校线不应存在）

5. 新增匹配元数据列：

   is_school_level  Boolean NOT NULL
     True  = 院校线（批次控制线，不与具体专业绑定）
     False = 专业线（某专业的录取线）
     ⚠️  NOT NULL：is_school_level 是唯一真相源，不允许为空。
         源数据在结构上可以在入库时区分院校线与专业线（两者来自不同表/字段集），
         无需两步填写。Migration 以 server_default=false() 处理存量行后立即
         DROP server_default，确保新 INSERT 必须显式传值（不传 → DB 报错）。
         major_id IS NULL 不能用于推断 is_school_level：未匹配的专业线同样
         有 major_id=NULL。

   match_status     String(20)  "matched" | "partial" | "unmatched"

   ❗ CHECK 约束 ck_school_level_no_major_fields：
      当 is_school_level=TRUE 时，以下专业级字段必须全为 NULL：
        major_id, major_name, raw_major_name, raw_major_code, score_subject_req
      admission_group 不受约束（部分省份院校线确有招生组编号）。
      表达式：
        NOT is_school_level OR (
          major_id IS NULL AND major_name IS NULL AND
          raw_major_name IS NULL AND raw_major_code IS NULL AND
          score_subject_req IS NULL
        )

── downgrade 限制 ───────────────────────────────────────────────────────────
  恢复 school_id / min_rank 的 NOT NULL 前做运行时计数检查；
  若存在 NULL 值则主动抛出 RuntimeError 并提示清理 SQL，
  不让 PostgreSQL 报出晦涩的 constraint violation。
"""
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # 1. 放开 school_id 的 NOT NULL 约束
    op.alter_column("admission_scores", "school_id", nullable=True)

    # 2. 放开 min_rank 的 NOT NULL 约束
    op.alter_column("admission_scores", "min_rank", nullable=True)

    # 3. 原始文本列
    op.add_column("admission_scores", sa.Column("raw_school_name", sa.String(200), nullable=True))
    op.add_column("admission_scores", sa.Column("raw_school_code", sa.String(20), nullable=True))
    op.add_column("admission_scores", sa.Column("raw_major_name", sa.String(200), nullable=True))
    op.add_column("admission_scores", sa.Column("raw_major_code", sa.String(20), nullable=True))

    # 4. 录取附加信息列
    op.add_column("admission_scores", sa.Column("admission_group", sa.String(20), nullable=True))
    op.add_column("admission_scores", sa.Column("score_subject_req", sa.String(100), nullable=True))

    # 5a. is_school_level：NOT NULL，用 server_default 安全填充存量行
    op.add_column(
        "admission_scores",
        sa.Column(
            "is_school_level",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),  # 存量行默认 False（专业线）
        ),
    )
    # 删除 server_default：之后 INSERT 必须显式传值，不得依赖默认值
    op.alter_column("admission_scores", "is_school_level", server_default=None)

    # 5b. match_status
    op.add_column("admission_scores", sa.Column("match_status", sa.String(20), nullable=True))

    # 6. CHECK：院校线不携带任何专业级字段
    #    admission_group 不在约束内（部分省份院校线确有招生组编号）
    op.create_check_constraint(
        "ck_school_level_no_major_fields",
        "admission_scores",
        (
            "NOT is_school_level OR ("
            "major_id IS NULL AND major_name IS NULL AND "
            "raw_major_name IS NULL AND raw_major_code IS NULL AND "
            "score_subject_req IS NULL"
            ")"
        ),
    )


def downgrade() -> None:
    # 前置检查：存量 NULL 会导致恢复 NOT NULL 失败，提前报错并给出清理语句
    conn = op.get_bind()
    null_school = conn.execute(
        text("SELECT COUNT(*) FROM admission_scores WHERE school_id IS NULL")
    ).scalar() or 0
    null_rank = conn.execute(
        text("SELECT COUNT(*) FROM admission_scores WHERE min_rank IS NULL")
    ).scalar() or 0
    if null_school or null_rank:
        raise RuntimeError(
            f"降级中止：admission_scores 中存在 {null_school} 行 school_id=NULL、"
            f"{null_rank} 行 min_rank=NULL。\n"
            "请先执行以下语句清理后再重试 downgrade：\n"
            "  UPDATE admission_scores SET school_id = <默认 id> WHERE school_id IS NULL;\n"
            "  DELETE FROM admission_scores WHERE min_rank IS NULL;\n"
            "  -- 或 UPDATE admission_scores SET min_rank = 0 WHERE min_rank IS NULL;"
        )

    op.drop_constraint("ck_school_level_no_major_fields", "admission_scores", type_="check")

    op.drop_column("admission_scores", "match_status")
    op.drop_column("admission_scores", "is_school_level")
    op.drop_column("admission_scores", "score_subject_req")
    op.drop_column("admission_scores", "admission_group")
    op.drop_column("admission_scores", "raw_major_code")
    op.drop_column("admission_scores", "raw_major_name")
    op.drop_column("admission_scores", "raw_school_code")
    op.drop_column("admission_scores", "raw_school_name")

    op.alter_column("admission_scores", "min_rank", nullable=False)
    op.alter_column("admission_scores", "school_id", nullable=False)
