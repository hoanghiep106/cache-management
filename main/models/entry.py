from db import db
from main.models.base import TimestampMixin


class EntryModel(db.Model, TimestampMixin):
    __tablename__ = 'entry'

    id = db.Column(db.String(100), unique=True, primary_key=True)
    latitude = db.Column(db.Float(), nullable=False)
    longitude = db.Column(db.Float(), nullable=False)
    radius = db.Column(db.Float(), nullable=False)
    categories = db.Column(db.String(105), nullable=True)
    total_used = db.Column(db.Integer(), nullable=False, default=0)
    last_used = db.Column(db.DateTime, nullable=True)

    def __init__(self, *args, **kwargs):
        super(EntryModel, self).__init__(*args, **kwargs)
