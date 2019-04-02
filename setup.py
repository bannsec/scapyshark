# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os, sys, ast
from scapyshark.version import version

here = os.path.abspath(os.path.dirname(__file__))

#with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()
long_description = "See website for more info."

setup(
    name='scapyshark',
    version=version,
    description='Wireshark, but with Scapy.',
    long_description=long_description,
    url='https://github.com/bannsec/scapyshark',
    author='Michael Bann',
    author_email='self@bannsecurity.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console'
    ],
    keywords='wireshark scapy python tcpdump',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    # Using github version since pypi version is old and dns responses are broken in it
    # Need latest version of prettytable for max_table variables and printing
    install_requires=['scapy @ https://github.com/secdev/scapy/archive/master.zip', 'prettytable @ https://github.com/jazzband/prettytable/archive/master.zip', 'urwid', 'requests', 'pexpect'],
    entry_points={
        'console_scripts': [
            'scapyshark = scapyshark.scapyshark:main',
        ],
    },
)

