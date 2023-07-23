# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


artist_genre = db.Table('artist_genre', db.Column('genre_id', db.Integer, db.ForeignKey(
    'Genre.id'), primary_key=True), db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True))

venue_genre = db.Table('venue_genre', db.Column('genre_id', db.Integer, db.ForeignKey(
    'Genre.id'), primary_key=True), db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True))


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_Link = db.Column(db.String(120))
    seeking_Description = db.Column(db.String(500))
    genres = db.relationship(
        "Genre", secondary=venue_genre, backref=db.backref("venue"))
    talent = db.Column(db.Boolean, default=False)
    shows = db.relationship("Show", backref="venue", lazy=True)

    def __repr__(self):
        return f'<id= {self.id} name={self.name} city={self.city}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate (done)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_Link = db.Column(db.String(120))
    seeking_Description = db.Column(db.String(300))
    genres = db.relationship(
        "Genre", secondary=artist_genre, backref=db.backref("artist"))
    seeking_venue = db.Column(db.Boolean, default=False)
    shows = db.relationship("Show", backref="artist", lazy=True)

    def __repr__(self):
        return f'<id= {self.id} name={self.name} city={self.city}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate (done)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. (done)


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        "Artist.id"), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<id= {self.id} venue_id={self.venue_id} artist_id={self.artist_id}>'

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # TODO: replace with real venues data. (done)
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venues_locations = Venue.query.distinct(Venue.city, Venue.state).all()
    lists = []
    for location in venues_locations:
        venues = Venue.query.filter_by(
            city=location.city, state=location.state).all()
        list = {
            'city': location.city,
            'state': location.state,
            'venues': venues
        }
        lists.append(list)

    return render_template('pages/venues.html', areas=lists)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. (done)
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search}%')).all()
    results = []
    for result in venues:
        venue = {
            "id": result.id,
            "name": result.name
        }
        results.append(venue)

    response = {
        "count": len(venues),
        "data": results
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id (done)
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    past_shows = []
    upcoming_shows = []
    for show in venue.shows:

        show_data = {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': format_datetime(str(show.start_date))
        }
        if show.start_date < datetime.now():
            past_shows.append(show_data)
        else:
            upcoming_shows.append(show_data)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": [gener.name for gener in venue.genres],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_Link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.talent,
        "seeking_description": venue.seeking_Description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = VenueForm(request.form)
    if form.validate():
        try:
            new_Venue = Venue(name=form.name.data,
                              city=form.city.data,
                              state=form.state.data,
                              address=form.address.data,
                              phone=form.phone.data,
                              image_link=form.image_link.data,
                              facebook_link=form.facebook_link.data,
                              website_Link=form.website_link.data,
                              seeking_Description=form.seeking_description.data,
                              talent=form.seeking_talent.data)

            geners = form.genres.data
            for gener_id in geners:
                data = Genre.query.get(gener_id)
                new_Venue.genres.append(data)

            db.session.add(new_Venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        except:
            print(sys.exc_info())
            db.session.rollback()
            flash('An error occurred. Venue ' +
                  request.form['name'] + "could not be listed.")
        finally:
            db.session.close()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'error in {field}: {error}', 'error')
     # TODO: on unsuccessful db insert, flash an error instead.
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    try:
        db.session.query(venue_genre).filter_by(venue_id=venue_id).delete()
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue was successfully deleted!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue could not be deleted.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database (done)
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
# TODO: implement search on artists with partial string search. Ensure it is case-insensitive. (done)
# seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
# search for "band" should return "The Wild Sax Band".
def search_artists():
    search = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search}%')).all()
    results = []
    for result in artists:
        artist = {
            "id": result.id,
            "name": result.name
        }
        results.append(artist)

    response = {
        "count": len(artists),
        "data": results
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    past_shows = []
    upcoming_shows = []
    for show in artist.shows:

        show_data = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': format_datetime(str(show.start_date))
        }
        if show.start_date < datetime.now():
            past_shows.append(show_data)
        else:
            upcoming_shows.append(show_data)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": [gener.name for gener in artist.genres],
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_Link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_Description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website_Link
    form.seeking_description.data = artist.seeking_Description
    form.seeking_venue.data = artist.seeking_venue
    form.genres.data = artist.genres
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    try:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.website_Link = form.website_link.data
        artist.seeking_Description = form.seeking_description.data
        artist.seeking_venue = form.seeking_venue.data

        artist.genres.clear()  # clear old genres
        genres = form.genres.data
        for genre_id in genres:
            data = Genre.query.get(genre_id)
            artist.genres.append(data)
        db.session.commit()
        flash('DONE!')
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website_Link
    form.seeking_description.data = venue.seeking_Description
    form.seeking_talent.data = venue.talent
    form.genres.data = venue.genres
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    try:
        venue.name = form.name.data
        venue.city = form.city.data,
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.address = form.address.data
        venue.image_link = form.image_link.data
        venue.facebook_link = form.facebook_link.data
        venue.website_Link = form.website_link.data
        venue.seeking_Description = form.seeking_description.data
        venue.talent = form.seeking_talent.data

        venue.genres.clear()  # clear old genres
        genres = form.genres.data
        for genre_id in genres:
            data = Genre.query.get(genre_id)
            venue.genres.append(data)
        db.session.commit()
        flash('DONE!')
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred.')
    finally:
        db.session.close()

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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    if form.validate():
        try:
            new_artist = Artist(name=form.name.data,
                                city=form.city.data,
                                state=form.state.data,
                                phone=form.phone.data,
                                image_link=form.image_link.data,
                                facebook_link=form.facebook_link.data,
                                website_Link=form.website_link.data,
                                seeking_Description=form.seeking_description.data,
                                seeking_venue=form.seeking_venue.data)

            geners = form.genres.data
            for gener_id in geners:
                data = Genre.query.get(gener_id)
                new_artist.genres.append(data)

            db.session.add(new_artist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        except:
            print(sys.exc_info())
            db.session.rollback()
            # on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' +
                  request.form['name'] + " could not be listed.")
        finally:
            db.session.close()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'error in {field}: {error}', 'error')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data. (done)
    shows = Show.query.all()
    data = []
    for show in shows:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)

        show_data = {
            'venue_id': show.venue_id,
            'artist_id': show.artist_id,
            'venue_name': venue.name,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': format_datetime(str(show.start_date))
        }
        data.append(show_data)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)
    if form.validate():
        try:
            new_show = Show(venue_id=form.venue_id.data,
                            artist_id=form.artist_id.data, start_date=form.start_time.data)
            db.session.add(new_show)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!')
        except:
            # unsuccessful db insert, flash an error instead.
            print(sys.exc_info())
            db.session.rollback()
            flash('An error occurred. Show could not be listed.')
        finally:
            db.session.close()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'error in {field}: {error}', 'error')
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
