"""update post_id key to public_id in Posts Schema

Revision ID: dc01f2dc07bf
Revises: 
Create Date: 2025-11-09 13:18:00.288511

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc01f2dc07bf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add new nullable column
    op.add_column('posts', sa.Column('public_id', sa.UUID(), nullable=True))

    # 2. Copy values from old column to new column
    op.execute("UPDATE posts SET public_id = post_id")

    # 3. Make new column NOT NULL
    op.alter_column('posts', 'public_id', nullable=False)

    # 4. Drop old unique constraint (if exists)
    op.drop_constraint(op.f('posts_post_id_key'), 'posts', type_='unique')

    # 5. Add new unique constraint
    op.create_unique_constraint('posts_public_id_key', 'posts', ['public_id'])

    # 6. Drop old column
    op.drop_column('posts', 'post_id')


def downgrade() -> None:
    """Downgrade schema."""
    # Reverse steps for safety rollback
    op.add_column('posts', sa.Column('post_id', sa.UUID(), nullable=True))
    op.execute("UPDATE posts SET post_id = public_id")
    op.alter_column('posts', 'post_id', nullable=False)
    op.drop_constraint('posts_public_id_key', 'posts', type_='unique')
    op.create_unique_constraint('posts_post_id_key', 'posts', ['post_id'])
    op.drop_column('posts', 'public_id')
