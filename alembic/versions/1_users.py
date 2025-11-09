from alembic import op
import sqlalchemy as sa

revision = '0002_users_profiles_settings'
down_revision = '0001_init'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('user_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('phone', sa.String(32)),
        sa.Column('company_name', sa.String(255)),
        sa.Column('inn', sa.String(12)),
        sa.Column('kpp', sa.String(9)),
        sa.Column('country', sa.String(64)),
        sa.Column('city', sa.String(64)),
        sa.Column('address_line', sa.String(255)),
        sa.Column('postal_code', sa.String(20)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'])

    op.create_table('user_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('notify_email', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notify_push', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('spike_pct', sa.String(16), nullable=False, server_default='0.3'),
        sa.Column('recurring_delta_pct', sa.String(16), nullable=False, server_default='0.1'),
        sa.Column('big_expense_threshold', sa.String(32), nullable=False, server_default='100000'),
        sa.Column('low_balance_days', sa.String(16), nullable=False, server_default='7'),
        sa.Column('min_tax_reserve_pct', sa.String(16), nullable=False, server_default='0.06'),
        sa.Column('preferences', sa.dialects.postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_user_settings_user_id', 'user_settings', ['user_id'])

def downgrade() -> None:
    op.drop_table('user_settings')
    op.drop_table('user_profiles')
