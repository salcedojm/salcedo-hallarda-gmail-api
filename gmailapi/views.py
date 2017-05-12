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
from email import encoders
from apiclient import errors
from email.mime.multipart import MIMEMultipart
import json, re, requests, httplib2, base64, email,time

flow = client.flow_from_clientsecrets(
    r'C:\Users\Innovation\Desktop\salcedo-hallarda-gmail-api\gmailapi\client_secret.json',
    scope=[r'https://mail.google.com/'],
    redirect_uri='http://localhost:6543/connected')       

flow.params['include_granted_scopes'] = 'true'   
flow.params['access_type']='offline'
@view_config(route_name='message_list', renderer='templates/message_list.jinja2')
@view_config(route_name='send_message_view', renderer='templates/send_message.jinja2')
@view_config(route_name='home', renderer='templates/mytemplate.jinja2')

@view_config(route_name='actions', renderer='templates/actions.jinja2')
def index(request):
	return {"projectTitle": "GMAIL API USAGE EXAMPLE"}

@view_config(route_name='gmail', renderer='templates/mytemplate.jinja2')
def gmail(request):
	auth_uri = flow.step1_get_authorize_url()
	print(auth_uri)
	return HTTPFound(location=str(auth_uri))

@view_config(route_name='connected', renderer='templates/connected.jinja2')
def connected(request):
	if 'error' in request.params:
		return HTTPFound(location='gmail')
	auth_code=request.params['code']
	credentials = flow.step2_exchange(auth_code)
	http_auth = credentials.authorize(httplib2.Http())
	gmail=build('gmail', 'v1', http=http_auth)
	emailAddress=gmail.users().getProfile(userId='me').execute()['emailAddress']
	session=request.session
	session['emailAddress']=emailAddress
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
		credential_storage.put(credentials)
		Users.objects(email=emailAddress).update(
			set__tokenExpiration=int(credentials.token_response['expires_in'])+time.time())
	return HTTPFound(location='actions')

@view_config(route_name='get_message_list', renderer='json')
def get_message_list(request):
	message_list=[]
	gmail=build_gmail_service(request)
	unread_messages = gmail.users().messages().list(userId='me', labelIds='UNREAD').execute()
	unread_ids=[x['id'] for x in unread_messages['messages']]
	for id in unread_ids:
		#GET ONE MESSAGE.
		message = gmail.users().messages().get(userId='me', id=id, format='raw').execute()
		#JSON FILE TONG METADATA NA TO KAILANGAN KO TO SOBRAAAAAA
		metadata_message=gmail.users().messages().get(userId='me', id=id, format='metadata').execute()
		for data in metadata_message['payload']['headers']:
			if data['name']=="From":
				sender=data['value']
				break
		msg_dict={"sender": sender, "snippet": str("%s..."%message['snippet'][0:40]), "id": id}
		message_list.append(msg_dict)
	return json.dumps(message_list)
@view_config(route_name='get_message', renderer='json')
def get_message(request):
	gmail=build_gmail_service(request)
	msg_id=str(request.POST.get('id'))
	message = gmail.users().messages().get(userId='me', id=msg_id, format='raw').execute()
	#JSON FILE TONG METADATA NA TO KAILANGAN KO TO SOBRAAAAAA
	metadata_message=gmail.users().messages().get(userId='me', id=msg_id, format='metadata').execute()
	
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
	for x in metadata_message['payload']['headers']:
		if x['name']=="From":
			sender=x['value']
			break
	return {"snippet": snippet, "message": value, "from": sender}

def get_new_access_token(refreshToken):
	client_id='671614443448-s8add1bvhklmrukfh3n7rd1vhspchl61.apps.googleusercontent.com'
	client_secret='8GruaReu0qjYemohKNrgzj-1'
	grant_type='refresh_token'
	url='https://www.googleapis.com/oauth2/v4/token'
	post_fields={'client_id': client_id, 'client_secret': client_secret, 'refresh_token': refreshToken, 'grant_type': grant_type}
	response=requests.post(url, post_fields)
	token_data=json.loads(response.text)
	# #reponse keys: access_token, token_type, expires_in
	return token_data

# RETURNS TRUE IF ACCESS TOKEN HAS EXPIRED
# PARAM userEmail = 'email of the user'
def is_token_expired(userEmail):
	timeLeft=int(Users.objects(email=userEmail)[0]['tokenExpiration'])-time.time()
	if timeLeft<300:
		return True
	else:
		return False

def create_message(sender, to, subject, message_text_html, message_text_plain):
    message = MIMEMultipart('alternative') # needed for both plain & HTML (the MIME type is multipart/alternative)
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = to

    #Create the body of the message (a plain-text and an HTML version)
    message.attach(MIMEText(message_text_plain, 'plain'))
    message.attach(MIMEText(message_text_html, 'html'))

    raw_message_no_attachment = base64.urlsafe_b64encode(message.as_bytes())
    raw_message_no_attachment = raw_message_no_attachment.decode()
    body  = {'raw': raw_message_no_attachment}
    return body

@view_config(route_name='send_message', renderer='json')
def send_message(request):
	gmail=build_gmail_service(request)
	sender=request.session['emailAddress']
	subject=request.POST.get('subject')
	message_text_html=str("<br>".join(request.POST.get('message').split("\n")))
	message_text_plain=request.POST.get('message')
	to=request.POST.get('to')
	message=create_message(sender, to, subject, message_text_html, message_text_plain)
	try:
		message_sent = (gmail.users().messages().send(userId='me', body=message).execute())
		message_id = message_sent['id']
		return{"response": "SENT"}
	except errors.HttpError as error:
		return{"response":str('An error occurred: {error}')}

def build_gmail_service(request):
	emailAddress=request.session['emailAddress']
	credential_storage=Storage('credentials/%s.dat' % emailAddress)
	credentials=credential_storage.get()
	#check if token has expired. if true then retrieve new access token
	if is_token_expired(str(emailAddress)):
		token_data=get_new_access_token(credentials.refresh_token)
		credentials.access_token=token_data['access_token']
		credentials.token_response['access_token']=token_data['access_token']
		credentials.token_response['expires_in']=token_data['expires_in']
		Users.objects(email=emailAddress).update(
			set__tokenExpiration=int(credentials.token_response['expires_in'])+time.time())
		credential_storage.put(credentials)
	http_auth=credentials.authorize(httplib2.Http())
	gmail=build('gmail', 'v1', http=http_auth)
	return gmail