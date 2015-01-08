from unittest import TestCase
from mongoengine import connection
from fend.settings import MONGO_TEST_DATABASE
from fend.models import Project
from bson import ObjectId


class TestProject(TestCase):
    def setUp(self):
        db = connection.get_db(
            MONGO_TEST_DATABASE['db_alias']
        )

        for collection in db.collection_names():
            if collection != 'system.indexes':
                db.drop_collection(collection)

    def test_creation(self):
	p = Project(
            name='aaa', author_id=ObjectId(), link='http://www.bla.com'
        )
        p.save()

        rp = Project.objects.get(name='aaa')
        self.assertEqual(p.name, rp.name)
        # Test the rest of the parameters

    # Tests for all the methods

# New test class for Author document
