from mongoengine import Document, StringField, ObjectIdField, URLField, DateTimeField, ListField, ValidationError
from datetime import datetime
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
        """Ensures that the name of the project is not empty."""
        if self.name is not None and type(self.name) is unicode and not self.name.strip():
                raise ValidationError(field_name='name', message='Field can not be empty.')

    def validate(self, clean=True):
        """Calls the parent `validate(self, clean)`. If `ValidationError` is raised, checks if
        the error is about the emptiness of the field `name`. If yes, raises a new properly
        formatted `ValidationError`, if no raises the error as it is.

        :param self: the document to validate.
        :param clean: whether to run the `clean(self)` function or not.
        """
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

