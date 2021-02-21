#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import app, db, Venue, Artist, Show

# app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  data = []

  for area in areas:
    result = Venue.query.filter(Venue.state == area.state).filter(Venue.city == area.city).all()
    venue_data = []
    for venue in result:
      venue_data.append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(db.session.query(Show).filter(Show.start_time > str(datetime.now())).all())
      })

    data.append({
        'city': area.city,
        'state': area.state,
        'venues': venue_data
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form['search_term']
  search_result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  for result in search_result:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == result.id).filter(Show.start_time > str(datetime.now())).all()),
    })
  
  response={
    "count": len(search_result),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.filter(Venue.id == venue_id).first()

  past = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
    Show.start_time < str(datetime.now())).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name, Artist.image_link, Show.start_time).all()

  upcoming = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
    Show.start_time > str(datetime.now())).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name, Artist.image_link, Show.start_time).all()

  upcoming_shows = []

  past_shows = []

  for i in upcoming:
    upcoming_shows.append({
      'artist_id': i[1],
      'artist_name': i[2],
      'image_link': i[3],
      'start_time': str(i[4])
    })

  for i in past:
    past_shows.append({
      'artist_id': i[1],
      'artist_name': i[2],
      'image_link': i[3],
      'start_time': str(i[4])
    })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": [venue.genres],
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  print(request.form['seeking_talent'])
  try:
    venue = Venue(
      name=request.form['name'], 
      city=request.form['city'], 
      state=request.form['state'], 
      address=request.form['address'], 
      phone=request.form['phone'], 
      image_link=request.form['image_link'], 
      genres=request.form['genres'], 
      facebook_link=request.form['facebook_link'],
      website=request.form['website'],
      seeking_talent = request.form['seeking_talent']=="True"
      )
    # print(venue.name)
    db.session.add(venue)
    db.session.commit()
    
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
    # abort(400)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  Venue.query.filter_by(id=venue_id).delete()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  count = len(results)
  data = []
  for result in results: # search each of the artist
    data.append({
      'id':result.id,
      'name':result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > str(datetime.now())).all()),
     })

  response = {
      "count": count,
      "data": data,
  } 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.filter(Artist.id == artist_id).first()

  past = db.session.query(Show).filter(Show.artist_id == artist_id).filter(
  Show.start_time < str(datetime.now())).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name, Venue.image_link, Show.start_time).all()

  upcoming = db.session.query(Show).filter(Show.artist_id == artist_id).filter(
    Show.start_time > str(datetime.now())).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name, Venue.image_link, Show.start_time).all()

  upcoming_shows = []

  past_shows = []

  for i in upcoming:
    upcoming_shows.append({
      'venue_id': i[1],
      'venue_name': i[2],
      'image_link': i[3],
      'start_time': str(i[4])
    })

  for i in past:
    past_shows.append({
      'venue_id': i[1],
      'venue_name': i[2],
      'image_link': i[3],
      'start_time': str(i[4])
    })

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": [artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = Artist.query.filter(Artist.id==artist_id).update({
    "name":request.form['name'],
    "city":request.form['city'], 
    "state":request.form['state'], 
    "phone":request.form['phone'], 
    "genres":request.form.getlist('genres'), 
    "image_link":request.form['image_link'],
    "seeking_venue":request.form['seeking_venue']=="True",
    "facebook_link":request.form['facebook_link'],
    "website":request.form['website'],
    })
  db.session.commit()
  db.session.close()
    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  try:
    artist = Artist(name=request.form['name'],
                    city=request.form['city'], 
                    state=request.form['state'], 
                    phone=request.form['phone'], 
                    genres=request.form.getlist('genres'), 
                    image_link=request.form['image_link'],
                    seeking_venue = request.form['seeking_venue']=="True",
                    facebook_link=request.form['facebook_link'],
                    website=request.form['website'],
                    )
    
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name']  + ' could not be listed.')
    # abort(400)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # num_shows should be aggregated based on number of upcoming shows per venue.
  response = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).all()

  data = []
  for show in response:
    venue_name = Venue.query.get(show.venue_id)
    artist_name = Artist.query.get(show.artist_id)
    artist_image_link = Artist.query.get(show.artist_id).image_link
    data.append({
        "venue_id": show.venue_id,
        "venue_name": venue_name,
        "artist_id": show.artist_id,
        "artist_name": artist_name,
        "artist_image_link": artist_image_link,
        "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  try:
    show = Show(
      artist_id=request.form['artist_id'], 
      venue_id=request.form['venue_id'], 
      start_time=request.form['start_time']
    )
    print(show)
    
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
    # abort(400)
  else:
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
