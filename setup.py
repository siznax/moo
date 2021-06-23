from setuptools import setup, find_packages

setup(
    name='Moo',
    author='Steve Sisney',
    author_email='steve@siznax.net',
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-executor',
        'mutagen',
    ],
    version='0.4'
)
