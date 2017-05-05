from mongoengine import *

connect('Refresh_Tokens')
class RefreshToken(DynamicDocument):
	refresh_token=StringField()
	expiration=IntField()
	access_token=StringField()