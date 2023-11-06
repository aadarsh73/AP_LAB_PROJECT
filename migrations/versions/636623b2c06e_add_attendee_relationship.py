"""Add attendee relationship

Revision ID: 636623b2c06e
Revises: 253f1e198859
Create Date: 2023-11-05 03:46:09.215751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '636623b2c06e'
down_revision = '253f1e198859'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('attendees',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'event_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('attendees')
    # ### end Alembic commands ###
