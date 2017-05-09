from mongoengine import *

connect('Refresh_Tokens')

class Users(DynamicDocument):
	email=StringField()
	refreshToken=StringField()
	tokenExpiration=IntField()