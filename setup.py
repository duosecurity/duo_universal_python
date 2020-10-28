from setuptools import setup
import os.path
import codecs


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


requirements_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')

with open(requirements_filename) as fd:
    install_requires = [i.strip() for i in fd.readlines()]

requirements_dev_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'tests/requirements.txt')

with open(requirements_dev_filename) as fd:
    tests_require = [i.strip() for i in fd.readlines()]

long_description_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'README.md')

with open(long_description_filename) as fd:
    long_description = fd.read()

setup(
    name='duo_universal',
    version=get_version("duo_universal/version.py"),
    packages=['duo_universal'],
    package_data={'duo_universal': ['ca_certs.pem']},
    url='https://github.com/duosecurity/duo_universal_python',
    license='BSD',
    author='Duo Security, Inc.',
    author_email='support@duosecurity.com',
    description='Duo Web SDK for two-factor authentication',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License'
    ],
    install_requires=install_requires,
    tests_require=tests_require
)
