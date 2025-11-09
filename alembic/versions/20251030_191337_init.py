
from alembic import op
import sqlalchemy as sa

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table('categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
    )
    op.create_table('bank_accounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bank_name', sa.String(100), nullable=False),
        sa.Column('external_id', sa.String(255), nullable=True),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
    )
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('posted_at', sa.DateTime(), nullable=False),
        sa.Column('amount', sa.Numeric(18,2), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('type', sa.String(10), nullable=False),
        sa.Column('mcc', sa.String(10), nullable=True),
        sa.Column('counterparty', sa.String(255), nullable=True),
        sa.Column('description_raw', sa.Text(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('category_confidence', sa.Numeric(5,2), nullable=True),
        sa.Column('is_business', sa.Boolean(), nullable=False),
        sa.Column('source', sa.String(10), nullable=False),
        sa.Column('hash_dedup', sa.String(64), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('transactions')
    op.drop_table('bank_accounts')
    op.drop_table('categories')
    op.drop_table('users')
