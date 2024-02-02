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
PROXY_HOST = "http://proxy.example.com:8001"
EXP_SECONDS = client.FIVE_MINUTES_IN_SECONDS
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
                                              HOST, REDIRECT_URI, EXP_SECONDS)
            self.assertEqual(e, client.ERR_CLIENT_ID)

    def test_long_client_id(self):
        """
        Test long client_id throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(LONG_CLIENT_ID, CLIENT_SECRET,
                                              HOST, REDIRECT_URI, EXP_SECONDS)
            self.assertEqual(e, client.ERR_CLIENT_ID)

    def test_no_client_id(self):
        """
        Test no client_id throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(NONE, CLIENT_SECRET,
                                              HOST, REDIRECT_URI, EXP_SECONDS)
            self.assertEqual(e, client.ERR_CLIENT_ID)

    def test_short_client_secret(self):
        """
        Test short client_secret throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, SHORT_CLIENT_SECRET,
                                              HOST, REDIRECT_URI, EXP_SECONDS)
            self.assertEqual(e, client.ERR_CLIENT_SECRET)

    def test_long_client_secret(self):
        """
        Test long client_secret throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, LONG_CLIENT_SECRET,
                                              HOST, REDIRECT_URI, EXP_SECONDS)
            self.assertEqual(e, client.ERR_CLIENT_SECRET)

    def test_no_client_secret(self):
        """
        Test no client_secret throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, NONE,
                                              HOST, REDIRECT_URI, EXP_SECONDS)
            self.assertEqual(e, client.ERR_CLIENT_SECRET)

    def test_no_host(self):
        """
        Test no host throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, CLIENT_SECRET,
                                              NONE, REDIRECT_URI, EXP_SECONDS)
            self.assertEqual(e, client.ERR_API_HOST)

    def test_no_redirect_uri(self):
        """
        Test no redirect_uri throws DuoException
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, CLIENT_SECRET,
                                              HOST, NONE, EXP_SECONDS)
            self.assertEqual(e, client.ERR_REDIRECT_URI)

    def test_exp_seconds_too_long(self):
        """
        Test to validate that a user can't set an expiry longer than 5 minutes.
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI, 2 * EXP_SECONDS)
            self.assertEqual(e, client.ERR_EXP_SECONDS_TOO_LONG)
        # Even if the end user forcefully sets the expiry, ensure the clamped value is in spec.
        self.client._exp_seconds = 2 * EXP_SECONDS
        self.assertEqual(self.client._clamped_expiry_duration, client.FIVE_MINUTES_IN_SECONDS)

    def test_exp_seconds_too_short(self):
        """
        Test to validate that a user can't set an expiry shorter than 0.
        """
        with self.assertRaises(client.DuoException) as e:
            self.client._validate_init_config(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI, -1)
            self.assertEqual(e, client.ERR_EXP_SECONDS_TOO_SHORT)

    def test_successful(self):
        """
        Test successful _validate_init_config
        """
        self.client._validate_init_config(CLIENT_ID, CLIENT_SECRET,
                                          HOST, REDIRECT_URI, EXP_SECONDS)

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

    def test_default_duo_code_attribute(self):
        self.assertEqual(self.client._use_duo_code_attribute, True)

    def test_proxy_unset(self):
        plain_client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)
        self.assertEqual(plain_client._http_proxy, NONE)

    def test_proxy_set_on_args(self):
        client_with_proxy = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI, NONE, True, PROXY_HOST)
        self.assertEqual(client_with_proxy._http_proxy, {'https': PROXY_HOST})

    def test_proxy_set_on_kwargs(self):
        client_with_proxy = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI, http_proxy=PROXY_HOST)
        self.assertEqual(client_with_proxy._http_proxy, {'https': PROXY_HOST})

    def test_proxy_set_off_args(self):
        client_with_no_proxy = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI, NONE, True, NONE)
        self.assertEqual(client_with_no_proxy._http_proxy, NONE)

    def test_proxy_set_off_kwargs(self):
        client_with_no_proxy = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI, http_proxy=NONE)
        self.assertEqual(client_with_no_proxy._http_proxy, NONE)


if __name__ == '__main__':
    unittest.main()
