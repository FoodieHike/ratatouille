   """<%text>
   ${message}
   </%text>
   Revision ID: ${up_revision}
   Revises: ${down_revision}
   Create Date: ${create_date}

   """
   from alembic import op
   import sqlalchemy as sa
   import os
   from typing import Sequence, Union

   # revision identifiers, used by Alembic.
   revision: str = '${up_revision}'
   down_revision: Union[str, None] = ${repr(down_revision)}
   branch_labels: Union[str, Sequence[str], None] = None
   depends_on: Union[str, Sequence[str], None] = None

   def use_sql(filename):
       with open(os.path.join(os.path.dirname(__file__), filename)) as file:
           commands = file.read().split(';')
       for command in commands:
           if command.strip():
               op.execute(sa.text(command.strip()))

   def upgrade() -> None:
       use_sql('up.sql')

   def downgrade() -> None:
       use_sql('down.sql')
   