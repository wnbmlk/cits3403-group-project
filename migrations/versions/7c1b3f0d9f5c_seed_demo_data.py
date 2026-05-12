"""seed demo data

Revision ID: 7c1b3f0d9f5c
Revises: 2d44a4220600
Create Date: 2026-05-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

from seed_demo_data import seed_demo_data


# revision identifiers, used by Alembic.
revision = '7c1b3f0d9f5c'
down_revision = '2d44a4220600'
branch_labels = None
depends_on = None


def _table_columns(connection, table_name):
    inspector = inspect(connection)
    if table_name not in inspector.get_table_names():
        return set()

    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade():
    connection = op.get_bind()
    movie_columns = _table_columns(connection, "movie")
    diary_columns = _table_columns(connection, "diary_entry")

    if movie_columns:
        if "media_type" not in movie_columns:
            op.add_column("movie", sa.Column("media_type", sa.String(length=50), nullable=True))
        if "status" not in movie_columns:
            op.add_column("movie", sa.Column("status", sa.String(length=50), nullable=True))
        if "poster_path" not in movie_columns:
            op.add_column("movie", sa.Column("poster_path", sa.String(length=255), nullable=True))

    if diary_columns:
        if "media_type" not in diary_columns:
            op.add_column("diary_entry", sa.Column("media_type", sa.String(length=50), nullable=True))
        if "poster_path" not in diary_columns:
            op.add_column("diary_entry", sa.Column("poster_path", sa.String(length=255), nullable=True))
        if "date_watched_end" not in diary_columns:
            op.add_column("diary_entry", sa.Column("date_watched_end", sa.DateTime(), nullable=True))

    seed_demo_data(generate_posters=True)


def downgrade():
    pass