# Duo Universal Python SDK

[![Build Status](https://github.com/duosecurity/duo_universal_python/workflows/Python%20CI/badge.svg)](https://github.com/duosecurity/duo_universal_python/actions)
[![Issues](https://img.shields.io/github/issues/duosecurity/duo_universal_python)](https://github.com/duosecurity/duo_universal_python/issues)
[![Forks](https://img.shields.io/github/forks/duosecurity/duo_universal_python)](https://github.com/duosecurity/duo_universal_python/network/members)
[![Stars](https://img.shields.io/github/stars/duosecurity/duo_universal_python)](https://github.com/duosecurity/duo_universal_python/stargazers)
[![License](https://img.shields.io/badge/License-View%20License-orange)](https://github.com/duosecurity/duo_universal_python/blob/master/LICENSE)


This SDK allows a web developer to quickly add Duo's interactive, self-service, two-factor authentication to any Python web login form. Both Python 2 and Python 3 are supported.

What's here:
* `duo_universal` - The Python Duo SDK for interacting with the Duo Universal Prompt
* `demo` - An example web application with Duo integrated
* `tests` - Test cases

## Getting Started
To use the SDK in your existing development environment, install it from pypi (https://pypi.org/project/duo_universal).
```
pip install duo_universal
```
Once it's installed, see our developer documentation at https://duo.com/docs/duoweb and `demo/app.py` in this repo for guidance on integrating Duo 2FA into your web application.

## Contribute
To contribute, fork this repo and make a pull request with your changes when they're ready. 

If you're not already working from a dedicated development environment, it's recommended a virtual environment is used. Assuming a virtual environment named `env`, create and activate the environment:
```
# Python 3
python -m venv env
source env/bin/activate

# Python 2
virtualenv env
source env/bin/activate
```

Build and install the SDK from source:
```
pip install -r requirements.txt
pip install .
```

## Tests
Install the test requirements:
```
cd tests
pip install -r requirements.txt
```
Then run tests from the `test` directory:
```
# Run an individual test file
python <test_name>.py

# Run all tests with nose
nose2

# Run all tests with unittest
python -m unittest
```

## Lint
```
flake8
```

## Support

Please report any bugs, feature requests, or issues to us directly at support@duosecurity.com.

Thank you for using Duo!

https://duo.com/
