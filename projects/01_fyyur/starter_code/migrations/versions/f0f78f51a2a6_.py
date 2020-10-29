"""empty message

Revision ID: f0f78f51a2a6
Revises: be07d45c7e06
Create Date: 2020-10-28 19:00:59.830125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0f78f51a2a6'
down_revision = 'be07d45c7e06'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('Venue', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('Artist', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
