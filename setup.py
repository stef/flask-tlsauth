import os
from setuptools import setup,find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "flask_tlsauth",
    version = "0.1",
    author = "Stefan Marsiske",
    author_email = "s@ctrlc.hu",
    license = "BSD",
    keywords = "flask crypto authentication TLS certificate x509 CA",
    packages = find_packages(),
    package_data = { '': ['templates/*.html'], },
    include_package_data=True,
    install_requires = ['tlsauth', 'Flask'],
    url = "http://packages.python.org/flask_tlsauth",
    description = "Flask extension implementing TLS Authentication - simple client certificate CA inclusive",
    long_description=read('README.org'),
    classifiers = ["Development Status :: 4 - Beta",
                   "License :: OSI Approved :: BSD License",
                   "Topic :: Security :: Cryptography",
                   "Environment :: Web Environment",
                 ],
)
