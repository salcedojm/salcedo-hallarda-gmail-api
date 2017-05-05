from mongoengine import *
from datetime import datetime

connect('Refresh_Tokens')
class RefreshToken(DynamicDocument):
	refresh_token=StringField()
	expiration=IntField()
	access_token=StringField()