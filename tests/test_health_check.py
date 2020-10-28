from mock import MagicMock, patch
from duo_universal import client
import requests
import unittest

CLIENT_ID = "DIXXXXXXXXXXXXXXXXXX"
WRONG_CLIENT_ID = "DIXXXXXXXXXXXXXXXXXY"
CLIENT_SECRET = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
HOST = "api-XXXXXXX.test.duosecurity.com"
REDIRECT_URI = "https://www.example.com"

WRONG_CERT_ERROR = 'certificate verify failed'
SUCCESS_CHECK = {
    'response': {'timestamp': 1573068322},
    'stat': 'OK'
}
ERROR_TIMEOUT = "Connection to api-xxxxxxx.test.duosecurity.com timed out."
ERROR_NETWORK_CONNECTION_FAILED = "Failed to establish a new connection"
ERROR_WRONG_CLIENT_ID = {
    'message': 'invalid_client',
    'code': 40002, 'stat': 'FAIL',
    'message_detail': 'The provided client_assertion was invalid.',
    'timestamp': 1573053670
}


class TestHealthCheck(unittest.TestCase):

    def setUp(self):
        self.client = client.Client(CLIENT_ID, CLIENT_SECRET, HOST, REDIRECT_URI)
        self.client_wrong_client_id = client.Client(WRONG_CLIENT_ID, CLIENT_SECRET,
                                                    HOST, REDIRECT_URI)

    @patch('requests.post', MagicMock(side_effect=requests.Timeout(ERROR_TIMEOUT)))
    def test_health_check_timeout_error(self):
        """
        Test health check failure due to a timeout
        """
        with self.assertRaises(client.DuoException) as e:
            self.client.health_check()
            self.assertEqual(e, ERROR_TIMEOUT)

    @patch('requests.post', MagicMock(side_effect=requests.ConnectionError(
                                      ERROR_NETWORK_CONNECTION_FAILED)))
    def test_health_check_duo_down_error(self):
        """
        Test health check failure due to a connection error,
        either because it cannot reach Duo or the network is down
        """
        with self.assertRaises(client.DuoException) as e:
            self.client.health_check()
            self.assertEqual(e, ERROR_NETWORK_CONNECTION_FAILED)

    @patch('requests.post')
    @patch('json.loads')
    def test_health_check_wrong_client_id(self, json_mock, requests_mock):
        """
        Test health check failure due to a bad client_id
        """
        requests_mock.return_value.content = ERROR_WRONG_CLIENT_ID
        json_mock.return_value = ERROR_WRONG_CLIENT_ID
        with self.assertRaises(client.DuoException):
            self.client_wrong_client_id.health_check()

    @patch('requests.post')
    def test_health_check_bad_cert(self, requests_mock):
        """
        Test health check failure due to bad Duo Cert
        """
        requests_mock.side_effect = requests.exceptions.SSLError(WRONG_CERT_ERROR)
        with self.assertRaises(client.DuoException) as e:
            self.client.health_check()
            self.assertEqual(e, WRONG_CERT_ERROR)

    @patch('requests.post')
    @patch('json.loads')
    def test_health_check_success(self, json_mock, requests_mock):
        """
        Successful health check
        """
        requests_mock.return_value.content = SUCCESS_CHECK
        json_mock.return_value = SUCCESS_CHECK
        result = self.client.health_check()
        self.assertEqual(result['stat'], 'OK')


if __name__ == '__main__':
    unittest.main()
