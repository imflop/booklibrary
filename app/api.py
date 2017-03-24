from flask_restful import Resource
from app.models import Author


class Author(Resource):
    def get(self):
        authors = Author.query.all()
        return authors
