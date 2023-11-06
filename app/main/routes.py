from app import db
from app.models.events import Event
from app.forms.event_forms import EventForm
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from flask import Blueprint
import requests
from flask_wtf.csrf import generate_csrf
from datetime import datetime
main = Blueprint('main', __name__)

def is_organization(user):
    return user.role == 'organization'

def is_attendee(user):
    return user.role == 'attendee'

def get_geolocation_for_ip(ip_address):
    try:
        api_key='4fbb2b148ff24938883e90bb7011b8a2'
        response = requests.get(f'https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={ip_address}')
        response.raise_for_status()  # will raise an exception for 4XX/5XX errors
        return response.json()
    except requests.RequestException as e:
        print(e)
        return None

@main.route('/')
def index():
    all_events = Event.query.all()
    upcoming_events = []
    ongoing_events = []
    events = Event.query.all()
    if current_user.is_authenticated and current_user.role == 'attendee':
        all_attending_events = current_user.events_attending.order_by(Event.start_time.asc()).all()
        # Get current time
        now = datetime.utcnow()
        event_data = [{
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
        } for event in current_user.events_attending]
        # Filter events user is attending by upcoming and ongoing
        upcoming_events = current_user.events_attending.filter(Event.start_time > now).order_by(Event.start_time.asc()).all()
        ongoing_events = current_user.events_attending.filter(Event.start_time <= now, Event.end_time >= now).order_by(Event.start_time.asc()).all()
        return render_template('index.html', event_data=event_data, all_events=all_events, upcoming_events=upcoming_events, ongoing_events=ongoing_events)
    elif current_user.is_authenticated and current_user.role == 'organization':
        now = datetime.utcnow()
        event_data = [{
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
        } for event in Event.query.filter(Event.organizer_id == current_user.id)]
        # Filter events user is attending by upcoming and ongoing
        upcoming_events = Event.query.filter(
            Event.organizer_id == current_user.id,
            Event.start_time > now
        ).order_by(Event.start_time.asc()).all()
        ongoing_events = Event.query.filter(
            Event.organizer_id == current_user.id,
            Event.start_time <= now,
            Event.end_time >= now
        ).order_by(Event.start_time.asc()).all()
        return render_template('index.html', event_data=event_data, all_events=all_events, upcoming_events=upcoming_events, ongoing_events=ongoing_events)
    else:
        return render_template('index.html', events=events)


@main.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        # Combine date and time fields into datetime objects
        start_datetime = datetime.combine(form.start_date.data, form.start_time.data)
        end_datetime = datetime.combine(form.end_date.data, form.end_time.data)
        event = Event(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            start_time=start_datetime,
            end_time=end_datetime,
            organizer_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Your event has been created!', 'success')
        return redirect(url_for('main.index'))
    return render_template('create_event.html', form=form)

@main.route('/events/<city>')
@login_required
def events_by_city(city):
    user_is_attendee = is_attendee(current_user)
    events = Event.query.filter_by(location=city).all()
    return render_template('events_by_city.html', events=events, city=city, user_is_attendee=user_is_attendee)


@main.route('/events')
@login_required
def events():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_is_attendee = is_attendee(current_user)
    user_is_organization = is_organization(current_user)
    print(current_user, user_is_attendee, user_is_organization)
    default_city = 'manipal'
    # Skip geolocation in development for localhost IP
    if not user_is_organization and user_ip != "127.0.0.1":
        geo_data = get_geolocation_for_ip(user_ip)
        if geo_data and 'city' in geo_data:
            user_city = geo_data['city']
        else:
            flash('Could not determine your location. Defaulting to Manipal.', 'warning')
            user_city = default_city
    else:
        user_city = default_city

        # Filter events based on whether the user is an attendee or organization
    if user_is_organization:
        events = Event.query.filter_by(organizer_id=current_user.id).all()
    else:
        events = Event.query.filter_by(location=user_city).all()

        # Determine the status of each event
    for event in events:
        if event.start_time <= datetime.utcnow() <= event.end_time:
            event.status = 'Live'
        elif datetime.utcnow() < event.start_time:
            event.status = 'Coming Soon'
        else:
            event.status = 'Expired'
    csrf_token = generate_csrf()
    form = EventForm()
    return render_template('events_by_city.html', events=events, form=form, city=user_city, csrf_token=csrf_token, user_is_attendee=user_is_attendee)

@main.route('/attend_event/<int:event_id>', methods=['POST'])
@login_required
def attend_event(event_id):
    event = Event.query.get_or_404(event_id)
    already_attending = current_user in event.attendees

    if already_attending:
        event.attendees.remove(current_user)
        db.session.commit()
        flash('You are no longer attending this event.', 'info')
    else:
        event.attendees.append(current_user)
        db.session.commit()
        flash('You are now attending this event.', 'success')

    return redirect(request.referrer or url_for('main.events'))

