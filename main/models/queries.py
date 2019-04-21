from main.db import db
from main.models.base import TimestampMixin


class QueryModel(db.Model, TimestampMixin):
    __tablename__ = 'queries'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float(), nullable=False)
    longitude = db.Column(db.Float(), nullable=False)
    category = db.Column(db.String(105), nullable=True)
    result_path = db.Column(db.String(1024), nullable=False)

    def __init__(self, *args, **kwargs):
        super(QueryModel, self).__init__(*args, **kwargs)
