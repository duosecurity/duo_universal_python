import configparser
import json
import os
import traceback

from flask import Flask, request, redirect, session, render_template

from duo_universal.client import Client, DuoException

config = configparser.ConfigParser()
config.read("duo.conf")

try:
    duo_client = Client(
        client_id=config['duo']['client_id'],
        client_secret=config['duo']['client_secret'],
        host=config['duo']['api_hostname'],
        redirect_uri=config['duo']['redirect_uri'],
    )
except DuoException as e:
    print("*** Duo config error. Verify the values in duo.conf are correct ***")
    raise e

duo_failmode = config['duo']['failmode']

app = Flask(__name__)
app.secret_key = os.urandom(32)


@app.route("/", methods=['GET'])
def login():
    return render_template("login.html", message="This is a demo")


@app.route("/", methods=['POST'])
def login_post():
    """
    respond to HTTP POST with 2FA as long as health check passes
    """
    try:
        duo_client.health_check()
    except DuoException:
        traceback.print_exc()
        if duo_failmode.upper() == "OPEN":
            # If we're failing open errors in 2FA still allow for success
            return render_template("success.html",
                                   message="Login 'Successful', but 2FA Not Performed. Confirm Duo client/secret/host values are correct")
        else:
            # Otherwise the login fails and redirect user to the login page
            return render_template("login.html",
                                   message="2FA Unavailable. Confirm Duo client/secret/host values are correct")

    username = request.form.get('username')
    password = request.form.get('password')

    # Check user's first factor
    if password is None or password == "":
        return render_template("login.html",
                               message="Missing password")

    # Generate random string to act as a state for the exchange
    state = duo_client.generate_state()
    session['state'] = state
    session['username'] = username
    prompt_uri = duo_client.create_auth_url(username, state)

    # Redirect to prompt URI which will redirect to the client's redirect URI
    # after 2FA
    return redirect(prompt_uri)


# This route URL must match the redirect_uri passed to the duo client
@app.route("/duo-callback")
def duo_callback():
    if request.args.get('error'):
        return "Got Error: {}".format(request.args)

    # Get state to verify consistency and originality
    state = request.args.get('state')

    # Get authorization token to trade for 2FA
    code = request.args.get('duo_code')

    if 'state' in session and 'username' in session:
        saved_state = session['state']
        username = session['username']
    else:
        # For flask, if url used to get to login.html is not localhost,
        # (ex: 127.0.0.1) then the sessions will be different
        # and the localhost session does not have the state
        return render_template("login.html",
                               message="No saved state please login again")

    # Ensure nonce matches from initial request
    if state != saved_state:
        return render_template("login.html",
                               message="Duo state does not match saved state")

    decoded_token = duo_client.exchange_authorization_code_for_2fa_result(code, username)

    # Exchange happened successfully so render success page
    return render_template("success.html",
                           message=json.dumps(decoded_token, indent=2, sort_keys=True))


if __name__ == '__main__':
    app.run(host="localhost", port=8080)
