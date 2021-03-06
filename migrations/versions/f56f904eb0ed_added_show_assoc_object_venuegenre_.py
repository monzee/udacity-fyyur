"""added Show assoc object, VenueGenre assoc table, more Venue fields

Revision ID: f56f904eb0ed
Revises: 6d869df4ce7f
Create Date: 2021-05-28 09:33:57.240223

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f56f904eb0ed'
down_revision = '6d869df4ce7f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    genre = op.create_table('Genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('venue_id', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Show_start_time'), 'Show', ['start_time'], unique=False)
    op.create_table('VenueGenre',
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('genre_id', 'venue_id')
    )
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(), nullable=True))
    # ### end Alembic commands ###

    genres = "Jazz,Reggae,Swing,Classical,Folk,Rock n Roll,R&B,Hip-Hop,Alternative,Blues," \
        + "Country,Electronic,Funk,Heavy Metal,Instrumental,Musical Theatre,Pop,Punk,Soul,Other"
    op.bulk_insert(genre, [{'name': g} for g in genres.split(',')])


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'website')
    op.drop_table('VenueGenre')
    op.drop_index(op.f('ix_Show_start_time'), table_name='Show')
    op.drop_table('Show')
    op.drop_table('Genre')
    # ### end Alembic commands ###
