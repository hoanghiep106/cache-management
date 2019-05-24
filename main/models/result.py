from db import db


class ResultModel(db.Model):
    __tablename__ = 'result'

    id = db.Column(db.Integer(), primary_key=True)
    entry_id = db.Column(db.String(100), db.ForeignKey('entry.id'), nullable=False)
    data_path = db.Column(db.String(1024), nullable=False)
    page = db.Column(db.Integer(), nullable=False)

    def __init__(self, *args, **kwargs):
        super(ResultModel, self).__init__(*args, **kwargs)
