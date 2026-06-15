"""import_batch columns + admission_scores dedup indexes + batch nullable

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-11

── 变更说明 ─────────────────────────────────────────────────────────────────

1. admission_scores.batch   NOT NULL → nullable
   原因：院校线源数据（school-index.json.gz / pro_type_min）不含批次信息，
         且库中约 50% 为专科院校，统一填"本科"会编造数据。
         NULL 诚实表达"批次未知"。
   已有行：均为空库，不存在 NULL 问题。

2. score_rank_tables.import_batch   String(50) nullable
   admission_scores.import_batch    String(50) nullable
   格式："{source}_{YYYYMMDD}"，例如 "eol_yfyd_20260611"、"gaokao_cn_20260611"。
   供后续数据后台追溯：查哪一批导入了哪些行、是否需要重跑。

3. 院校线幂等唯一索引（院校线 is_school_level=TRUE 专用）：
   uq_adm_school_matched
     UNIQUE (school_id, year, student_province, subject_type)
     WHERE school_id IS NOT NULL AND is_school_level
     → 用于已匹配到 schools 表的行；ON CONFLICT DO UPDATE 更新 min_score。

   uq_adm_school_unmatched
     UNIQUE (raw_school_code, year, student_province, subject_type)
     WHERE school_id IS NULL AND is_school_level
     → 用于未匹配行（school_id=NULL，raw_school_code 存源数据院校代码）。

── downgrade 限制 ───────────────────────────────────────────────────────────
  恢复 batch NOT NULL 前做 NULL 计数检查，存在 NULL 则主动报错。
"""
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # 1. batch 改可空
    op.alter_column("admission_scores", "batch", nullable=True)

    # 2. import_batch 列
    op.add_column(
        "score_rank_tables",
        sa.Column("import_batch", sa.String(50), nullable=True),
    )
    op.add_column(
        "admission_scores",
        sa.Column("import_batch", sa.String(50), nullable=True),
    )

    # 3. 院校线幂等索引（partial unique）
    op.create_index(
        "uq_adm_school_matched",
        "admission_scores",
        ["school_id", "year", "student_province", "subject_type"],
        unique=True,
        postgresql_where=text("school_id IS NOT NULL AND is_school_level"),
    )
    op.create_index(
        "uq_adm_school_unmatched",
        "admission_scores",
        ["raw_school_code", "year", "student_province", "subject_type"],
        unique=True,
        postgresql_where=text("school_id IS NULL AND is_school_level"),
    )


def downgrade() -> None:
    # 前置检查：batch NULL 值
    conn = op.get_bind()
    null_batch = conn.execute(
        text("SELECT COUNT(*) FROM admission_scores WHERE batch IS NULL")
    ).scalar() or 0
    if null_batch:
        raise RuntimeError(
            f"降级中止：admission_scores 中存在 {null_batch} 行 batch=NULL。\n"
            "请先填充后重试：UPDATE admission_scores SET batch='未知' WHERE batch IS NULL;"
        )

    op.drop_index("uq_adm_school_unmatched", table_name="admission_scores")
    op.drop_index("uq_adm_school_matched", table_name="admission_scores")
    op.drop_column("admission_scores", "import_batch")
    op.drop_column("score_rank_tables", "import_batch")
    op.alter_column("admission_scores", "batch", nullable=False)
