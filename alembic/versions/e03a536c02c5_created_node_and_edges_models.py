"""created node and edges models

Revision ID: e03a536c02c5
Revises: 3bfcad279aa5
Create Date: 2025-04-19 15:37:21.346088

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e03a536c02c5'
down_revision: Union[str, None] = '3bfcad279aa5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
