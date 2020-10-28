from mock import MagicMock, patch
from duo_universal import client
import unittest

CLIENT_ID = "DIXXXXXXXXXXXXXXXXXX"
CLIENT_SECRET = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
HOST = "api-XXXXXXX.test.duosecurity.com"
REDIRECT_URI = "https://www.example.com"

ERROR_TIMEOUT = "Connection to api-xxxxxxx.test.duosecurity.com timed out."
ERROR_NETWORK_CONNECTION_FAILED = "Failed to establish a new connection"

EXPIRATION_TIME = 10 + client.FIVE_MINUTES_IN_SECONDS
RAND_ALPHANUMERIC_STR = "deadbeef"

SUCCESS_JWT_ARGS = {
    'iss': CLIENT_ID,
    'sub': CLIENT_ID,
    'aud': client.OAUTH_V1_TOKEN_ENDPOINT,
    'exp': EXPIRATION_TIME,
    'jti': RAND_ALPHANUMERIC_STR
}


class TestCreateJwtArgs(unittest.TestCase):

    def setUp(self):
        self.client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

    @patch("time.time", MagicMock(return_value=10))
    def test_create_jwt_args_success(self):
        """
        Test that _create_jwt_args creates proper jwt arguments
        """
        self.client._generate_rand_alphanumeric = MagicMock(return_value=RAND_ALPHANUMERIC_STR)
        actual_jwt_args = self.client._create_jwt_args(client.OAUTH_V1_TOKEN_ENDPOINT)
        self.assertEqual(SUCCESS_JWT_ARGS, actual_jwt_args)


if __name__ == '__main__':
    unittest.main()
