gmailapi
===============================

Getting Started
---------------

- Change directory into this project.

    cd salcedo-hallarda-gmail-api

- Create a Python virtual environment.

    python -m venv env

- Activate the virtual environment

	cd env\scripts
	activate
	cd ../..

- Upgrade packaging tools.

    salcedo-hallarda-gmail-api/pip install --upgrade pip setuptools

- Install the project in editable mode with its testing requirements.

    salcedo-hallarda-gmail-api/pip install -e .

- Install the gmail api client and oauth2client
	
	pip install --upgrade google-api-python-client

- Install mongoengine
	
	pip install mongoengine

-Install requests
	pip install requests

- In gmailapi/templates/views.py LINE 17
	Copy the directory of your client_secret.json file

- Run your project.

    salcedo-hallarda-gmail-api/pserve development.ini --reload