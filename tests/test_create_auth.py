from urllib.parse import urlencode
from duo_universal import client
from mock import MagicMock, patch
import jwt
import unittest

CLIENT_ID = "DIXXXXXXXXXXXXXXXXXX"
CLIENT_SECRET = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
HOST = "api-XXXXXXX.test.duosecurity.com"
REDIRECT_URI = "https://www.example.com"
USERNAME = "user1"
STATE = "deadbeefdeadbeefdeadbeefdeadbeefdead"
DEST_APP_NAME = "Example App"
DEST_APP_ID = "example-app-1234"
DISPLAY_USERNAME = "User One"

NONE = None


class TestCreateAuthUrl(unittest.TestCase):

    @patch('time.time', MagicMock(return_value=2))
    def test_encrypted_jwt(self):
        """
        Test create_auth_url returns a valid authorization uri
        """
        duo_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

        expected_jwt_args = {
            'scope': 'openid',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'iss': CLIENT_ID,
            'aud': client.API_HOST_URI_FORMAT.format(HOST),
            'exp': 302,
            'state': STATE,
            'response_type': 'code',
            'duo_uname': USERNAME,
            'use_duo_code_attribute': True,
        }

        self._assert_client_creates_expected_uri(duo_client, expected_jwt_args)

    @patch('time.time', MagicMock(return_value=2))
    def test_use_duo_code_false(self):
        """
        Test create_auth_url returns a valid authorization uri
        """
        duo_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI, use_duo_code_attribute=False)

        expected_jwt_args = {
            'scope': 'openid',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'iss': CLIENT_ID,
            'aud': client.API_HOST_URI_FORMAT.format(HOST),
            'exp': 302,
            'state': STATE,
            'response_type': 'code',
            'duo_uname': USERNAME,
            'use_duo_code_attribute': False,
        }

        self._assert_client_creates_expected_uri(duo_client, expected_jwt_args)

    @patch('time.time', MagicMock(return_value=2))
    def test_dest_app_name_and_dest_app_id(self):
        """
        Test create_auth_url includes dest_app_name and dest_app_id when given
        """
        duo_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

        expected_jwt_args = {
            'scope': 'openid',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'iss': CLIENT_ID,
            'aud': client.API_HOST_URI_FORMAT.format(HOST),
            'exp': 302,
            'state': STATE,
            'response_type': 'code',
            'duo_uname': USERNAME,
            'use_duo_code_attribute': True,
            'dest_app_name': DEST_APP_NAME,
            'dest_app_id': DEST_APP_ID,
        }

        self._assert_client_creates_expected_uri(
            duo_client, expected_jwt_args,
            dest_app_name=DEST_APP_NAME, dest_app_id=DEST_APP_ID)

    @patch('time.time', MagicMock(return_value=2))
    def test_display_username(self):
        """
        Test create_auth_url includes display_username when given
        """
        duo_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

        expected_jwt_args = {
            'scope': 'openid',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'iss': CLIENT_ID,
            'aud': client.API_HOST_URI_FORMAT.format(HOST),
            'exp': 302,
            'state': STATE,
            'response_type': 'code',
            'duo_uname': USERNAME,
            'use_duo_code_attribute': True,
            'display_username': DISPLAY_USERNAME,
        }

        self._assert_client_creates_expected_uri(
            duo_client, expected_jwt_args, display_username=DISPLAY_USERNAME)

    @patch('time.time', MagicMock(return_value=2))
    def test_dest_app_name_without_dest_app_id(self):
        """
        Test create_auth_url includes dest_app_name on its own
        """
        duo_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

        expected_jwt_args = {
            'scope': 'openid',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'iss': CLIENT_ID,
            'aud': client.API_HOST_URI_FORMAT.format(HOST),
            'exp': 302,
            'state': STATE,
            'response_type': 'code',
            'duo_uname': USERNAME,
            'use_duo_code_attribute': True,
            'dest_app_name': DEST_APP_NAME,
        }

        self._assert_client_creates_expected_uri(
            duo_client, expected_jwt_args, dest_app_name=DEST_APP_NAME)

    @patch('time.time', MagicMock(return_value=2))
    def test_max_age(self):
        """
        Test create_auth_url includes max_age when given
        """
        duo_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

        expected_jwt_args = {
            'scope': 'openid',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'iss': CLIENT_ID,
            'aud': client.API_HOST_URI_FORMAT.format(HOST),
            'exp': 302,
            'state': STATE,
            'response_type': 'code',
            'duo_uname': USERNAME,
            'use_duo_code_attribute': True,
            'max_age': 3600,
        }

        self._assert_client_creates_expected_uri(
            duo_client, expected_jwt_args, max_age=3600)

    @patch('time.time', MagicMock(return_value=2))
    def test_max_age_zero(self):
        """
        Test create_auth_url includes a max_age of zero, which forces
        interactive reauthentication rather than being treated as unset
        """
        duo_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

        expected_jwt_args = {
            'scope': 'openid',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'iss': CLIENT_ID,
            'aud': client.API_HOST_URI_FORMAT.format(HOST),
            'exp': 302,
            'state': STATE,
            'response_type': 'code',
            'duo_uname': USERNAME,
            'use_duo_code_attribute': True,
            'max_age': 0,
        }

        self._assert_client_creates_expected_uri(
            duo_client, expected_jwt_args, max_age=0)

    @patch('time.time', MagicMock(return_value=2))
    def test_prompt(self):
        """
        Test create_auth_url includes prompt when given
        """
        duo_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

        expected_jwt_args = {
            'scope': 'openid',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'iss': CLIENT_ID,
            'aud': client.API_HOST_URI_FORMAT.format(HOST),
            'exp': 302,
            'state': STATE,
            'response_type': 'code',
            'duo_uname': USERNAME,
            'use_duo_code_attribute': True,
            'prompt': 'login',
        }

        self._assert_client_creates_expected_uri(
            duo_client, expected_jwt_args, prompt='login')

    def _assert_client_creates_expected_uri(self, duo_client, expected_jwt_args, **kwargs):
        authorize_endpoint = \
            client.OAUTH_V1_AUTHORIZE_ENDPOINT.format(HOST)

        expected_all_args = {
            'response_type': 'code',
            'client_id': CLIENT_ID,
            'request': jwt.encode(expected_jwt_args, CLIENT_SECRET, algorithm='HS512'),
        }

        encoded_all_args = urlencode(expected_all_args)

        expected_authorization_uri = "{}?{}".format(authorize_endpoint,
                                                    encoded_all_args)
        actual_authorization_uri = duo_client.create_auth_url(USERNAME, STATE, **kwargs)

        self.assertEqual(expected_authorization_uri, actual_authorization_uri)


if __name__ == '__main__':
    unittest.main()
