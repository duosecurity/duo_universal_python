from duo_universal import client
import unittest

CLIENT_ID = "DIXXXXXXXXXXXXXXXXXX"
LONG_CLIENT_ID = "DIXXXXXXXXXXXXXXXXXXZ"
SHORT_CLIENT_ID = "DIXXXXXXXXXXXXXXXXX"
CLIENT_SECRET = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
SHORT_CLIENT_SECRET = "deadbeefdeadbeefdeadbeefdeadbeefdeadbee"
LONG_CLIENT_SECRET = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeeff"
HOST = "api-XXXXXXX.test.duosecurity.com"
WRONG_HOST = "api-XXXXXXX.test.duosecurity.com"
REDIRECT_URI = "https://www.example.com"
CA_CERT_NEW = "/path/to/cert/ca_cert_new.pem"
NONE = None


class TestCheckConf(unittest.TestCase):

    def setUp(self):
        self.client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)

    def test_short_client_id(self):
        """
        Test short client_id throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(SHORT_CLIENT_ID, CLIENT_SECRET,
                                              HOST, REDIRECT_URI)
            self.assertEqual(e, client.ERR_CLIENT_ID)

    def test_long_client_id(self):
        """
        Test long client_id throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(LONG_CLIENT_ID, CLIENT_SECRET,
                                              HOST, REDIRECT_URI)
            self.assertEqual(e, client.ERR_CLIENT_ID)

    def test_no_client_id(self):
        """
        Test no client_id throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(NONE, CLIENT_SECRET,
                                              HOST, REDIRECT_URI)
            self.assertEqual(e, client.ERR_CLIENT_ID)

    def test_short_client_secret(self):
        """
        Test short client_secret throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, SHORT_CLIENT_SECRET,
                                              HOST, REDIRECT_URI)
            self.assertEqual(e, client.ERR_CLIENT_SECRET)

    def test_long_client_secret(self):
        """
        Test long client_secret throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, LONG_CLIENT_SECRET,
                                              HOST, REDIRECT_URI)
            self.assertEqual(e, client.ERR_CLIENT_SECRET)

    def test_no_client_secret(self):
        """
        Test no client_secret throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, NONE,
                                              HOST, REDIRECT_URI)
            self.assertEqual(e, client.ERR_CLIENT_SECRET)

    def test_no_host(self):
        """
        Test no host throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, CLIENT_SECRET,
                                              NONE, REDIRECT_URI)
            self.assertEqual(e, client.ERR_API_HOST)

    def test_no_redirect_uri(self):
        """
        Test no redirect_uri throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, CLIENT_SECRET,
                                              HOST, NONE)
            self.assertEqual(e, client.ERR_REDIRECT_URI)

    def test_successful(self):
        """
        Test successful _validate_init_config
        """
        self.client._validate_init_config(CLIENT_ID, CLIENT_SECRET,
                                          HOST, REDIRECT_URI)

    def test_no_duo_cert(self):
        self.assertEqual(self.client._duo_certs, client.DEFAULT_CA_CERT_PATH)

    def test_new_duo_cert(self):
        new_cert_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI, CA_CERT_NEW)
        self.assertEqual(new_cert_client._duo_certs, CA_CERT_NEW)

    def test_none_duo_cert(self):
        new_cert_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI, None)
        self.assertEqual(new_cert_client._duo_certs, client.DEFAULT_CA_CERT_PATH)

    def test_disable_duo_cert(self):
        new_cert_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI, "DISABLE")
        self.assertFalse(new_cert_client._duo_certs)


if __name__ == '__main__':
    unittest.main()
