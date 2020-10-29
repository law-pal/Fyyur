import json
import dateutil.parser
import babel.dates
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
import datetime
import sys

import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


# Implemented Show, Venue and Artist models, and completed all model relationships and properties, as a database migration.
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False)
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)
    shows = db.relationship('Shows', backref='venue', lazy=True)

    def __repr__(self):
          return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)
    shows = db.relationship('Shows', backref='artist', lazy=True)

    def __repr__(self):
          return f'<Artist {self.id} {self.name}>'
    
class Shows(db.Model):
    __tablename__='Shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
          return f'<Shows {self.id}{self.artist_id}{self.venue_id}>'

db.create_all()


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


#  Created sqlalchemy querys for venues 
@app.route('/venues')
def venues():
  venues = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []

  for area in venues:
    area_of_venues = Venue.query.filter_by(city=area.city).filter_by(state=area.state).all()
    venue_data = []
    for venue in area_of_venues:
      venue_data.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(db.session.query(Shows).filter(Shows.venue_id == 3).filter(Shows.start_time > datetime.now()).all())
       })
    data.append({
        'city': area.city,
        'state': area.state,
        'venues': venue_data
        })
        
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  try:
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    data = []

    for result in venues:
      data.append({
        'id': result.id,
        'name': result.name,
        'num_upcoming_shows':  len(db.session.query(Shows).filter(Shows.venue_id == result.id).filter(Shows.start_time > datetime.now()).all())
      })

      response={
        'count': len(venues),
        'data': data
      }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  except:
    flash('An error occurred while searching, please try again')
    return redirect(url_for('venues'))


# Shows the venue page with the given venue_id
# Replaced with real venue data from the venues table, using venue_id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  get_past_shows = db.session.query(Shows).join(Artist).filter(venue_id == venue_id).filter(Shows.start_time < datetime.now()).all()
  past_shows = []

  get_upcoming_shows = db.session.query(Shows).join(Artist).filter(venue_id == venue_id).filter(Shows.start_time > datetime.now()).all()
  upcoming_shows = []

  for show in get_past_shows:
    past_shows.append({
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.isoformat(sep='T', timespec='auto')
    })

  for show in get_upcoming_shows:
    upcoming_shows.append({
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.isoformat(sep='T', timespec='auto')
    })

  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres.split(','),
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)


# Created Venues
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

# Inserted form data as a new Venue record in the db, instead
# Modified data to be the data object returned from db insertion
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  error = False

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  website = True if 'website' in request.form else False
  genres = request.form.getlist('genres')
  address = request.form['address']
  facebook_link = request.form['facebook_link']
  seeking_talent = True if 'seeking_talent' in request.form else False
  seeking_description = True if 'seeking_description' in request.form else False

  try:
    venue = Venue(name =name, city = city, state = state, phone = phone, website = website, genres = genres, address = address, facebook_link = facebook_link, seeking_talent = seeking_talent, seeking_description = seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error: flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:  flash('Venue ' + request.form['name'] + ' was successfully listed!')
 
  return render_template('pages/home.html')


# Completed this endpoint for taking a venue_id, and using
# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:  flash('An error occurred. Venue ' + {venue_id} + ' could not be deleted.')
  else:  flash('Venue ' + {venue_id} + ' was successfully deleted!')

  return render_template('pages/artists.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None

#  Artists
# Replaced with real data returned from querying the database  
@app.route('/artists')
def artists():
  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)


# Implemented search on artists with partial string search. Ensure it is case-insensitive.
@app.route('/artists/search', methods=['POST'])
def search_artists():
  try:
    search_term = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    data = []

    for result in artists:
      data.append({
        'id': result.id,
        'name': result.name,
        'num_upcoming_shows':  len(db.session.query(Shows).filter(Shows.artist_id == result.id).filter(Shows.start_time > datetime.now()).all())
      })

      response={
        'count': len(artists),
        'data': data
      }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  except:
    flash('An error occurred while searching, please try again')
    return redirect(url_for('artists'))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  get_past_shows = db.session.query(Shows).join(Venue).filter(artist_id == artist_id).filter(Shows.start_time < datetime.now()).all()
  past_shows = []

  get_upcoming_shows = db.session.query(Shows).join(Venue).filter(artist_id == artist_id).filter(Shows.start_time > datetime.now()).all()
  upcoming_shows = []

  for show in get_past_shows:
    past_shows.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time.isoformat(sep='T', timespec='auto')
    })

  for show in get_upcoming_shows:
    upcoming_shows.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time.isoformat(sep='T', timespec='auto')
    })

  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres.split(','),
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)


#  Update
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist:
      form.name = artist.name,
      form.genres = artist.genres,
      form.city = artist.city,
      form.state = artist.state,
      form.phone = artist.phone,
      form.website = artist.website,
      form.facebook_link = artist.facebook_link,
      form.seeking_venue = artist.seeking_venue,
      form.seeking_description = artist.seeking_description,
      form.image_link = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

 
# Populated form with fields from artist with ID <artist_id>
# Take values from the form submitted, and update existing
# artist record with ID <artist_id> using the new attributes
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
 
  error = False
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form['name']
    artist.genres = request.form['genres']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = request.form['seeking_venue']
    artist.seeking_description = request.form['seeking_description']
    artist.image_link = request.form['image_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Artist could not be changed.')
  if not error: 
    flash('Artist was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if venue:
      form.name = venue.name,
      form.genres = venue.genres,
      form.address = venue.address,
      form.city = venue.city,
      form.state = venue.state,
      form.phone = venue.phone,
      form.website = venue.website,
      form.facebook_link = venue.facebook_link,
      form.seeking_talent = venue.seeking_talent,
      form.seeking_description = venue.seeking_description,
      form.image_link = venue.image_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)


# Take values from the form submitted, and update existing
# venue record with ID <venue_id> using the new attributes
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']
    venue.genres = request.form['genres']
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.website = request.form['website']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_talent = request.form['seeking_talent']
    venue.seeking_description = request.form['seeking_description']
    venue.image_link = request.form['image_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Venue could not be changed.')
  if not error: 
    flash('Venue was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))


# Created Artist
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


# called upon submitting the new artist listing form
# Inserted form data as a new Venue record in the db, instead
# modified data to be the data object returned from db insertion
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  name = request.form['name']
  genres = request.form['genres']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  website = True if 'website' in request.form else False
  facebook_link = request.form['facebook_link']
  seeking_venue = True if 'seeking_venue' in request.form else False
  seeking_description = True if 'seeking_description' in request.form else False
  image_link = True if 'image_link' in request.form else False
  try:
    artist = Artist(name = name, genres = genres, city = city, state = state, phone = phone, website = website, facebook_link = facebook_link, seeking_venue = seeking_venue, seeking_description = seeking_description, image_link = image_link)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Artist' +  request.form['name'] + 'could not be listed')
  if not error: 
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


# Shows
# Displays list of shows at /shows
# num_shows should be aggregated based on number of upcoming shows per venue.
@app.route('/shows')
def shows():
  shows =  db.session.query(Shows).all()
  data = []

  for show in shows:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.isoformat(sep='T', timespec='auto')
    })
  return render_template('pages/shows.html', shows=data)
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


# Called to create new shows in the db, upon submitting new show listing for
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error =False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Shows(artist_id = artist_id, venue_id = venue_id, start_time = start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Show could not be listed')
  if not error: 
    flash('Show was successfully listed!')

  return render_template('pages/home.html')
 

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
