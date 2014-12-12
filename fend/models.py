from mongoengine import Document, StringField, ObjectIdField, URLField, DateTimeField
from datetime import datetime


class Project(Document):
    name = StringField(required=True)
    author_id = ObjectIdField(required=True)
    project_version = StringField()
    picture = URLField()
    description = StringField()
    link = URLField(required=True)
    created_at = DateTimeField(default=datetime.now, required=True)


class Author(Document):
    name = StringField(required=True)

