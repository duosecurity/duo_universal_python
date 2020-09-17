from six.moves.urllib.parse import urlencode
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

EXPECTED_JWT_ARGS = {
    'scope': 'openid',
    'redirect_uri': REDIRECT_URI,
    'client_id': CLIENT_ID,
    'iss': CLIENT_ID,
    'aud': client.API_HOST_URI_FORMAT.format(HOST),
    'exp': 302,
    'state': STATE,
    'response_type': 'code',
    'duo_uname': USERNAME,
    'use_duo_code_attribute': 'True',
}

EXPECTED_ALL_ARGS = {
    'response_type': 'code',
    'client_id': CLIENT_ID,
    'request': jwt.encode(EXPECTED_JWT_ARGS, CLIENT_SECRET, algorithm='HS512'),
}


class TestCreateAuthUrl(unittest.TestCase):

    def setUp(self):
        self.client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

    @patch('time.time', MagicMock(return_value=2))
    def test_encrypted_jwt(self):
        """
        Test create_auth_url returns a valid authorization uri
        """
        authorize_endpoint = \
            client.OAUTH_V1_AUTHORIZE_ENDPOINT.format(HOST)
        encoded_all_args = urlencode(EXPECTED_ALL_ARGS)

        expected_authorization_uri = "{}?{}".format(authorize_endpoint,
                                                    encoded_all_args)
        actual_authorization_uri = self.client.create_auth_url(USERNAME, STATE)

        self.assertEqual(expected_authorization_uri, actual_authorization_uri)


if __name__ == '__main__':
    unittest.main()
