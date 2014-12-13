from mongoengine import Document, StringField, ObjectIdField, URLField, DateTimeField, ListField, ValidationError
from helpers import *


class Project(Document):
    name = StringField(required=True)
    author_id = ObjectIdField(required=True)
    project_version = StringField()
    picture = URLField()
    description = StringField()
    link = URLField(required=True)
    created_at = DateTimeField(default=datetime.now, required=True)

    def clean(self):
        if self.name is not None and type(self.name) is unicode and not self.name.strip():
                raise ValidationError(field_name='name', message='Field can not be empty.')

    def validate(self, clean=True):
        try:
            Document.validate(self, clean)
        except ValidationError as e:
            error = e.errors.get('__all__')
            raise ValidationError(errors={error.field_name: error.message}) if error is not None else e

    def to_dict(self):
        return document_to_dict(self)


class Author(Document):
    name = StringField(required=True)
    projects = ListField(ObjectIdField())

    def to_dict(self):
        return document_to_dict(self)

