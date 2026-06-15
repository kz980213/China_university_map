"""initial schema: schools / majors / school_majors / admission_scores

Revision ID: 0001
Revises:
Create Date: 2026-06-10
"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table(
        "schools",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("english_name", sa.String(300), nullable=True),
        sa.Column("school_code", sa.String(20), nullable=False),
        sa.Column("province", sa.String(50), nullable=False),
        sa.Column("city", sa.String(50), nullable=False),
        sa.Column("district", sa.String(50), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("school_type", sa.String(20), nullable=False),
        sa.Column("ownership", sa.String(20), nullable=False),
        sa.Column("is_985", sa.Boolean(), nullable=False),
        sa.Column("is_211", sa.Boolean(), nullable=False),
        sa.Column("is_double_first_class", sa.Boolean(), nullable=False),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("admission_website", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("popular_majors", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("school_code"),
    )

    op.create_table(
        "majors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("discipline", sa.String(50), nullable=False),
        sa.Column("degree", sa.String(50), nullable=False),
        sa.Column("duration", sa.String(20), nullable=False),
        sa.Column("description", sa.String(2000), nullable=True),
        sa.Column("employment_direction", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "school_majors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("school_id", sa.Integer(), nullable=False),
        sa.Column("major_id", sa.Integer(), nullable=False),
        sa.Column("college_name", sa.String(200), nullable=False),
        sa.Column("tuition", sa.Integer(), nullable=True),
        sa.Column("duration", sa.String(20), nullable=False),
        sa.Column("subject_requirement", sa.String(100), nullable=True),
        sa.Column("is_national_first_class", sa.Boolean(), nullable=False),
        sa.Column("is_provincial_first_class", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.ForeignKeyConstraint(["major_id"], ["majors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "admission_scores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("school_id", sa.Integer(), nullable=False),
        sa.Column("major_id", sa.Integer(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("student_province", sa.String(50), nullable=False),
        sa.Column("subject_type", sa.String(20), nullable=False),
        sa.Column("batch", sa.String(50), nullable=False),
        sa.Column("major_name", sa.String(200), nullable=True),
        sa.Column("min_score", sa.Integer(), nullable=False),
        sa.Column("min_rank", sa.Integer(), nullable=False),
        sa.Column("avg_score", sa.Integer(), nullable=True),
        sa.Column("max_score", sa.Integer(), nullable=True),
        sa.Column("enrollment_count", sa.Integer(), nullable=True),
        sa.Column("remark", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.ForeignKeyConstraint(["major_id"], ["majors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("admission_scores")
    op.drop_table("school_majors")
    op.drop_table("majors")
    op.drop_table("schools")
