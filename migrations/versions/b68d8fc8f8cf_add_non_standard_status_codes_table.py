"""Add non_standard_status_codes table

Revision ID: b68d8fc8f8cf
Revises: 553005ad347e
Create Date: 2024-11-21 17:30:23.792473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b68d8fc8f8cf'
down_revision: Union[str, None] = '553005ad347e'
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
