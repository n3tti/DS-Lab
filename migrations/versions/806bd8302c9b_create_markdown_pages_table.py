"""Create markdown_pages table

Revision ID: 806bd8302c9b
Revises: f9de45d2221c
Create Date: 2024-11-18 20:42:46.347897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '806bd8302c9b'
down_revision: Union[str, None] = 'f9de45d2221c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###