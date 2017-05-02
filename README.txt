gmailapi
===============================

Getting Started
---------------

- Change directory into this project.

    cd salcedo-hallarda-gmail-api

- Create a Python virtual environment.

    python3 -m venv env

- Upgrade packaging tools.

    env/bin/pip install --upgrade pip setuptools

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Run your project's tests.

    env/bin/pytest

- Install the gmail api client and oauth2client
	
	pip install --upgrade google-api-python-client

- In gmailapi/templates/views.py LINE 9
	Copy the directory of client_secret.json file
- Run your project.

    env/bin/pserve development.ini