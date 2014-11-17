from mongoengine import Document, StringField


class Test(Document):
    text = StringField(required=True, db_field='t')
