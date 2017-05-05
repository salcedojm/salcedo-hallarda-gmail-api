from mongoengine import *

class RefreshToken(DynamicDocument):
	refresh_token=StringField()
	expiration=IntField()
	access_token=StringField()