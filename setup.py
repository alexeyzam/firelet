#!/usr/bin/env python

from setuptools import setup
from firelet import __version__

CLASSIFIERS = map(str.strip,
"""Environment :: Console
Environment :: Web Environment
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 2.7
Topic :: Security
""".splitlines())

setup(
    name="firelet",
    version = __version__,
    author = "Federico Ceratto",
    author_email = "federico.ceratto@gmail.com",
    description = "Distributed firewall management",
    license = "GPLv3+",
    url = "http://www.firelet.net/",
    long_description = """Firelet is a distributed firewall management tool. It provides a CLI and a web-based interface.""",
    classifiers=CLASSIFIERS,
    setup_requires=['nose>=1.0'],
    install_requires = [
        'beaker',
        'bottle',
        'netaddr',
        'paramiko',
        'setproctitle',
    ],
    packages = ["firelet"],
    platforms=['Linux'],
    package_data={'': [
        'static/*'
        'tests/*',
        'views/*',
    ]},
    entry_points = {
        'console_scripts': [
            'firelet_c = firelet.cli:main',
            'fireletd = firelet.fireletd:main',
        ],
    },
    use_2to3 = True,
    scripts = ([]),
    test_suite='nose.collector',
    tests_require=['nose'],
    data_files=[
        ('/etc/firelet', ['firelet.ini']),
    ],
)


