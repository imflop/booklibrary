import os
from datetime import datetime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Resource, Api, fields, reqparse

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Settings
# ------------------------------------------------------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'blib.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'
app.config['RESTPLUS_VALIDATE'] = True
app.config['RESTPLUS_MASK_SWAGGER'] = False
db = SQLAlchemy(app)
api = Api(app, version='1.0', title='Book Library API',
          description='Just for test')


# Super hard models
# ------------------------------------------------------------------------------
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


# Serializers
# ------------------------------------------------------------------------------
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

pagination = api.model('Page result', {
    'page': fields.Integer(description='Number of this page result'),
    'pages': fields.Integer(description='Total number of page result'),
    'per_page': fields.Integer(description='Number of items per page'),
    'totals': fields.Integer(description='Total number of result')
})

page_of_book = api.inherit('Page of books', pagination, {
    'items': fields.List(fields.Nested(book))
})


# Arguments parser for pagination
# ------------------------------------------------------------------------------
pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('page', type=int, required=False, default=1)
pagination_arguments.add_argument('bool', type=bool, required=False, default=1)
pagination_arguments.add_argument('per_page', type=int, required=False,
                                  choices=[2, 10, 30, 40, 50], default=10)


# Super awesome business logic
# ------------------------------------------------------------------------------
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


def create_author(data):
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    the_author = Author(first_name, last_name)
    db.session.add(the_author)
    db.session.commit()


def update_author(author_id, data):
    the_author = Author.query.filter(Author.id == author_id).one
    the_author.first_name = data.get('first_name')
    the_author.last_name = data.get('last_name')
    db.session.add(the_author)
    db.session.commit()


def delete_author(author_id):
    the_author = Author.query.filter(Author.id == author_id).one()
    db.session.delete(the_author)
    db.session.commit()


# Endpoints
# ------------------------------------------------------------------------------
ns = api.namespace('api', description='CRUD operations')


@ns.route('/book')
class BookList(Resource):
    @api.expect(pagination_arguments)
    @api.marshal_with(page_of_book)
    def get(self):
        """
        Возвращаем список книг по страницам
        :return: список книг
        """
        args = pagination_arguments.parse_args(request)
        page = args.get('page', 1)
        per_page = args.get('per_page', 10)
        book_query = Books.query
        books_page = book_query.paginate(page, per_page, error_out=False)
        return books_page

    @api.expect(book)
    def post(self):
        """
        Создаем книгу
        :return: не ок, 201
        """
        create_book_item(request.json)
        return None, 201


@ns.route('/book/<int:id>')
@ns.response(404, 'Book not found')
@ns.param('id', 'Book id')
class BookItem(Resource):
    @ns.marshal_with(book)
    def get(self, _id):
        """
        Вернем книгу по айди
        :param _id: айди книги
        :return: книга
        """
        return Books.query.filter(Books.id == _id).one()

    @api.response(204, 'Book successfull deleted')
    def delete(self, _id):
        """
        Удалим книгу по айди
        :param _id: айди книги
        :return: не ок или 204
        """
        delete_book_item(_id)
        return None, 204

    @api.expect(book)
    @api.response(204, 'Book successfull updated')
    def put(self, _id):
        """
        Обновляем книгу
        :param _id: книги
        :return: не ок, 204
        """
        update_book_item(_id, request.json)
        return None, 204


@ns.route('/author')
class AuthorList(Resource):
    @api.marshal_list_with(author)
    def get(self):
        """
        Возвращаем список авторов
        :return: список авторов
        """
        the_authors = Author.query.all()
        return the_authors

    @api.response(201, 'Author successful created')
    @api.expect(author)
    def post(self):
        """
        Создаем автора
        :return: не ок, ок
        """
        data = request.json
        create_author(data)
        return None, 201


@ns.route('/author/<int:id>')
@ns.response(404, 'Author nor found')
@ns.param('id', 'Author id')
class AuthorItem(Resource):
    @api.marshal_with(author_with_books)
    def get(self, _id):
        """
        Вытягиваем автора с его книгами
        :param _id: айди автора
        :return: автора с книгами
        """
        return Author.query.filter(Author.id == _id).one()

    @api.response(204, 'Author successfull deleted')
    def delete(self, _id):
        """
        Удаляем автора
        :param _id: айди автора
        :return: не ок, ок
        """
        delete_author(_id)
        return None, 204

    @api.expect(author)
    @api.response(204, 'Author successfull updated')
    def put(self, _id):
        """
        Обновляем автора
        :param _id: айди автора
        :return: не ок, ок
        """
        update_author(_id, request.json)
        return None, 204


if __name__ == '__main__':
    app.run(debug=True)
