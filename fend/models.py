from mongoengine import Document, StringField, ObjectIdField, URLField, DateTimeField, ListField
from helpers import *


class Project(Document):
    name = StringField(required=True)
    author_id = ObjectIdField(required=True)
    project_version = StringField()
    picture = URLField()
    description = StringField()
    link = URLField(required=True)
    created_at = DateTimeField(default=datetime.now, required=True)

    def to_dict(self):
        return document_to_dict(self)


class Author(Document):
    name = StringField(required=True)
    projects = ListField(ObjectIdField())

    def to_dict(self):
        return document_to_dict(self)

