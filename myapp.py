import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Resource, Api, fields

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'blib.db')
api = Api(app, version='1.0', title='Book Library API',
          description='Just for test')
db = SQLAlchemy(app)


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
    author = db.relationship('Author',
                             backref=db.backref('books', lazy='dynamic'))

    def __repr__(self):
        return "<Book: {}>".format(self.title).capitalize()

ns = api.namespace('api', description='CRUD operations')

author = api.model('Author', {
    'id': fields.Integer(readOnly=True, description='Author unique id'),
    'first_name': fields.String(required=True, description='Author first name'),
    'last_name': fields.String(required=True, description='Author last name')
})


class AuthorDAO(object):
    def __init__(self):
        self.authors = Author.query.all()

    def get(self, id):
        a = Author.query.get(id)
        if a is not None:
            return a
        else:
            api.abort(404, "Author {} doesn't exist".format(id))

    def create(self, data):
        print(data)

ADAO = AuthorDAO()


@ns.route('/')
class AuthorList(Resource):
    @ns.marshal_with(author)
    def get(self):
        return ADAO.authors

    @ns.marshal_with(author, code=201)
    def post(self, data):
        return ADAO.create(data)


@ns.route('/author/<int:id>')
@ns.response(404, 'Author not found')
@ns.param('id', 'Author id')
class AuthorApi(Resource):
    @ns.marshal_with(author)
    def get(self, id):
        return ADAO.get(id)


if __name__ == '__main__':
    app.run(debug=True)
