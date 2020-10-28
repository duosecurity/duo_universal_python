from mock import MagicMock, patch
from duo_universal import client
import unittest
import requests
import jwt
import time

CLIENT_ID = "DIXXXXXXXXXXXXXXXXXX"
WRONG_CLIENT_ID = "DIXXXXXXXXXXXXXXXXXY"
CLIENT_SECRET = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
WRONG_CLIENT_SECRET = "wrongclientidwrongclientidwrongclientidw"
HOST = "api-XXXXXXX.test.duosecurity.com"
REDIRECT_URI = "https://www.example.com"
DUO_CODE = "deadbeefdeadbeefdeadbeefdeadbeef"
WRONG_DUO_CODE = "deadbeefdeadbeefdeadbeefdeadbeee"
USERNAME = "username"
WRONG_USERNAME = "wrong_username"
NONCE = "abcdefghijklmnopqrstuvwxyzabcdef"
WRONG_NONCE = "bbcceeggiikkmmooqqssuuwwyyaaccee"

WRONG_CERT_ERROR = 'certificate verify failed'
ERROR_TIMEOUT = "Connection to api-xxxxxxx.test.duosecurity.com timed out."
ERROR_NETWORK_CONNECTION_FAILED = "Failed to establish a new connection"

REQUESTS_POST_ERROR = 400
REQUESTS_POST_SUCCESS = 200
ERROR_WRONG_DUO_CODE = {
    'error': 'invalid_grant',
    'error_description': 'The provided authorization grant or '
                         'refresh token is invalid, expired, '
                         'revoked, does not match '
                         'the redirection URI.'
}
ERROR_WRONG_CLIENT_ID = {
    'error': 'invalid_client',
    'error_description': 'Invalid Client assertion: '
                         'The `iss` claim must match '
                         'the supplied client_id'
}
NONE = None


class TestExchangeAuthCodeInputs(unittest.TestCase):

    def setUp(self):
        self.client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)
        self.client_wrong_client_id = client.Client(WRONG_CLIENT_ID, CLIENT_SECRET,
                                                    HOST, REDIRECT_URI)
        self.jwt_decode = {
            "auth_result": {
                "result": "allow",
                "status": "allow",
                "status_msg": "Login Successful",
            },
            "aud": CLIENT_ID,
            "auth_time": time.time(),
            "exp": time.time() + client.FIVE_MINUTES_IN_SECONDS,
            "iat": time.time() + 1,
            "iss": "https://{}/oauth/v1/token".format(HOST),
            "preferred_username": USERNAME,
        }

    def test_no_duo_code(self):
        """
        Test that exchange_authorization_code_for_2fa_result
        throws a DuoException if there is no duo_code
        """
        with self.assertRaises(client.DuoException) as e:
            self.client.exchange_authorization_code_for_2fa_result(NONE, USERNAME)
            self.assertEqual(e, client.ERR_DUO_CODE)

    @patch('requests.post', MagicMock(
        side_effect=requests.Timeout(ERROR_TIMEOUT)))
    def test_exchange_authorization_code_timeout_error(self):
        """
        Test that exchange_authorization_code_for_2fa_result
        throws DuoException if the request times out
        """
        with self.assertRaises(client.DuoException) as e:
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)
            self.assertEqual(e, ERROR_TIMEOUT)

    @patch('requests.post', MagicMock(
        side_effect=requests.ConnectionError(ERROR_NETWORK_CONNECTION_FAILED)))
    def test_exchange_authorization_code_duo_down_error(self):
        """
        Test that exchange_authorization_code_for_2fa_result
        throws DuoException if the network connection failed
        """
        with self.assertRaises(client.DuoException) as e:
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)
            self.assertEqual(e, ERROR_NETWORK_CONNECTION_FAILED)

    @patch('requests.post')
    @patch('json.loads')
    def test_exchange_authorization_code_wrong_client_id(self,
                                                         mock_json_loads,
                                                         mock_post):
        """
        Test that a wrong integration key throws a DuoException
        """
        mock_post.return_value.status_code = REQUESTS_POST_ERROR
        mock_json_loads.return_value = ERROR_WRONG_CLIENT_ID

        with self.assertRaises(client.DuoException) as e:
            self.client_wrong_client_id.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)
            self.assertEqual(e['error'], 'invalid_grant')

    @patch('requests.post')
    @patch('json.loads')
    def test_exchange_authorization_code_wrong_duo_code(self,
                                                        mock_json_loads,
                                                        mock_post):
        """
        Test that a wrong duo_code exchanged with Duo throws a DuoException
        """
        mock_post.return_value.status_code = REQUESTS_POST_ERROR
        mock_json_loads.return_value = ERROR_WRONG_DUO_CODE

        with self.assertRaises(client.DuoException) as e:
            self.client.exchange_authorization_code_for_2fa_result(WRONG_DUO_CODE, USERNAME)
            self.assertEqual(e['error'], 'invalid_client')

    @patch('requests.post')
    def test_exchange_authorization_code_wrong_cert(self, requests_mock):
        """
        Test that a wrong Duo Cert causes the client to throw a DuoException
        """
        requests_mock.side_effect = requests.exceptions.SSLError(WRONG_CERT_ERROR)
        with self.assertRaises(client.DuoException) as e:
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)
            self.assertEqual(e, WRONG_CERT_ERROR)

    @patch('requests.post')
    @patch('jwt.decode')
    def test_exchange_authorization_code_success(self, mock_jwt, mock_post):
        """
        Test that a successful authorization duo_code exchange
        returns a successful jwt
        """
        mock_post.return_value.status_code = REQUESTS_POST_SUCCESS
        mock_jwt.return_value = self.jwt_decode
        output = self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)
        self.assertEqual(output, self.jwt_decode)

    @patch('requests.post')
    def test_exchange_authorization_nonce(self, mock_post):
        """
        Test that a good nonce succeeds
        """
        mock_post.return_value = self.generate_post_return_value('nonce', NONCE)
        output = self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME, NONCE)
        self.assertEqual(output, self.jwt_decode)

    @patch('requests.post')
    def test_invalid_token_signature_failure(self, mock_post):
        """
        Test that an altered token fails signature validation
        """
        # Invalid token created by altering the payload of a valid token
        mock_response = MockResponse(status_code=200, content={"id_token": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhYmNkZWYiLCJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjJ9.kmo4YemI0g8l9fGV1z5Obec3oEQdeena21lFrDrID9O2NmPC-6Oh2InZ0Gd34EhqevZ5dqRf-nfYNAL6nDS33A"})
        mock_post.return_value = mock_response
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)

    @patch('requests.post')
    def test_invalid_signing_key_failure(self, mock_post):
        """
        Test that a token signed with the wrong secret throws an error
        """
        encoded_jwt = jwt.encode(self.jwt_decode, WRONG_CLIENT_SECRET, algorithm='HS512')
        id_token = {"id_token": encoded_jwt}
        mock_post.return_value = MockResponse(id_token)
        with self.assertRaises(client.DuoException) as e:
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)
            self.assertEqual(e.message, "Signature verification failed")

    @patch('requests.post')
    def test_exchange_authorization_wrong_preferred_username(self, mock_post):
        """
        Test that a wrong preferred name throws an error
        """
        mock_post.return_value = self.generate_post_return_value('preferred_username', WRONG_USERNAME)
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)

    @patch('requests.post')
    def test_exchange_authorization_wrong_aud(self, mock_post):
        """
        Test that a wrong audience throws an error
        """
        mock_post.return_value = self.generate_post_return_value('aud', WRONG_CLIENT_ID)
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)

    @patch('requests.post')
    def test_exchange_authorization_no_aud(self, mock_post):
        """
        Test that no audience throws an error
        """
        mock_post.return_value = self.pop_post_return_value('aud')
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)

    @patch('requests.post')
    def test_exchange_authorization_wrong_iss(self, mock_post):
        """
        Test that a wrong issuer throws an error
        """
        mock_post.return_value = self.generate_post_return_value('iss', HOST)
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)

    @patch('requests.post')
    def test_exchange_authorization_no_preferred_username(self, mock_post):
        """
        Test that no preferred name throws an error
        """
        mock_post.return_value = self.pop_post_return_value('preferred_username')
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)

    @patch('requests.post')
    def test_exchange_authorization_no_iat(self, mock_post):
        """
        Test that no iat throws an error
        """
        mock_post.return_value = self.pop_post_return_value('iat')
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)

    @patch('requests.post')
    def test_exchange_authorization_no_exp(self, mock_post):
        """
        Test that no expiration throws an error
        """
        mock_post.return_value = self.pop_post_return_value('exp')
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)

    @patch('requests.post')
    def test_exchange_authorization_past_exp(self, mock_post):
        """
        Test that an expired auth throws an error
        """
        mock_post.return_value = self.generate_post_return_value('exp', 1)
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME)

    @patch('requests.post')
    def test_exchange_authorization_wrong_nonce(self, mock_post):
        """
        Test that a wrong nonce throws an error
        """
        mock_post.return_value = self.generate_post_return_value('nonce', WRONG_NONCE)
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME, NONCE)

    @patch('requests.post')
    @patch('jwt.decode')
    def test_exchange_authorization_no_nonce(self, mock_jwt, mock_post):
        """
        Test that a no nonce when one is expected throws an error
        """
        mock_post.return_value.status_code = REQUESTS_POST_SUCCESS
        mock_jwt.return_value = self.jwt_decode
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, USERNAME, NONCE)

    @patch('requests.post')
    @patch('jwt.decode')
    def test_exchange_authorization_no_username(self, mock_jwt, mock_post):
        """
        Test that a no username throws an error
        """
        mock_post.return_value.status_code = REQUESTS_POST_SUCCESS
        mock_jwt.return_value = self.jwt_decode
        with self.assertRaises(client.DuoException):
            self.client.exchange_authorization_code_for_2fa_result(DUO_CODE, None)

    def generate_post_return_value(self, key, value):
        self.jwt_decode[key] = value
        id_token = {"id_token": jwt.encode(self.jwt_decode, CLIENT_SECRET, algorithm='HS512')}
        return MockResponse(id_token)

    def pop_post_return_value(self, key):
        self.jwt_decode.pop(key)
        id_token = {"id_token": jwt.encode(self.jwt_decode, CLIENT_SECRET, algorithm='HS512')}
        return MockResponse(id_token)


class MockResponse:
    def __init__(self, content, status_code=200):
        self.status_code = status_code
        self.content = content

    def json(self):
        return self.content


if __name__ == '__main__':
    unittest.main()
