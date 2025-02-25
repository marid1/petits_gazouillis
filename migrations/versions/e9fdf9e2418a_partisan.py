"""partisan

Revision ID: e9fdf9e2418a
Revises: 0cb6c0e784ec
Create Date: 2024-09-17 08:57:39.501737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9fdf9e2418a'
down_revision = '0cb6c0e784ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('partisans',
    sa.Column('partisan_id', sa.Integer(), nullable=True),
    sa.Column('utilisateur_qui_est_suivi_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['partisan_id'], ['utilisateur.id'], ),
    sa.ForeignKeyConstraint(['utilisateur_qui_est_suivi_id'], ['utilisateur.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('partisans')
    # ### end Alembic commands ###
