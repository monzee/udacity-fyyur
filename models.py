from contextlib import contextmanager
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()

def init(app):
    db.init_app(app)
    return Migrate(app, db)


@contextmanager
def transaction():
  sess = db.session
  try:
    yield sess
    sess.commit()
  except:
    sess.rollback()
    raise
  finally:
    sess.close()


venue_genres = db.Table(
  'VenueGenre',
  db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
  db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
)

artist_genres = db.Table(
  'ArtistGenre',
  db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
  db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
)


class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    # probably should have made this the lone column actually
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<Genre {self.id}: {self.name}>'


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    genres = db.relationship('Genre', secondary=venue_genres)
    shows = db.relationship('Show', backref='venue')

    @property
    def upcoming_shows(self):
      return Show.upcoming(self.shows)

    @property
    def past_shows(self):
      return Show.past(self.shows)

    def __repr__(self):
        return f'<Venue {self.id}: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    genres = db.relationship('Genre', secondary=artist_genres)
    shows = db.relationship('Show', backref='artist')

    @property
    def upcoming_shows(self):
      return Show.upcoming(self.shows)

    @property
    def past_shows(self):
      return Show.past(self.shows)

    def __repr__(self):
        return f'<Artist {self.id}: {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'))
    start_time = db.Column(db.DateTime, index=True)

    @staticmethod
    def upcoming(shows):
      return [s for s in shows if s.start_time >= datetime.now()]

    @staticmethod
    def past(shows):
      return [s for s in shows if s.start_time < datetime.now()]

    def __repr__(self):
        return f'<Show {self.id}: {self.artist}@{self.venue}>'
