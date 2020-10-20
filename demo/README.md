# Duo Universal Python SDK Demo

A simple Python web application that serves a logon page integrated with Duo 2FA.

## Setup
Change to the "demo" directory
```
cd demo
```

Set up a virtual environment
```
# Python 3
python -m venv env
source env/bin/activate

# Python 2
virtualenv env
source env/bin/activate
```

Install the demo requirements:
```
pip install -r requirements.txt
```

Then, create a `Web SDK` application in the Duo Admin Panel. See https://duo.com/docs/protecting-applications for more details.
## Using the App

1. Copy the Client ID, Client Secret, and API Hostname values for your `Web SDK` application into the `duo.conf` file.
1. Start the app.
    ```
    python app.py
    ```
1. Navigate to http://localhost:8080. 
1. Log in with the user you would like to enroll in Duo or with an already enrolled user (any password will work).
