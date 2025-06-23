"""baseline

Revision ID: a9662790b5c4
Revises: 
Create Date: 2025-06-15 15:14:30.549203

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "a9662790b5c4"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
