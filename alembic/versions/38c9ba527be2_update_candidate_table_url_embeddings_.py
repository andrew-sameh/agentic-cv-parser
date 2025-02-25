"""update candidate table, url, embeddings namespace

Revision ID: 38c9ba527be2
Revises: cbadba36e1b1
Create Date: 2025-02-25 17:34:54.425884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38c9ba527be2'
down_revision: Union[str, None] = 'cbadba36e1b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('candidates', sa.Column('resume_url', sa.String(length=100), nullable=True))
    op.add_column('candidates', sa.Column('embeddings_namespace', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_candidates_embeddings_namespace'), 'candidates', ['embeddings_namespace'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_candidates_embeddings_namespace'), table_name='candidates')
    op.drop_column('candidates', 'embeddings_namespace')
    op.drop_column('candidates', 'resume_url')
    # ### end Alembic commands ###
