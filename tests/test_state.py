from duo_universal import client
import unittest

CLIENT_ID = "DIXXXXXXXXXXXXXXXXXX"
CLIENT_SECRET = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
LONG_CLIENT_SECRET = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeeff"
HOST = "api-XXXXXXX.test.duosecurity.com"
REDIRECT_URI = "https://www.example.com"

SHORT_STATE_LENGTH = client.MINIMUM_STATE_LENGTH - 1
ZERO_LENGTH = 0


class TestGenerateState(unittest.TestCase):

    def setUp(self):
        self.client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

    def test_generate_state_length(self):
        """
        Test generate_state outputs a string
        that has a length of client.STATE_LENGTH
        """
        output = self.client.generate_state()
        self.assertEqual(client.STATE_LENGTH, len(output))

    def test_generate_state_random(self):
        """
        Test that running generate_state twice gives two different outputs
        """
        first_output = self.client.generate_state()
        second_output = self.client.generate_state()
        self.assertNotEqual(first_output, second_output)


class TestGenerateRandomAlphanumeric(unittest.TestCase):

    def setUp(self):
        self.client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

    def test_zero_length(self):
        """
        Test zero length throws DuoException error
        """
        with self.assertRaises(ValueError) as e:
            self.client._generate_rand_alphanumeric(ZERO_LENGTH)
            self.assertEqual(e, client.ERR_GENERATE_LEN)

    def test_short_length(self):
        """
        Test short length throws DuoException error
        """
        with self.assertRaises(ValueError) as e:
            self.client._generate_rand_alphanumeric(SHORT_STATE_LENGTH)
            self.assertEqual(e, client.ERR_GENERATE_LEN)

    def test_success(self):
        """
        Test that _generate_rand_alphanumeric
        returns string with length STATE_LENGTH
        """
        generate = self.client._generate_rand_alphanumeric(client.STATE_LENGTH)
        self.assertEqual(client.STATE_LENGTH, len(generate))


if __name__ == '__main__':
    unittest.main()
