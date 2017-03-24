from app import db


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))

    def __repr__(self):
        return "<Author: {} {}>".format(self.first_name, self.last_name).title()


class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    pub_date = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author', backref='books')

    def __repr__(self):
        return "<Book: {}>".format(self.title).capitalize()
