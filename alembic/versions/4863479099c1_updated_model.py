"""updated model

Revision ID: 4863479099c1
Revises: e03a536c02c5
Create Date: 2025-04-19 16:36:55.190092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4863479099c1'
down_revision: Union[str, None] = 'e03a536c02c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
