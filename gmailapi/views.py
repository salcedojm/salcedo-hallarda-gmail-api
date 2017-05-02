from pyramid.view import view_config
from oauth2client import client
from pyramid.httpexceptions import HTTPFound
import httplib2, base64, email
from apiclient.discovery import build
from email.mime.text import MIMEText

flow = client.flow_from_clientsecrets(
    r'C:\Users\Innovation\Desktop\salcedo-hallarda-gmail-api\gmailapi\client_secret_671614443448-s8add1bvhklmrukfh3n7rd1vhspchl61.apps.googleusercontent.com.json',
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
	
	#GET ONE MESSAGE.
	message = gmail.users().messages().get(userId='me', id=message_ids[0], format='raw').execute()
	msg_str = str(base64.urlsafe_b64decode(message['raw'].encode('ASCII')))
	mime_msg = email.message_from_string(msg_str)
	
	"""read_message={}
	if mime_msg.get_content_maintype()=="multipart/alternative":
		for content in mime_msg.message.walk():
			if content.get_content_type()=="text/plain":
				read_message['body']=content.get_payload(decode=True)
			elif content.get_content_type()=="text/html":
				read_message['html']=content.get_payload(decode=True)
	elif mime_msg.get_content_maintype()=="text":
		read_message['body']=mime_msg.get_payload()"""
	mytext=''
	for part in mime_msg.walk():
		mime_msg.get_payload()
		if part.get_content_type()=='text/html':
			mytext=base64.urlsafe_b64decode(part.get_payload().encode('UTF-8'))
	#GET UNREAD MESSAGES
	unread_messages = gmail.users().messages().list(userId='me',labelIds='UNREAD').execute()
	
	#GET UNREAD MESSAGES ID's
	unread_ids=[x['id'] for x in unread_messages['messages']]
	return {"key": request.params['code'], "results": str(mime_msg)}