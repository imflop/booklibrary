import unittest

from myapp import app, db
from myapp import Author, Books

from flask_fixtures import FixturesMixin

app.config.from_object('config')


class TestApp(unittest.TestCase, FixturesMixin):
    fixtures = ['authors.yaml']

    app = app
    db = db

    def test_authors(self):
        authors = Author.query.all()
        assert len(authors) == Author.query.count() == 1
        assert len(authors[0].books) == 3

