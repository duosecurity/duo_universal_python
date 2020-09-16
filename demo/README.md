# Duo Universal Python SDK Demo

A simple Python web application that serves a logon page integrated with Duo 2FA.

## Setup
The following steps assume the SDK is already installed and that you're working in your preferred environment. See the top-level README for installation and environment setup instructions.

Install the demo requirements:
```
cd demo
pip install -r requirements.txt
```

Then, create a `Web SDK` application in the Duo Admin Panel. See https://duo.com/docs/protecting-applications for more details.
## Using the App

1. Using the Client ID, Client Secret, and API Hostname for your `Web SDK` application, start the app.
    ```
    DUO_CLIENT_ID=<client_id> DUO_CLIENT_SECRET=<client_secret> DUO_API_HOST=<api_host> python app.py
    ```
1. Navigate to http://localhost:8080. 
1. Log in with the user you would like to enroll in Duo or with an already enrolled user (any password will work).