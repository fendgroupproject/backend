from mongoengine import connect
import settings

def setup(test=False):
    if test:
        db = settings.MONGO_TEST_DATABASE
    else:
        db = settings.MONGO_DATABASE

    connect(db=db['db_name'], alias=db['db_alias'])
