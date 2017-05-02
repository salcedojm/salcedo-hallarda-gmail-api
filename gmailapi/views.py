from pyramid.view import view_config
from oauth2client import client
from pyramid.httpexceptions import HTTPFound
import httplib2, base64, email
from apiclient.discovery import build
from email.mime.text import MIMEText
import json
snippet=""
msg_txt=""
flow = client.flow_from_clientsecrets(
    r'C:\Users\Innovation\Desktop\salcedo-hallarda-gmail-api\gmailapi\client_secret.json',
    scope=r'https://mail.google.com/',
    redirect_uri='http://localhost:6543/connected')
flow.params['access_type'] = 'offline'         # offline access
flow.params['include_granted_scopes'] = 'true'   # incremental auth

@view_config(route_name='home', renderer='templates/mytemplate.jinja2')
def index(request):
	return {"projectTitle": "GMAIL API USAGE EXAMPLE"}

@view_config(route_name='gmail', renderer='templates/mytemplate.jinja2')
def gmail(request):
	
	auth_uri = flow.step1_get_authorize_url()
	print(auth_uri)
	return HTTPFound(location=str(auth_uri))

@view_config(route_name='connected', renderer='templates/connected.jinja2')
def connected_view(request):
	auth_code=request.params['code']
	credentials = flow.step2_exchange(auth_code)
	http_auth = credentials.authorize(httplib2.Http())
	gmail=build('gmail', 'v1', http=http_auth)
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
	message = gmail.users().messages().get(userId='me', id=message_ids[0], format='raw').execute()
	msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
	msg_str=msg_str.decode('utf-8')
	mime_msg = email.message_from_string(msg_str)
	for part in mime_msg.walk():
		if part.get_content_type()=="text/plain":
			body=part.get_payload(decode=True)
			msg=body.decode('utf-8')
			msg = "<br>".join(msg.split("\n"))

	global snippet
	global msg_txt
	snippet=message['snippet']
	msg_txt=msg
	return {"key": request.params['code'], "results": msg , "messageSnippet": message['snippet']}

@view_config(route_name='get_message', renderer='json')
def get_message(request):
	global snippet
	global msg_txt
	return {"snippet": snippet, "message": msg_txt}