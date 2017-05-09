from pyramid.view import view_config
from oauth2client import client
from pyramid.httpexceptions import HTTPFound
from .models import *
from apiclient.discovery import build
from email.mime.text import MIMEText
from datetime import datetime
from pprint import pprint
from oauth2client.file import Storage
from threading import Timer
import json, re, requests, httplib2, base64, email,time

flow = client.flow_from_clientsecrets(
    r'C:\Users\Innovation\Desktop\salcedo-hallarda-gmail-api\gmailapi\client_secret.json',
    scope=[r'https://mail.google.com/',
    r'https://www.googleapis.com/auth/gmail.modify',
    r'https://www.googleapis.com/auth/gmail.compose',
    r'https://www.googleapis.com/auth/gmail.readonly'],
    redirect_uri='http://localhost:6543/connected')       # offline access

flow.params['include_granted_scopes'] = 'true'   # incremental auth
flow.params['access_type']='offline'
flow.params['approval_prompt']='force'

@view_config(route_name='send_message_view', renderer='templates/send_message.jinja2')
@view_config(route_name='home', renderer='templates/mytemplate.jinja2')
def index(request):
	return {"projectTitle": "GMAIL API USAGE EXAMPLE"}

@view_config(route_name='gmail', renderer='templates/mytemplate.jinja2')
def gmail(request):
	auth_uri = flow.step1_get_authorize_url()
	print(auth_uri)
	return HTTPFound(location=str(auth_uri))

@view_config(route_name='connected', renderer='templates/connected.jinja2')
def connected(request):
	auth_code=request.params['code']
	global credentials
	global gmail
	credentials = flow.step2_exchange(auth_code)
	http_auth = credentials.authorize(httplib2.Http())
	gmail=build('gmail', 'v1', http=http_auth)
	emailAddress=gmail.users().getProfile(userId='me').execute()['emailAddress']
	session=request.session
	session['emailAddress']=emailAddress
	#storage = Storage('credentials/%s.dat' % emailAddress)
	#storage.put(credentials)
	existing_user=bool(Users.objects(email=emailAddress))
	if not existing_user:
		users=Users(email=emailAddress,
			refreshToken=credentials.refresh_token,
			tokenExpiration=int(credentials.token_response['expires_in'])+time.time())
		users.save()
		credential_storage=Storage('credentials/%s.dat' % emailAddress)
		credential_storage.put(credentials)
	else:
		credential_storage=Storage('credentials/%s.dat' % emailAddress)
		credentials=credential_storage.get()

	print("ACCESS TOKEN: %s" %credentials.access_token)
	
	if credentials.refresh_token is not None:
		refresh_token=credentials.refresh_token
	else:
		refresh_token="ALREADY DEEMED"
	return HTTPFound(location='messages')

@view_config(route_name='messages', renderer='templates/messages.jinja2')
def messages(request):
	return {"title": "MESSAGES"}

@view_config(route_name='get_message', renderer='json')
def get_message(request):
	global gmail
	session=request.session
	emailAddress=session['emailAddress']
	check_token_expiry(str(emailAddress),str(credentials.refresh_token))
	fields = gmail.users().labels().list(userId='me').execute()
	#GET ALL MESSAGE
	
	messages = gmail.users().messages().list(userId='me', q='').execute()
	
	#GET ALL MESSAGE ID's
	message_ids=[x['id'] for x in messages['messages']]
	
	#GET UNREAD MESSAGES
	unread_messages = gmail.users().messages().list(userId='me', labelIds='UNREAD').execute()
	
	#GET UNREAD MESSAGES ID's
	unread_ids=[x['id'] for x in unread_messages['messages']]
	
	#GET ONE MESSAGE.
	message = gmail.users().messages().get(userId='me', id=unread_ids[0], format='raw').execute()
	msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
	msg_str=msg_str.decode('utf-8')
	mime_msg = email.message_from_string(msg_str)
	for part in mime_msg.walk():
		if part.get_content_type()=="text/plain":
			body=part.get_payload(decode=True)
			msg=body.decode('utf-8')
			msg = str("<br>".join(msg.split("\n")))

	snippet=message['snippet']
	msg_txt=msg
	urls=re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg_txt)

	link = re.compile(r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.MULTILINE|re.UNICODE)
	value = link.sub(r'<a href="\1" target="_blank">\1</a>', msg_txt)
	#for x in urls:
	#	msg_txt.replace('"'+x+'"', "<a href='"+x+"'>"+x+"</a>")
	#	print("<a href='"+x+"'>"+x+"</a>")
	return {"snippet": snippet, "message": value}

def get_new_access_token(refreshToken):
	client_id='671614443448-s8add1bvhklmrukfh3n7rd1vhspchl61.apps.googleusercontent.com'
	client_secret='8GruaReu0qjYemohKNrgzj-1'
	grant_type='refresh_token'
	url='https://www.googleapis.com/oauth2/v4/token'
	post_fields={'client_id': client_id, 'client_secret': client_secret, 'refresh_token': refreshToken, 'grant_type': grant_type}
	response=requests.post(url, post_fields)
	json_data=json.loads(response.text)
	# expire_time=int(json_data['expires_in'])+time.time()
	# r=RefreshToken(refresh_token=refreshToken, expiration=expire_time, access_token=json_data['access_token'])
	# r.save()
	# #reponse keys: access_token, token_type, expires_in
	return json_data

def check_token_expiry(userEmail, refresh_token):
	timeLeft=int(Users.objects(email=userEmail)[0]['tokenExpiration'])-time.time()
	print("TIMELEFT IS %s" % timeLeft)
