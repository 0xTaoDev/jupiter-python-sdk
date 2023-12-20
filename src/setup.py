from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Jupiter Python SDK'
LONG_DESCRIPTION = 'This package allows the use of Jupiter decentralized exchange features on Solana using Python.'

# Setting up
setup(
    name="jupiter-python-sdk",
    version=VERSION,
    author="TaoDev",
    author_email="taodev3@proton.me",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
    'wheel',
    'pyaudio',
    'anchorpy',
    'anchorpy-core',
    'anyio',
    'attrs',
    'base58',
    'based58',
    'borsh-construct',
    'cachetools',
    'certifi',
    'charset-normalizer',
    'colorama',
    'construct',
    'construct-typing',
    'h11',
    'httpcore',
    'httpx',
    'idna',
    'iniconfig',
    'jsonalias',
    'jsonrpcclient',
    'more-itertools',
    'packaging',
    'pluggy',
    'psutil',
    'py',
    'pyheck',
    'pytest',
    'pytest-asyncio',
    'pytest-xprocess',
    'rfc3986',
    'sniffio',
    'solana',
    'solders',
    'sumtypes',
    'toml',
    'toolz',
    'types-cachetools',
    'typing_extensions',
    'urllib3',
    'websockets',
    'zstandard'
    ],
    keywords=['python', 'solana', 'jupiter', 'dex', 'trading', 'sdk'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11.4",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)