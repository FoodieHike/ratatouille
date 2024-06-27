"""first cerating tables

Revision ID: a5ee1c8228d9
Revises:
Create Date: 2024-06-03 18:37:28.217482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import HASHED_PASSWORD

# revision identifiers, used by Alembic.
revision: str = 'a5ee1c8228d9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def use_sql(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        commands = file.read().split(';')
    for command in commands:
        if command:
            op.execute(sa.text(command))


def upgrade() -> None:
    use_sql('up.sql')
    conn = op.get_bind()
    conn.execute(
        sa.text('''
            UPDATE users
            SET password = :password
            WHERE id = 1
        '''),
        {'password': HASHED_PASSWORD}
    )


def downgrade() -> None:
    use_sql('down.sql')
