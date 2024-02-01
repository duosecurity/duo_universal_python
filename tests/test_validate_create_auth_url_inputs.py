from duo_universal import client
import unittest

CLIENT_ID = "DIXXXXXXXXXXXXXXXXXX"
CLIENT_SECRET = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
HOST = "api-XXXXXXX.test.duosecurity.com"
REDIRECT_URI = "https://www.example.com"
USERNAME = "user1"
STATE = "deadbeefdeadbeefdeadbeefdeadbeefdead"
SHORT_STATE = STATE[:client.MINIMUM_STATE_LENGTH - 1]
LONG_LENGTH = "a" * (client.MAXIMUM_STATE_LENGTH + 1)
NONE = None


class TestCreateAuthUrlInputs(unittest.TestCase):

    def setUp(self):
        self.client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

    def test_no_state(self):
        """
        Test _validate_create_auth_url_inputs
        throws a DuoException if the state is None
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_create_auth_url_inputs(USERNAME, NONE)
            self.assertEqual(e, client.ERR_STATE)

    def test_short_state(self):
        """
        Test _validate_create_auth_url_inputs
        throws a DuoException if the state is too short
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_create_auth_url_inputs(USERNAME, SHORT_STATE)
            self.assertEqual(e, client.ERR_STATE)

    def test_long_state(self):
        """
        Test _validate_create_auth_url_inputs
        throws a DuoException if the state is too long
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_create_auth_url_inputs(USERNAME, LONG_LENGTH)
            self.assertEqual(e, client.ERR_STATE)

    def test_short_nonce(self):
        """
        Test _validate_create_auth_url_inputs
        throws a DuoException if the nonce is set and is too short
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_create_auth_url_inputs(USERNAME, STATE, nonce=SHORT_STATE)
            self.assertEqual(e, client.ERR_NONCE_LEN)

    def test_long_nonce(self):
        """
        Test _validate_create_auth_url_inputs
        throws a DuoException if the nonce is set and is too long
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_create_auth_url_inputs(USERNAME, STATE, nonce=LONG_LENGTH)
            self.assertEqual(e, client.ERR_NONCE_LEN)

    def test_no_username(self):
        """
        Test _validate_create_auth_url_inputs
        throws a DuoException if the username is None
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_create_auth_url_inputs(NONE, STATE)
            self.assertEqual(e, client.ERR_USERNAME)

    def test_success(self):
        """
        Test _validate_create_auth_url_inputs
        does not throw an error for valid inputs
        """
        self.client._validate_create_auth_url_inputs(USERNAME, STATE)

    def test_success_with_nonce(self):
        """
        Test _validate_create_auth_url_inputs
        does not throw an error for valid inputs
        """
        self.client._validate_create_auth_url_inputs(USERNAME, STATE, nonce=STATE)


if __name__ == '__main__':
    unittest.main()
