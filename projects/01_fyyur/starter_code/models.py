from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500),nullable=True)
  genres = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120),nullable=True)
  website = db.Column(db.String(500),nullable=True)
  seeking_talent = db.Column(db.Boolean, default=False)
  show = db.relationship("Show", backref='Venue') 

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120),nullable=True)
  image_link = db.Column(db.String(500),nullable=True)
  website = db.Column(db.String(500),nullable=True)
  seeking_venue = db.Column(db.Boolean, default=False)
  show = db.relationship("Show", backref='Artist') # Pei added
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  # start_time = db.Column(db.DateTime, default=datetime.now(), nullable=False) # Pei: string?
  start_time = db.Column(db.DateTime, nullable=False) # Pei: string?