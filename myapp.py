import os
from datetime import datetime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Resource, Api, fields

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'blib.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app, version='1.0', title='Book Library API',
          description='Just for test')
db = SQLAlchemy(app)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))

    def __repr__(self):
        return "<Author %r>" % self.first_name


class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    pub_date = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author',
                             backref=db.backref('books', lazy='dynamic'))

    def __init__(self, title, athr, pub_date=None):
        self.title = title
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.author = athr

    def __repr__(self):
        return "<Book %r>" % self.title


author = api.model('The Author', {
    'id': fields.Integer(readOnly=True, description='Author unique id'),
    'first_name': fields.String(required=True, description='Author first name'),
    'last_name': fields.String(required=True, description='Author last name')
})

book = api.model('The Book', {
    'id': fields.Integer(readOnly=True, description='Book unique id'),
    'title': fields.String(required=True, description='Book title'),
    'pub_date': fields.DateTime,
    'author_id': fields.Integer(attribute='author.id'),
    'author': fields.String(attribute='author.id')
})

author_with_books = api.inherit('Author with books', author, {
    'books': fields.List(fields.Nested(book))
})


def create_book_item(data):
    title = data.get('title')
    pub_date = data.get('pub_date')
    author_id = data.get('author_id')
    the_author = Author.query.filter(Author.id == author_id).one()
    the_book = Books(title, the_author, pub_date)
    db.session.add(the_book)
    db.session.commit()


def delete_book_item(book_id):
    the_book = Books.query.filter(Books.id == book_id).one()
    db.session.delete(the_book)
    db.session.commit()


def update_book_item(book_id, data):
    the_book = Books.query.filter(Books.id == book_id).one()
    the_book.title = data.get('title')
    author_id = data.get('author_id')
    the_book.author = Author.query.filter(Author.id == author_id).one()
    db.session.add(the_book)
    db.session.commit()


ns = api.namespace('api', description='CRUD operations')


@ns.route('/')
class BookList(Resource):
    # @ns.marshal_with(author)
    # def get(self):
    #     return ADAO.authors

    @api.expect(book)
    def post(self):
        """
        Создаем книгу
        :return: зе бук
        """
        create_book_item(request.json)
        return None, 201


@ns.route('/book/<int:id>')
@ns.response(404, 'Book not found')
@ns.param('id', 'Book id')
class BookItem(Resource):
    @ns.marshal_with(book)
    def get(self, id):
        """
        Вернем книгу по айди
        :param id: айди книги
        :return: книга
        """
        return Books.query.filter(Books.id == id).one()

    @api.response(204, 'Book successfully deleted')
    def delete(self, id):
        """
        Удалим книгу по айди
        :param id: айди книги
        :return: 204 или ничего
        """
        delete_book_item(id)
        return None, 204

    @api.expect(book)
    @api.response(204, 'Book successfull updated')
    def put(self, id):
        """
        Обновляем книгу
        :param id: книги
        :return: ок
        """
        update_book_item(id, request.json)
        return None, 204


@ns.route('/author/<int:id>')
@ns.response(404, 'Author nor found')
@ns.param('id', 'Author id')
class AuthorItem(Resource):
    @api.marshal_with(author_with_books)
    def get(self, id):
        return Author.query.filter(Author.id == id).one()


if __name__ == '__main__':
    app.run(debug=True)
