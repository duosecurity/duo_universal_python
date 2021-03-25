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

    def _assert_client_creates_expected_uri(self, duo_client, expected_jwt_args):
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
        actual_authorization_uri = duo_client.create_auth_url(USERNAME, STATE)

        self.assertEqual(expected_authorization_uri, actual_authorization_uri)


if __name__ == '__main__':
    unittest.main()
