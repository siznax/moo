from setuptools import setup, find_packages

setup(
    name='Moo',
    author='Steve Sisney',
    author_email='steve@siznax.net',
    packages=find_packages(),
    install_requires=['flask', 'mutagen', 'unidecode'],
    version='0.2'
)
