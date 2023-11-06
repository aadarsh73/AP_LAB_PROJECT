from app import db
from datetime import datetime

attendees = db.Table('attendees',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    organizer = db.relationship('User', backref='organized_events')
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(140), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    is_fundraiser = db.Column(db.Boolean, default=False, nullable=False)
    funds_raised = db.Column(db.Float, default=0.0, nullable=False)
    funds_goal = db.Column(db.Float, default=0.0, nullable=False)
    attendees = db.relationship('User', secondary=attendees, backref=db.backref('events_attending', lazy='dynamic'))

    def __repr__(self):
        return '<Event {}>'.format(self.title)
