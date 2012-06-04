#!/usr/bin/env python

from setuptools import setup
from firelet.flcore import __version__

CLASSIFIERS = map(str.strip,
"""Environment :: Console
Environment :: Web Environment
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Operating System :: POSIX :: Linux
Programming Language :: Python
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
    install_requires = [
        'bottle',
        'netaddr'
        'paramiko',
    ],
    packages = ["firelet"],
    platforms=['Linux'],
    package_data={'': ['test/*',
                                        'views/*',
                                        'static/*']},
    entry_points = {
        'console_scripts': [
            'firelet_c = firelet.cli:main',
            'fireletd = firelet.fireletd:main',
        ],
    },
    scripts = ([]),
    test_suite='nose.collector',
    tests_require=['nose'],
)


