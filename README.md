# Duo Universal Python SDK

[![Build Status](https://github.com/duosecurity/duo_universal_python/workflows/Python%20CI/badge.svg)](https://github.com/duosecurity/duo_universal_python/actions)
[![Issues](https://img.shields.io/github/issues/duosecurity/duo_universal_python)](https://github.com/duosecurity/duo_universal_python/issues)
[![Forks](https://img.shields.io/github/forks/duosecurity/duo_universal_python)](https://github.com/duosecurity/duo_universal_python/network/members)
[![Stars](https://img.shields.io/github/stars/duosecurity/duo_universal_python)](https://github.com/duosecurity/duo_universal_python/stargazers)
[![License](https://img.shields.io/badge/License-View%20License-orange)](https://github.com/duosecurity/duo_universal_python/blob/master/LICENSE)


This SDK allows a web developer to quickly add Duo's interactive, self-service, two-factor authentication to any Python3 web login form. Only Python 3 is supported.

## Tested Against Python Versions:
- 3.7
- 3.8
- 3.9
- 3.10
- 3.11

## TLS 1.2 and 1.3 Support

Duo_universal_python uses Python's ssl module and OpenSSL for TLS operations. Python versions 2.7 (and higher) and 3.5 (and higher) have both TLS 1.2 and TLS 1.3 support.

## What's here:
* `duo_universal` - The Python Duo SDK for interacting with the Duo Universal Prompt
* `demo` - An example web application with Duo integrated
* `tests` - Test cases

## Getting Started
To use the SDK in your existing development environment, install it from pypi (https://pypi.org/project/duo_universal).
```
pip3 install duo_universal
```
Once it's installed, see our developer documentation at https://duo.com/docs/duoweb and `demo/app.py` in this repo for guidance on integrating Duo 2FA into your web application.

## Contribute
To contribute, fork this repo and make a pull request with your changes when they're ready. 

If you're not already working from a dedicated development environment, it's recommended a virtual environment is used. Assuming a virtual environment named `env`, create and activate the environment:
```
python3 -m venv env
source env/bin/activate
```

Build and install the SDK from source:
```
pip3 install -r requirements.txt
pip3 install .
```

## Tests
Install the test requirements:
```
cd tests
pip3 install -r requirements.txt
```
Then run tests from the `test` directory:
```
# Run an individual test file
python3 <test_name>.py

# Run all tests with unittest
python3 -m unittest
```

## Lint
```
flake8
```

## Support

Please report any bugs, feature requests, or issues to us directly at support@duosecurity.com.

Thank you for using Duo!

https://duo.com/
