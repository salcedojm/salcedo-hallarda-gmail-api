from pyramid.view import view_config
from oauth2client import client
from pyramid.httpexceptions import HTTPFound
import httplib2
from apiclient.discovery import build
import base64
import email
flow = client.flow_from_clientsecrets(
    r'C:\Users\jmsalcedo\Desktop\salcedo-hallarda-gmail-api\gmailapi\client_secret_671614443448-s8add1bvhklmrukfh3n7rd1vhspchl61.apps.googleusercontent.com.json',
    scope=r'https://mail.google.com/',
    redirect_uri='http://localhost:6543/connected')
flow.params['access_type'] = 'offline'         # offline access
flow.params['include_granted_scopes'] = 'true'   # incremental auth

@view_config(route_name='gmail', renderer='templates/mytemplate.jinja2')
def my_view(request):
	
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
	messages = gmail.users().messages().list(userId='me', q='').execute()
	#msg_id=[x['messages'][0] for x in messages if x=='messages']
	#print(msg_id)
	message = gmail.users().messages().get(userId='me', id=messages['messages'][0]['id'], format='raw').execute()
	#msg_str = str(base64.urlsafe_b64decode(message['raw'].encode('ASCII')))
	#mime_msg = email.message_from_string(msg_str)
	#messageMainType = mime_msg.get_content_maintype()
	#if messageMainType == 'multipart':
#		for part in mime_msg.get_payload():
#			if part.get_content_maintype() == 'text':
#				return part.get_payload()
 #                   return ""
  #          elif messageMainType == 'text':
   #                 return mime_msg.get_payload()
	return {"key": request.params['code'], "results": str(message)}