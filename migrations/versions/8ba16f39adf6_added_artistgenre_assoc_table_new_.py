"""added ArtistGenre assoc table, new Artist columns

Revision ID: 8ba16f39adf6
Revises: f56f904eb0ed
Create Date: 2021-05-28 10:48:53.449811

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '8ba16f39adf6'
down_revision = 'f56f904eb0ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    artistgenre = op.create_table('ArtistGenre',
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], ),
    sa.PrimaryKeyConstraint('genre_id', 'artist_id')
    )
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(), nullable=True))
    op.drop_column('Artist', 'genres')
    # ### end Alembic commands ###

    meta = sa.MetaData(bind=op.get_bind())
    meta.reflect(only=('Venue', 'VenueGenre', 'Artist', 'Show'))

    def tbl(name):
        return sa.Table(name, meta)

    jazz, reggae, swing, classical, folk, rocknroll, rnb, hiphop = range(1, 9)
    musicalhop, duelingpianos, parksquare = range(1, 4)
    gunsnpetals, matt, wildsax = range(1, 4)

    op.bulk_insert(tbl('Venue'), [{
        'name': "The Musical Hop",
        'address': "1015 Folsom Street",
        'city': "San Francisco",
        'state': "CA",
        'phone': "123-123-1234",
        'website': "https://www.themusicalhop.com",
        'facebook_link': "https://www.facebook.com/TheMusicalHop",
        'seeking_talent': True,
        'seeking_description': "We are on the lookout for a local artist to play every two weeks. Please call us.",
        'image_link': "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    }, {
        'name': "The Dueling Pianos Bar",
        'address': "335 Delancey Street",
        'city': "New York",
        'state': "NY",
        'phone': "914-003-1132",
        'website': "https://www.theduelingpianos.com",
        'facebook_link': "https://www.facebook.com/theduelingpianos",
        'seeking_talent': False,
        'seeking_description': None,
        'image_link': "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    }, {
        'name': "Park Square Live Music & Coffee",
        'address': "34 Whiskey Moore Ave",
        'city': "San Francisco",
        'state': "CA",
        'phone': "415-000-1234",
        'website': "https://www.parksquarelivemusicandcoffee.com",
        'facebook_link': "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        'seeking_talent': False,
        'seeking_description': None,
        'image_link': "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    }])

    venuegenres = {
        musicalhop: [jazz, reggae, swing, classical, folk],
        duelingpianos: [classical, rnb, hiphop],
        parksquare: [rocknroll, jazz, classical, folk]
    }
    op.bulk_insert(tbl('VenueGenre'), [
        {'venue_id': i, 'genre_id': g}
        for i, genres in venuegenres.items()
        for g in genres
    ])

    op.bulk_insert(tbl('Artist'), [{
        'name': "Guns N Petals",
        'city': "San Francisco",
        'state': "CA",
        'phone': "326-123-5000",
        'website': "https://www.gunsnpetalsband.com",
        'facebook_link': "https://www.facebook.com/GunsNPetals",
        'seeking_venue': True,
        'seeking_description': "Looking for shows to perform at in the San Francisco Bay Area!",
        'image_link': "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    }, {
        'name': "Matt Quevedo",
        'city': "New York",
        'state': "NY",
        'phone': "300-400-5000",
        'website': None,
        'facebook_link': "https://www.facebook.com/mattquevedo923251523",
        'seeking_venue': False,
        'seeking_description': None,
        'image_link': "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    }, {
        'name': "The Wild Sax Band",
        'city': "San Francisco",
        'state': "CA",
        'phone': "432-325-5432",
        'website': None,
        'facebook_link': None,
        'seeking_venue': False,
        'seeking_description': None,
        'image_link': "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    }])

    artistgenres = {
        gunsnpetals: [rocknroll],
        matt: [jazz],
        wildsax: [jazz, classical]
    }
    op.bulk_insert(artistgenre, [
        {'artist_id': i, 'genre_id': g}
        for i, genres in artistgenres.items()
        for g in genres
    ])

    op.bulk_insert(tbl('Show'), [{
        'venue_id': musicalhop,
        'artist_id': gunsnpetals,
        'start_time': datetime.fromisoformat("2019-05-21T21:30:00.000")
    }, {
        'venue_id': parksquare,
        'artist_id': matt,
        'start_time': datetime.fromisoformat("2019-06-15T23:00:00.000")
    }, {
        'venue_id': parksquare,
        'artist_id': wildsax,
        'start_time': datetime.fromisoformat("2035-04-01T20:00:00.000")
    }, {
        'venue_id': parksquare,
        'artist_id': wildsax,
        'start_time': datetime.fromisoformat("2035-04-08T20:00:00.000")
    }, {
        'venue_id': parksquare,
        'artist_id': wildsax,
        'start_time': datetime.fromisoformat("2035-04-15T20:00:00.000")
    }])



def downgrade():
    op.execute('delete from "Show" where id <= 5')
    op.execute('delete from "Artist" where id <= 3')
    op.execute('delete from "VenueGenre" where venue_id <= 3')
    op.execute('delete from "Venue" where id <= 3')

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'website')
    op.drop_table('ArtistGenre')
    # ### end Alembic commands ###
