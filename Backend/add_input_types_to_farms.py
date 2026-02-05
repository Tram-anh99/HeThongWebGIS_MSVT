"""Add fertilizer and pesticide type FKs to farms

Revision ID: add_input_types_to_farms
Revises: 
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_input_types_to_farms'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add foreign key columns for fertilizer and pesticide types
    op.add_column('vung_trong', sa.Column('phan_bon_id', sa.Integer(), nullable=True))
    op.add_column('vung_trong', sa.Column('thuoc_bvtv_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraints
    op.create_foreign_key(
        'fk_vung_trong_phan_bon',
        '

vung_trong', 'phan_bon',
        ['phan_bon_id'], ['id']
    )
    op.create_foreign_key(
        'fk_vung_trong_thuoc_bvtv',
        'vung_trong', 'thuoc_bvtv',
        ['thuoc_bvtv_id'], ['id']
    )


def downgrade():
    op.drop_constraint('fk_vung_trong_thuoc_bvtv', 'vung_trong', type_='foreignkey')
    op.drop_constraint('fk_vung_trong_phan_bon', 'vung_trong', type_='foreignkey')
    op.drop_column('vung_trong', 'thuoc_bvtv_id')
    op.drop_column('vung_trong', 'phan_bon_id')
