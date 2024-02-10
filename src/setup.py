from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.2.0'
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
    license=('LICENSE.txt'),
    install_requires=[
    'base58',
    'solders',
    'solana',
    'httpx',
    'anchorpy',
    ],
    keywords=['python', 'solana', 'jupiter', 'dex', 'trading', 'sdk'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)