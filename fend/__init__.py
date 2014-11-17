from mongoengine import connect

from fend.models import Test

connect(db='fend', alias='default')
