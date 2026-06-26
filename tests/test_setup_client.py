from unittest.mock import patch, MagicMock
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


class TestDisableCaPinning(unittest.TestCase):

    def test_default_is_pinning_enabled(self):
        c = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)
        self.assertFalse(c._disable_ca_pinning)
        self.assertEqual(c._duo_certs, client.DEFAULT_CA_CERT_PATH)

    def test_disable_ca_pinning_true(self):
        c = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI,
                          disable_ca_pinning=True)
        self.assertTrue(c._disable_ca_pinning)
        self.assertTrue(c._duo_certs)

    def test_disable_ca_pinning_with_default_duo_certs(self):
        c = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI,
                          duo_certs=client.DEFAULT_CA_CERT_PATH, disable_ca_pinning=True)
        self.assertTrue(c._disable_ca_pinning)
        self.assertTrue(c._duo_certs)

    def test_disable_ca_pinning_with_none_duo_certs(self):
        c = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI,
                          duo_certs=None, disable_ca_pinning=True)
        self.assertTrue(c._disable_ca_pinning)
        self.assertTrue(c._duo_certs)

    def test_disable_ca_pinning_with_custom_duo_certs_raises(self):
        with self.assertRaises(client.DuoException) as ctx:
            client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI,
                          duo_certs=CA_CERT_NEW, disable_ca_pinning=True)
        self.assertIn("Cannot both disable CA pinning", str(ctx.exception))

    def test_disable_ca_pinning_with_disable_duo_certs_raises(self):
        with self.assertRaises(client.DuoException) as ctx:
            client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI,
                          duo_certs="DISABLE", disable_ca_pinning=True)
        self.assertIn("Cannot both disable CA pinning", str(ctx.exception))

    def test_disable_ca_pinning_false_preserves_existing_behavior(self):
        c = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI,
                          disable_ca_pinning=False)
        self.assertEqual(c._duo_certs, client.DEFAULT_CA_CERT_PATH)


class TestDisableCaPinningRequests(unittest.TestCase):

    @patch('requests.post')
    def test_health_check_pinning_disabled_uses_system_trust_store(self, requests_mock):
        requests_mock.return_value = MagicMock(content=b'{"stat": "OK", "response": {"timestamp": 1}}')
        c = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI,
                          disable_ca_pinning=True)
        c.health_check()
        _, kwargs = requests_mock.call_args
        self.assertTrue(kwargs['verify'])
        self.assertIsNot(kwargs['verify'], client.DEFAULT_CA_CERT_PATH)

    @patch('requests.post')
    def test_health_check_pinning_enabled_uses_bundled_certs(self, requests_mock):
        requests_mock.return_value = MagicMock(content=b'{"stat": "OK", "response": {"timestamp": 1}}')
        c = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)
        c.health_check()
        _, kwargs = requests_mock.call_args
        self.assertEqual(kwargs['verify'], client.DEFAULT_CA_CERT_PATH)

    @patch('requests.post')
    def test_token_exchange_pinning_disabled_uses_system_trust_store(self, requests_mock):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id_token': 'fake'}
        requests_mock.return_value = mock_response
        c = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI,
                          disable_ca_pinning=True)
        try:
            c.exchange_authorization_code_for_2fa_result('code', 'user')
        except client.DuoException:
            pass
        _, kwargs = requests_mock.call_args
        self.assertTrue(kwargs['verify'])
        self.assertIsNot(kwargs['verify'], client.DEFAULT_CA_CERT_PATH)

    @patch('requests.post')
    def test_token_exchange_pinning_enabled_uses_bundled_certs(self, requests_mock):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id_token': 'fake'}
        requests_mock.return_value = mock_response
        c = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)
        try:
            c.exchange_authorization_code_for_2fa_result('code', 'user')
        except client.DuoException:
            pass
        _, kwargs = requests_mock.call_args
        self.assertEqual(kwargs['verify'], client.DEFAULT_CA_CERT_PATH)


if __name__ == '__main__':
    unittest.main()
