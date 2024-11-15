"""Create scraped_page table

Revision ID: 27f6f4997933
Revises: 
Create Date: 2024-11-14 00:53:53.296467

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "27f6f4997933"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "scraped_pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sa.Enum("DISCOVERED", "PROCESSING", "COMPLETED", "FAILED", "REVISITED", name="pagestatusenum"), nullable=False),
        sa.Column("depth", sa.Integer(), nullable=False),
        sa.Column("cousin_urls_dict", sa.JSON(), nullable=True),
        sa.Column("response_status_code", sa.Integer(), nullable=True),
        sa.Column("response_text", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("response_body", sa.LargeBinary(), nullable=True),
        sa.Column("response_content_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("response_content_length", sa.Integer(), nullable=True),
        sa.Column("response_content_encoding", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("response_last_modified", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("response_date", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("response_metadata_lang", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("response_metadata_title", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("response_metadata_description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("response_metadata_keywords", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("response_metadata_content_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scraped_pages_url"), "scraped_pages", ["url"], unique=True)
    op.create_table(
        "child_parent_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=False),
        sa.Column("child_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["scraped_pages.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_child_parent_links_child_url"), "child_parent_links", ["child_url"], unique=False)
    op.create_table(
        "image_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("alt", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("status", sa.Enum("DISCOVERED", "PROCESSING", "FAILED", "DOWNLOADED", "PROCESSED", name="linkstatusenum"), nullable=False),
        sa.Column("scraped_page_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["scraped_page_id"],
            ["scraped_pages.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_image_links_url"), "image_links", ["url"], unique=False)
    op.create_table(
        "pdf_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scraped_page_id", sa.Integer(), nullable=False),
        sa.Column("url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("lang", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("status", sa.Enum("DISCOVERED", "PROCESSING", "FAILED", "DOWNLOADED", "PROCESSED", name="linkstatusenum"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["scraped_page_id"],
            ["scraped_pages.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pdf_links_url"), "pdf_links", ["url"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_pdf_links_url"), table_name="pdf_links")
    op.drop_table("pdf_links")
    op.drop_index(op.f("ix_image_links_url"), table_name="image_links")
    op.drop_table("image_links")
    op.drop_index(op.f("ix_child_parent_links_child_url"), table_name="child_parent_links")
    op.drop_table("child_parent_links")
    op.drop_index(op.f("ix_scraped_pages_url"), table_name="scraped_pages")
    op.drop_table("scraped_pages")
    # ### end Alembic commands ###
