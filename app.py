#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from itertools import groupby
from sys import exc_info
from models import init, transaction, Artist, Genre, Show, Venue
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
migrate = init(app)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  orderedvenues = Venue.query.order_by(Venue.state, Venue.city)
  venuesbycity = groupby(orderedvenues, lambda v: (v.state, v.city))
  data = [{
    'city': city,
    'state': state,
    'venues': [{
      'id': v.id,
      'name': v.name,
      'num_upcoming_shows': len(v.upcoming_shows)
    } for v in venues]
  } for (state, city), venues in venuesbycity]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  term = request.form.get('search_term', '')
  found = Venue.query.filter(Venue.name.ilike(f'%{term}%')).all()
  response = {
    'count': len(found),
    'data': [{
      'id': v.id,
      'name': v.name,
      'num_upcoming_shows': len(v.upcoming_shows)
    } for v in found]
  }
  return render_template('pages/search_venues.html', results=response, search_term=term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  data = None if venue is None else {
    'id': venue.id,
    'name': venue.name,
    'genres': [g.name for g in venue.genres],
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': [{
      'artist_id': s.artist.id,
      'artist_name': s.artist.name,
      'artist_image_link': s.artist.image_link,
      'start_time': str(s.start_time)
    } for s in venue.past_shows],
    'upcoming_shows': [{
      'artist_id': s.artist_id,
      'artist_name': s.artist.name,
      'artist_image_link': s.artist.image_link,
      'start_time': str(s.start_time)
    } for s in venue.upcoming_shows],
    'past_shows_count': len(venue.past_shows),
    'upcoming_shows_count': len(venue.upcoming_shows),
  }
  return render_template(
    'pages/show_venue.html',
    venue=data,
    delete_url=url_for("delete_venue_from_the_90s", venue_id=venue.id)
  )

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  if not request.form['facebook_link']:
    # because the url validator fails if the value is an empty string (which
    # it will be if the submitted field is blank). it should be valid because
    # it is optional but i don't want to touch any code outside this file.
    form.facebook_link.validators = []
  try:
    if form.validate():
      with transaction() as sess:
        d = form.data
        d['genres'] = Genre.query.filter(Genre.name.in_(d['genres'])).all()
        d['website'] = d.pop('website_link')
        venue = Venue(**d)
        sess.add(venue)
        # on successful db insert, flash success
        flash(f'Venue {d["name"]} was successfully listed!')
        return redirect(url_for("index"))
    flash('Unable to create venue due to invalid data', 'error')
    for field, errors in _join_errors(form):
      flash(f'{field}: {errors}', 'error')
  except:
    flash('Unable to create venue due to a backend error', 'error')
    app.log_exception(exc_info())
  return render_template('forms/new_venue.html', form=form)


def _delete(id):
  with transaction() as sess:
    venue = Venue.query.get(id)
    if venue is None:
      return False, f'No such venue (id: {id})'
    sess.delete(venue)
    return True, venue.name

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    ok, error = _delete(venue_id)
    if ok:
      return jsonify({'ok': True})
    return jsonify({'ok': False, 'reason': error}), 404
  except:
    app.log_exception(exc_info())
    return jsonify({'ok': False, 'reason': 'Server error'}), 500

@app.route('/venues/without/<venue_id>', methods=['POST'])
def delete_venue_from_the_90s(venue_id):
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  ok, result = _delete(venue_id)
  if ok:
    flash(f'Venue {result} deleted')
    return redirect(url_for("index"))
  flash(f'Unable to delete venue: {result}', 'error')
  return redirect(url_for("show_venue", venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = [{'id': a.id, 'name': a.name} for a in Artist.query.all()]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  term = request.form.get('search_term', '')
  found = Artist.query.filter(Artist.name.ilike(f'%{term}%')).all()
  response = {
    'count': len(found),
    'data': [{
      'id': a.id,
      'name': a.name,
      'num_upcoming_shows': len(a.upcoming_shows)
    } for a in found]
  }
  return render_template('pages/search_artists.html', results=response, search_term=term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  a = Artist.query.get(artist_id)
  data = None if a is None else {
    'id': a.id,
    'name': a.name,
    'genres': [g.name for g in a.genres],
    'city': a.city,
    'state': a.state,
    'phone': a.phone,
    'website': a.website,
    'facebook_link': a.facebook_link,
    'seeking_venue': a.seeking_venue,
    'seeking_description': a.seeking_description,
    'image_link': a.image_link,
    'past_shows': [{
      'venue_id': s.venue.id,
      'venue_name': s.venue.name,
      'venue_image_link': s.venue.image_link,
      'start_time': str(s.start_time)
    } for s in a.past_shows],
    'upcoming_shows': [{
      'venue_id': s.venue.id,
      'venue_name': s.venue.name,
      'venue_image_link': s.venue.image_link,
      'start_time': str(s.start_time)
    } for s in a.upcoming_shows],
    'past_shows_count': len(a.past_shows),
    'upcoming_shows_count': len(a.upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  a = Artist.query.get(artist_id)
  artist = None if a is None else {
    'id': a.id,
    'name': a.name,
    'genres': [g.name for g in a.genres],
    'city': a.city,
    'state': a.state,
    'phone': a.phone,
    'website_link': a.website,
    'facebook_link': a.facebook_link,
    'seeking_venue': a.seeking_venue,
    'seeking_description': a.seeking_description,
    'image_link': a.image_link,
  }
  form = ArtistForm(data=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if not request.form['facebook_link']:
    form.facebook_link.validators = []
  try:
    if form.validate():
      del form.genres, form.website_link
      with transaction():
        form.populate_obj(artist)
        selected = request.form.getlist('genres')
        artist.genres = Genre.query.filter(Genre.name.in_(selected)).all()
        artist.website = request.form['website_link']
        flash(f'Updated info for artist {artist.name}')
        return redirect(url_for('show_artist', artist_id=artist_id))
    flash('Unable to update artist due to invalid data', 'error')
    for field, errors in _join_errors(form):
      flash(f'{field}: {errors}', 'error')
  except:
    flash('Unable to update artist due to a backend error', 'error')
    app.log_exception(exc_info())
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  v = Venue.query.get(venue_id)
  venue = None if v is None else {
    'id': v.id,
    'name': v.name,
    'genres': [g.name for g in v.genres],
    'address': v.address,
    'city': v.city,
    'state': v.state,
    'phone': v.phone,
    'website_link': v.website,
    'facebook_link': v.facebook_link,
    'seeking_talent': v.seeking_talent,
    'seeking_description': v.seeking_description,
    'image_link': v.image_link
  }
  form = VenueForm(data=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm()
  if not request.form['facebook_link']:
    form.facebook_link.validators = []
  try:
    if form.validate():
      del form.genres, form.website_link
      with transaction():
        form.populate_obj(venue)
        selected = request.form.getlist('genres')
        venue.genres = Genre.query.filter(Genre.name.in_(selected)).all()
        venue.website = request.form['website_link']
        flash(f'Updated info for venue {venue.name}')
        return redirect(url_for('show_venue', venue_id=venue_id))
    flash('Unable to update venue due to invalid data', 'error')
    for field, errors in _join_errors(form):
      flash(f'{field}: {errors}', 'error')
  except:
    flash('Unable to update venue due to a backend error', 'error')
    app.log_exception(exc_info())
  return render_template('forms/edit_venue.html', form=form, venue=venue)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  if not request.form['facebook_link']:
    form.facebook_link.validators = []
  if form.validate():
    with transaction() as sess:
      d = form.data
      d['genres'] = Genre.query.filter(Genre.name.in_(d['genres'])).all()
      d['website'] = d.pop('website_link')
      sess.add(Artist(**d))
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return redirect(url_for("index"))
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  flash('Unable to create artist due to invalid data', 'error')
  for field, errors in _join_errors(form):
    flash(f'{field}: {errors}', 'error')
  return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = [{
    'venue_id': s.venue.id,
    'venue_name': s.venue.name,
    'artist_id': s.artist.id,
    'artist_name': s.artist.name,
    'artist_image_link': s.artist.image_link,
    'start_time': str(s.start_time)
  } for s in Show.query.all()]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  try:
    if form.validate():
      # on successful db insert, flash success
      with transaction() as sess:
        d = form.data
        d['artist_id'] = int(d['artist_id'])
        d['venue_id'] = int(d['venue_id'])
        sess.add(Show(**d))
        flash('Show was successfully listed!')
        return redirect(url_for("index"))
    app.logger.info(form.data)
    flash('Unable to create show due to invalid data', 'error')
    for field, errors in _join_errors(form):
      flash(f'{field}: {errors}', 'error')
  except:
    flash('Unable to create show due to a backend error', 'error')
    app.log_exception(exc_info())
  return render_template('forms/new_show.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


def _join_errors(form):
  for field, errors in form.errors.items():
    yield field, '; '.join(errors)

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
