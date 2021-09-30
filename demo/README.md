# Duo Universal Python SDK Demo

A simple Python3 web application that serves a logon page integrated with Duo 2FA.

## Setup
Change to the "demo" directory
```
cd demo
```

Set up a virtual environment
```
python3 -m venv env
source env/bin/activate
```

Install the demo requirements:
```
pip3 install -r requirements.txt
```

Then, create a `Web SDK` application in the Duo Admin Panel. See https://duo.com/docs/protecting-applications for more details.

## Using the App

1. Copy the Client ID, Client Secret, and API Hostname values for your `Web SDK` application into the `duo.conf` file.
1. Start the app.
    ```
    python3 app.py
    ```
1. Navigate to http://localhost:8080. 
1. Log in with the user you would like to enroll in Duo or with an already enrolled user (any password will work).

## (Optional) Accessing the app from an external or mobile device

The default demo app configuration only allows connections from `localhost`; other devices on the network cannot access it.

To allow connections from other devices (e.g. to test the login experience from a mobile device):

1. Edit the `redirect_uri` field in `duo.conf` to be a network-accessible hostname of the machine running the demo app.
    * Due to API-enforced restrictions, this **must** be a host/domain name, not IP address.
    * The URI **must** be https.
    * Example `redirect_uri` using the computer's hostname: `https://john-11234.local:8080/duo-callback`
    * Alternatively, a third party services such as [nip.io](http://nip.io) can be used for resolving domain names to internal IP addresses.
1. Start the demo app by running the following command within the `/demo` directory:
    ```
    flask run --host=0.0.0.0 --port 8080 --cert=adhoc
    ```
    * `--host=0.0.0.0` allows connections from external devices.
    * `--cert=adhoc` will serve content over HTTPS using a self-signed certificate. (You will likely be required to accept certificate warnings in the client browser.)
1. On the client device, access the demo app using the **same** host/domain name as the redirect URL.
    * E.g. `https://john-11234.local:8080`
