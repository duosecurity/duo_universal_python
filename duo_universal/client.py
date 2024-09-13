from urllib.parse import urlencode
import time
import jwt
import requests
import json
import random
import string
import os
import platform
from duo_universal.version import __version__

CLIENT_ID_LENGTH = 20
CLIENT_SECRET_LENGTH = 40
JTI_LENGTH = 36
MINIMUM_STATE_LENGTH = 16
MAXIMUM_STATE_LENGTH = 1024
STATE_LENGTH = 36
SUCCESS_STATUS_CODE = 200
FIVE_MINUTES_IN_SECONDS = 300
# One minute in seconds
LEEWAY = 60

ERR_USERNAME = 'The username is invalid.'
ERR_NONCE = 'The nonce is invalid.'
ERR_CLIENT_ID = 'The Duo client id is invalid.'
ERR_CLIENT_SECRET = 'The Duo client secret is invalid.'
ERR_API_HOST = 'The Duo api host is invalid'
ERR_REDIRECT_URI = 'No redirect uri'
ERR_CODE = 'Missing authorization code'
ERR_UNKNOWN = 'An unknown error has occurred.'
ERR_GENERATE_LEN = 'Length needs to be at least 16'
ERR_STATE_LEN = ('State must be at least {MIN} characters long and no longer than {MAX} characters').format(
    MIN=MINIMUM_STATE_LENGTH,
    MAX=MAXIMUM_STATE_LENGTH
)
ERR_NONCE_LEN = ('Nonce must be at least {MIN} characters long and no longer than {MAX} characters').format(
    MIN=MINIMUM_STATE_LENGTH,
    MAX=MAXIMUM_STATE_LENGTH
)
ERR_EXP_SECONDS_TOO_LONG = 'Client may not be configured for a JWT expiry longer than five minutes.'
ERR_EXP_SECONDS_TOO_SHORT = 'Invalid JWT expiry duration.'

API_HOST_URI_FORMAT = "https://{}"
OAUTH_V1_HEALTH_CHECK_ENDPOINT = "https://{}/oauth/v1/health_check"
OAUTH_V1_AUTHORIZE_ENDPOINT = "https://{}/oauth/v1/authorize"
OAUTH_V1_TOKEN_ENDPOINT = "https://{}/oauth/v1/token"
DEFAULT_CA_CERT_PATH = os.path.join(os.path.dirname(__file__), 'ca_certs.pem')

CLIENT_ASSERT_TYPE = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"


class DuoException(Exception):
    pass


class Client:
    @property
    def _clamped_expiry_duration(self):
        return max(min(FIVE_MINUTES_IN_SECONDS, self._exp_seconds), 1)

    def _generate_rand_alphanumeric(self, length):
        """
        Generates random string
        Arguments:

        length      -- Desired length of random string

        Returns:

        Randomly generated alphanumeric string

        Raises:

        ValueError if length is too short
        """
        if length < min(MINIMUM_STATE_LENGTH, JTI_LENGTH):
            raise ValueError(ERR_GENERATE_LEN)
        generator = random.SystemRandom()
        characters = string.ascii_letters + string.digits
        return ''.join(generator.choice(characters) for i in range(length))

    def _validate_init_config(self, client_id, client_secret,
                              api_host, redirect_uri, exp_seconds):
        """
        Verifies __init__ parameters

        Arguments:

        client_id       -- Client ID for the application in Duo
        client_secret   -- Client secret for the application in Duo
        host            -- Duo api host
        redirect_uri    -- Uri to redirect to after a successful auth
        exp_seconds     -- The JWT expiry window

        Raises:

        DuoException errors for invalid parameters
        """
        if not client_id or len(client_id) != CLIENT_ID_LENGTH:
            raise DuoException(ERR_CLIENT_ID)
        if not client_secret or len(client_secret) != CLIENT_SECRET_LENGTH:
            raise DuoException(ERR_CLIENT_SECRET)
        if not api_host:
            raise DuoException(ERR_API_HOST)
        if not redirect_uri:
            raise DuoException(ERR_REDIRECT_URI)
        if exp_seconds > FIVE_MINUTES_IN_SECONDS:
            raise DuoException(ERR_EXP_SECONDS_TOO_LONG)
        elif exp_seconds < 0:
            raise DuoException(ERR_EXP_SECONDS_TOO_SHORT)

    def _validate_create_auth_url_inputs(self, username, state, nonce=None):
        if nonce and (MINIMUM_STATE_LENGTH >= len(nonce) or len(nonce) >= MAXIMUM_STATE_LENGTH):
            raise DuoException(ERR_NONCE_LEN)
        if not state or not (MINIMUM_STATE_LENGTH <= len(state) <= MAXIMUM_STATE_LENGTH):
            raise DuoException(ERR_STATE_LEN)
        if not username:
            raise DuoException(ERR_USERNAME)

    def _create_jwt_args(self, endpoint):
        jwt_args = {
            'iss': self._client_id,
            'sub': self._client_id,
            'aud': endpoint,
            'exp': time.time() + self._clamped_expiry_duration,
            'jti': self._generate_rand_alphanumeric(JTI_LENGTH)
        }

        return jwt_args

    def __init__(self, client_id, client_secret, host,
                 redirect_uri, duo_certs=DEFAULT_CA_CERT_PATH, use_duo_code_attribute=True, http_proxy=None,
                 exp_seconds=FIVE_MINUTES_IN_SECONDS):
        """
        Initializes instance of Client class

        Arguments:

        client_id                -- Client ID for the application in Duo
        client_secret            -- Client secret for the application in Duo
        host                     -- Duo api host
        redirect_uri             -- Uri to redirect to after a successful auth
        duo_certs                -- (Optional) Provide custom CA certs
        use_duo_code_attribute   -- (Optional: default true) Flag to use `duo_code` instead of `code` for returned authorization parameter
        http_proxy               -- (Optional) HTTP proxy to tunnel requests through
        exp_seconds              -- (Optional) The number of seconds used for JWT expiry. Must be be at most 5 minutes.
        """

        self._validate_init_config(client_id,
                                   client_secret,
                                   host,
                                   redirect_uri,
                                   exp_seconds)

        self._client_id = client_id
        self._client_secret = client_secret
        self._api_host = host
        self._redirect_uri = redirect_uri
        self._use_duo_code_attribute = use_duo_code_attribute

        # If duo_certs is None set it to the DEFAULT_CA_CERT_PATH
        # so that we make sure we are pinning certs
        if duo_certs is not None:
            if duo_certs == "DISABLE":
                self._duo_certs = False
            else:
                self._duo_certs = duo_certs
        else:
            self._duo_certs = DEFAULT_CA_CERT_PATH

        if http_proxy is not None:
            self._http_proxy = {'https': http_proxy}
        else:
            self._http_proxy = None
        self._exp_seconds = exp_seconds

    def generate_state(self):
        """
        Return a random string of 36 characters
        """
        return self._generate_rand_alphanumeric(STATE_LENGTH)

    def health_check(self):
        """
        Checks whether Duo is available.

        Returns:

        {'response': {'timestamp': <int:unix timestamp>}, 'stat': 'OK'}

        Raises:

        DuoException on error for invalid credentials
        or problem connecting to Duo
        """

        health_check_endpoint = OAUTH_V1_HEALTH_CHECK_ENDPOINT.format(self._api_host)

        jwt_args = self._create_jwt_args(health_check_endpoint)

        all_args = {
            'client_assertion': jwt.encode(jwt_args,
                                           self._client_secret,
                                           algorithm='HS512'),
            'client_id': self._client_id
        }
        try:
            response = requests.post(health_check_endpoint,
                                     data=all_args,
                                     verify=self._duo_certs,
                                     proxies=self._http_proxy)
            res = json.loads(response.content)
            if res['stat'] != 'OK':
                raise DuoException(res)

        except Exception as e:
            raise DuoException(e)

        return res

    def create_auth_url(self, username, state, nonce=None):
        """Generate uri to Duo's prompt

        Arguments:

        username        -- username trying to authenticate with Duo
        state           -- Randomly generated character string of at least 16
                           and at most 1024 characters returned to the integration by Duo after 2FA
        nonce           -- Randomly generated character string of at least 16
                           and at most 1024 characters used as the nonce for the underlying OIDC flow

        Returns:

        Authorization uri to redirect to for the Duo prompt
        """

        self._validate_create_auth_url_inputs(username, state, nonce=nonce)

        authorize_endpoint = OAUTH_V1_AUTHORIZE_ENDPOINT.format(self._api_host)

        jwt_args = {
            'scope': 'openid',
            'redirect_uri': self._redirect_uri,
            'client_id': self._client_id,
            'iss': self._client_id,
            'aud': API_HOST_URI_FORMAT.format(self._api_host),
            'exp': time.time() + self._clamped_expiry_duration,
            'state': state,
            'response_type': 'code',
            'duo_uname': username,
            'use_duo_code_attribute': self._use_duo_code_attribute,
        }

        request_jwt = jwt.encode(jwt_args,
                                 self._client_secret,
                                 algorithm='HS512')
        all_args = {
            'response_type': 'code',
            'client_id': self._client_id,
            'request': request_jwt,
        }
        if nonce:
            all_args['nonce'] = nonce

        query_string = urlencode(all_args)
        authorization_uri = "{}?{}".format(authorize_endpoint, query_string)
        return authorization_uri

    def exchange_authorization_code_for_2fa_result(self, duoCode, username, nonce=None):
        """
        Exchange the duo_code for a token with Duo to determine
        if the auth was successful.

        Argument:

        duoCode         -- Authentication session transaction id
                           returned by Duo
        username        -- Name of the user authenticating with Duo
        nonce           -- Random 36B string used to associate
                           a session with an ID token

        Return:

        A token with meta-data about the auth

        Raises:

        DuoException on error for invalid duo_codes, invalid credentials,
        or problems connecting to Duo
        """
        if not duoCode:
            raise DuoException(ERR_CODE)

        token_endpoint = OAUTH_V1_TOKEN_ENDPOINT.format(self._api_host)
        jwt_args = self._create_jwt_args(token_endpoint)

        all_args = {
            'grant_type': 'authorization_code',
            'code': duoCode,
            'redirect_uri': self._redirect_uri,
            'client_id': self._client_id,
            'client_assertion_type': CLIENT_ASSERT_TYPE,
            'client_assertion': jwt.encode(jwt_args,
                                           self._client_secret,
                                           algorithm='HS512')
        }
        try:
            user_agent = ("duo_universal_python/{version} "
                          "python/{python_version} {os_name}").format(version=__version__,
                                                                      python_version=platform.python_version(),
                                                                      os_name=platform.platform())
            response = requests.post(token_endpoint,
                                     params=all_args,
                                     headers={"user-agent":
                                              user_agent},
                                     verify=self._duo_certs,
                                     proxies=self._http_proxy)
        except Exception as e:
            raise DuoException(e)

        if response.status_code != SUCCESS_STATUS_CODE:
            error_message = json.loads(response.content)
            raise DuoException(error_message)

        try:
            decoded_token = jwt.decode(
                response.json()['id_token'],
                self._client_secret,
                audience=self._client_id,
                issuer=OAUTH_V1_TOKEN_ENDPOINT.format(self._api_host),
                leeway=LEEWAY,
                algorithms=["HS512"],
                options={
                    'require': ['exp', 'iat'],
                    'verify_iat': True
                },
            )
        except Exception as e:
            raise DuoException(e)

        if ('preferred_username' not in decoded_token or not decoded_token['preferred_username'] == username):
            raise DuoException(ERR_USERNAME)
        if nonce and ('nonce' not in decoded_token or not decoded_token['nonce'] == nonce):
            raise DuoException(ERR_NONCE)

        return decoded_token
