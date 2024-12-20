"""md ready

Revision ID: 0928467fe1c5
Revises: 7d528b1c979c
Create Date: 2024-12-05 17:56:56.108609

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '0928467fe1c5'
down_revision: Union[str, None] = '7d528b1c979c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file_storage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('link_id', sa.Integer(), nullable=False),
    sa.Column('url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('extension', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('filename', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_file_storage_link_id'), 'file_storage', ['link_id'], unique=True)
    op.create_index(op.f('ix_file_storage_url'), 'file_storage', ['url'], unique=False)
    op.create_index(op.f('ix_child_parent_links_parent_id'), 'child_parent_links', ['parent_id'], unique=False)
    op.create_index(op.f('ix_image_links_status'), 'image_links', ['status'], unique=False)
    op.add_column('pdf_links', sa.Column('metadata_dict', sa.JSON(), nullable=True))
    op.add_column('pdf_links', sa.Column('referenced_links', sa.JSON(), nullable=True))
    op.add_column('pdf_links', sa.Column('referenced_images', sa.JSON(), nullable=True))
    op.add_column('pdf_links', sa.Column('md_text', sa.Text(), nullable=True))
    op.create_index(op.f('ix_pdf_links_status'), 'pdf_links', ['status'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_pdf_links_status'), table_name='pdf_links')
    op.drop_column('pdf_links', 'md_text')
    op.drop_column('pdf_links', 'referenced_images')
    op.drop_column('pdf_links', 'referenced_links')
    op.drop_column('pdf_links', 'metadata_dict')
    op.drop_index(op.f('ix_image_links_status'), table_name='image_links')
    op.drop_index(op.f('ix_child_parent_links_parent_id'), table_name='child_parent_links')
    op.drop_index(op.f('ix_file_storage_url'), table_name='file_storage')
    op.drop_index(op.f('ix_file_storage_link_id'), table_name='file_storage')
    op.drop_table('file_storage')
    # ### end Alembic commands ###
